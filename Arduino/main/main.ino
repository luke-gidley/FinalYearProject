// Test for minimum program size.
// Edit AVRI2C_FASTMODE in SSD1306Ascii.h to change the default I2C frequency.

#include "SSD1306Ascii.h"
#include "SSD1306AsciiAvrI2c.h"

// 0X3C+SA0 - 0x3C or 0x3D
#define I2C_ADDRESS 0x3C

//Hardware Defines

const int lockButton = 2;
const int lock = 5;


String password[4] = {"5", "5", "5", "5"};
int userPassword[4];
bool unlock = false;
int passwordCounter = 0;

//Hardware variables
int lockButtonState = 0;
String incomingByte = "";
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
  oled.print("Hello world!");
  
  ///////////////////////////////////////////////////////////////////////

//Hardware setup
   pinMode(lockButton, INPUT_PULLUP);
   pinMode(lock, OUTPUT);
   
}
//------------------------------------------------------------------------------
void loop() {

  lockButtonState = !digitalRead(lockButton);
  
  if(lockButtonState == 1)
  {

    start = 1;
  }

  if(start){
    for(int i = 0; i < 4; i++)
    {
      oled.clear();
      oled.write("prepare next");
      delay(3000);
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
      delay(1000);
      if (Serial.available() > 0 )
      {
        incomingByte = Serial.readString();
        oled.clear();
        oled.print(incomingByte);
        if(password[i] != incomingByte)
          passwordCounter++;
        delay(2000); 
      }
    }
  }
  start = 0;

  if(passwordCounter == 4)
  {
    digitalWrite(lock, HIGH);    
  }
}

//connect to lock through mofset,
