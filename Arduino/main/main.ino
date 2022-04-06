// Test for minimum program size.
// Edit AVRI2C_FASTMODE in SSD1306Ascii.h to change the default I2C frequency.

#include "SSD1306Ascii.h"
#include "SSD1306AsciiAvrI2c.h"

// 0X3C+SA0 - 0x3C or 0x3D
#define I2C_ADDRESS 0x3C

//Hardware Defines

const int lockButton = 2;
const int lock = 5;


String password[4] = {"5","5","5","5"};
int userPassword[4];
bool unlock = false;
int passwordCounter = -1;

//Hardware variables
int lockButtonState = 0;
String incomingByte = "";
String incoming = "";
int start = 0;

SSD1306AsciiAvrI2c oled;


//Function prototyping
void waitForUser();
//------------------------------------------------------------------------------
void setup() {

//serial port setup

  Serial.begin(9600);

//Screen setup 

  oled.begin(&Adafruit128x64, I2C_ADDRESS);
  oled.setFont(CalLite24);
  oled.clear();
  oled.print("Ready!");
  
  ///////////////////////////////////////////////////////////////////////

//Hardware setup
   pinMode(lockButton, INPUT_PULLUP);
   pinMode(lock, OUTPUT);
   
}
//------------------------------------------------------------------------------
void loop() {

  lockButtonState = !digitalRead(lockButton);

  //lock button
  if(lockButtonState == 1)
  {
    digitalWrite(lock, LOW);
    passwordCounter = -1;
    oled.clear();
    oled.print("Locked!");
  }

  //reading the password from the computer and checking if it has been told to start
  if(Serial.available() > 0)
  {
    String incoming = Serial.readStringUntil('\n');
    if(incoming == "password")
    {
      oled.clear();
      for(int i = 0; i < 4; i++)
      {
        if(Serial.available() > 0)
        {
          String passwordPart = Serial.readStringUntil('\n');
          char k = Serial.read();
          delay(500);
          password[i] = passwordPart;
        }
      }
    }
    if(incoming == "start")
    {
      oled.clear();
      start = 1;
    }
  }
   
  //when the arduino starts, it loops through this to display information on the LCD
  if(start){
    passwordCounter = 0;
    for(int i = 0; i < 4; i++)
    {
      oled.clear();
      oled.write("prepare \n next");
      delay(2000);
      oled.clear();
      oled.write("3");
      delay(1000);
      oled.clear();
      oled.write("2");
      delay(1000);
      oled.clear();
      oled.write("1");
      delay(1000);
      oled.clear();
      oled.write("snap!");
      Serial.write('1');
      delay(2000);
      //password digit checking
      if (Serial.available() > 0 )
      {
        incomingByte = Serial.readStringUntil('\n');
        char k = Serial.read();
        //oled.clear();
        //oled.print("I:" + incomingByte + " P:" + password[i]);
        if(password[i] == incomingByte)
          passwordCounter++;
        delay(1000); 
      }
    }
  }
  start = 0;

  //unlocks if password is correct.
  if(passwordCounter == 4)
  {
    oled.clear();
    oled.print("Unlocked!");
    digitalWrite(lock, HIGH);
    passwordCounter = -1;
  }
  //displays incorrect if the password is incorrect.
  else if(passwordCounter > -1 && passwordCounter < 4)
  {
    oled.clear();
    oled.print("Incorrect!");
    passwordCounter = -1;
  }
}

//connect to lock through mofset,
