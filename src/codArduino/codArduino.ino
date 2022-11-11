#include <LiquidCrystal_I2C.h> // Libreria para el manejo de la pantalla LCD.
#include <Keypad.h> // Libreria para el manejo del teclado.
// Permite trabajar con el hardware directamente del MODULO-GPS
#include<SoftwareSerial.h>
// Permite interpretar los datos enviados por el GPS(los datos son enviados en codigo NMEA -> National Marine Electronics Asociation)
#include<TinyGPS.h>// TYNYGPS
// VARIABLES
char LetterKey; // Almacena la tecla presionada en el keypad
int estado = 0;  //0:cerrado 1:abierto.
char clave[5]; // Almacena la contraseña.
char clave_maestra[5] = "1234"; // Almacena la contraseña a comparar.
int indice; // indice del array
int fallos = 0;
int pinLed = 13;
float flat, flon;

// COMPONENTES:
//____________________PANTALLA LCD____________________
LiquidCrystal_I2C lcd(0x27,16,2); // Creamos un objeto para controlar los parametros (INFO) que se le envia al LED

//____________________KEYPAD____________________
const byte ROWS = 4;
const byte COLUMNS = 4;
char keys[ROWS][COLUMNS] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};

byte rowsPins[ROWS] = {2,3,4,5};
byte columnsPins[COLUMNS] = {6,7,8,9};

Keypad teclado = Keypad(makeKeymap(keys),rowsPins,columnsPins,ROWS,COLUMNS);

// ____________________MODULO GPS____________________
// DECLARAMOS UN OBJETO DE TIPO SOFTWARE-SERIAL
SoftwareSerial ss(12,11); // TX/RX
// DECLARAMOS UN OBJETO DE TIPO TINY-GPS
TinyGPS gps;

void setup() {
  // PANTALLA LCD
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("CLAVE:"); 
  limpiar();
  // MODULO GPS
  Serial.begin(115200);
  // LE DECIMOS AL MODULO GPS QUE ME ENVIE LOS DATOS A LA VELOCIDAD DE 9600 baudios
  ss.begin(9600);
  // LED
  pinMode(pinLed,OUTPUT);
}

void loop() {
  LetterKey = teclado.getKey();
  if (LetterKey){
    if (strstr('#',LetterKey)){
      limpiar();
      indice = 0;
    }else{
      clave[indice] = LetterKey;
      indice++;
      lcd.print(LetterKey);
    }
  }

  if (indice == 4){
    if(!strcmp(clave,clave_maestra)){
      abrir();
    }else{
       error();
    }
     indice = 0;
  }

  if(ss.available()>0){
    // VERIFICA LA CONVERCIÓN DE INFORMACIÓN DE NMEA A COORDENADAS POLARES LEIBLES(LAT,LNG)
    if(gps.encode(ss.read())){
      // VARIABLES (LAT,LON)
      gps.f_get_position(&flat, &flon);
    }
  }
}

// ______Funcion limpiar______
void limpiar(){
  lcd.setCursor(0,0);
  lcd.print("CLAVE:          ");
  lcd.setCursor(9,0);
}

// ______Funcion abrir______
void abrir(){
  if (estado == 0){
    estado = 1;
    lcd.setCursor(0,1);
    lcd.print("Abierto         ");
    fallos = 0;
  }else{
    estado = 0;
    lcd.setCursor(0,1);
    lcd.print("Cerrado         ");
  }
  limpiar();
  digitalWrite(pinLed,LOW);
}

// ______Funcion error______
void error(){
  if (estado == 0){
    fallos += 1;
    if (fallos == 3){
      localizar();
      fallos = 0;
    }
  }
  
  lcd.setCursor(0,1);
  lcd.print("ERROR DE CLAVE  ");
  limpiar();
}

// ______Funcion localizar______
void localizar(){
  digitalWrite(pinLed,HIGH);
  Serial.println(String(flat,6) + "," + String(flon,6));
}
