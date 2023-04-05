#include <Wire.h>
#include "VL53L0X.h"

#define XSHUT_pin6 9
#define XSHUT_pin5 8
#define XSHUT_pin4 7
#define XSHUT_pin3 4
#define XSHUT_pin2 3
#define XSHUT_pin1 2

#define AIR_PUMP_1_SELECT  5
#define AIR_PUMP_2_SELECT  10
#define AIR_PUMP_3_SELECT  11
#define AIR_PUMP_INFLATE   12
#define AIR_PUMP_DEFLATE   13

#define Sensor2_newAddress 42
#define Sensor3_newAddress 43
#define Sensor4_newAddress 44
#define Sensor5_newAddress 45
#define Sensor6_newAddress 46

byte incomingByte = 0;
byte incomingBytes = 0;
byte flag = false;
uint32_t timeout = 500;
unsigned long startTime = millis();;

VL53L0X Sensor1;
VL53L0X Sensor2;
VL53L0X Sensor3;
VL53L0X Sensor4;
VL53L0X Sensor5;
VL53L0X Sensor6;

void setup()
{ /*WARNING*/
  //Shutdown pins of VL53L0X ACTIVE-LOW-ONLY NO TOLERANT TO 5V will fry them
  pinMode(XSHUT_pin1, OUTPUT);
  pinMode(XSHUT_pin2, OUTPUT);
  pinMode(XSHUT_pin3, OUTPUT);

  // DEFINE OUTPUT PIN FOR AIR PUMP
  pinMode(AIR_PUMP_1_SELECT, OUTPUT);
  pinMode(AIR_PUMP_2_SELECT, OUTPUT);
  pinMode(AIR_PUMP_3_SELECT, OUTPUT);
  pinMode(AIR_PUMP_INFLATE, OUTPUT);
  pinMode(AIR_PUMP_DEFLATE, OUTPUT);

  Serial.begin(9600);
  Serial.println("WORKING");

  Wire.begin();
  //Change address of sensor and power up next one

  Sensor6.setAddress(Sensor6_newAddress);
  pinMode(XSHUT_pin5, INPUT);
  delay(10); //For power-up procedure t-boot max 1.2ms "Datasheet: 2.9 Power sequence"
  Sensor5.setAddress(Sensor5_newAddress);
  pinMode(XSHUT_pin4, INPUT);
  delay(10);
  Sensor4.setAddress(Sensor4_newAddress);
  pinMode(XSHUT_pin3, INPUT);
  delay(10);
  Sensor3.setAddress(Sensor3_newAddress);
  pinMode(XSHUT_pin2, INPUT);
  delay(10);
  Sensor2.setAddress(Sensor2_newAddress);
  pinMode(XSHUT_pin1, INPUT);
  delay(10);

  Sensor1.init();
  Sensor2.init();
  Sensor3.init();

  Sensor1.setTimeout(500);
  Sensor2.setTimeout(500);
  Sensor3.setTimeout(500);

  // Start continuous back-to-back mode (take readings as
  // fast as possible).  To use continuous timed mode
  // instead, provide a desired inter-measurement period in
  // ms (e.g. sensor.startContinuous(100)).
  Sensor1.startContinuous();
  Sensor2.startContinuous();
  Sensor3.startContinuous();
}

void loop() {

  if (Serial.available() > 0) {
    // read the incoming byte:
    incomingByte = Serial.read();

    if (incomingByte != B1010) {
      incomingByte = incomingByte - 48;
      incomingBytes = incomingBytes << 1 | incomingByte;
      digitalWrite(AIR_PUMP_1_SELECT, false);
      digitalWrite(AIR_PUMP_2_SELECT, false);
      digitalWrite(AIR_PUMP_3_SELECT, false);
      digitalWrite(AIR_PUMP_INFLATE, false);
      digitalWrite(AIR_PUMP_DEFLATE, false);
      return;
    }

    // say what you got:
    // Serial.print("I received incomingBytes as: ");
    // Serial.println(incomingBytes, BIN);

    if (incomingBytes > B11111) {
      incomingBytes = 0;
      return;
    }

    if (incomingBytes & B10000) {
      digitalWrite(AIR_PUMP_1_SELECT, true);
      // Serial.println("AIR_PUMP_1_SELECT");
    }
    if (incomingBytes & B01000) {
      digitalWrite(AIR_PUMP_2_SELECT, true);
      // Serial.println("AIR_PUMP_2_SELECT");
    }
    if (incomingBytes & B00100) {
      digitalWrite(AIR_PUMP_3_SELECT, true);
      // Serial.println("AIR_PUMP_3_SELECT");
    }
    if (incomingBytes & B00010 && incomingBytes & B00001) {
      digitalWrite(AIR_PUMP_INFLATE, false);
      digitalWrite(AIR_PUMP_DEFLATE, false);
      // Serial.println("AIR_PUMP_ACTION_ERROR");
    }
    else if (incomingBytes & B00010) {
      digitalWrite(AIR_PUMP_INFLATE, true);
      digitalWrite(AIR_PUMP_DEFLATE, false);
      // Serial.println("AIR_PUMP_INFLATE");
    }
    else if (incomingBytes & B00001) {
      digitalWrite(AIR_PUMP_INFLATE, false);
      digitalWrite(AIR_PUMP_DEFLATE, true);
      // Serial.println("AIR_PUMP_DEFLATE");
    }
    else {
      digitalWrite(AIR_PUMP_INFLATE, false);
      digitalWrite(AIR_PUMP_DEFLATE, false);
      // Serial.println("AIR_PUMP_NO_ACTION");
    }

    incomingBytes = 0;
    flag = true;
    startTime = millis();
    // Serial.println();
  }

  if (flag && millis() - startTime >= timeout)
  {
    digitalWrite(AIR_PUMP_1_SELECT, false);
    digitalWrite(AIR_PUMP_2_SELECT, false);
    digitalWrite(AIR_PUMP_3_SELECT, false);
    digitalWrite(AIR_PUMP_INFLATE, false);
    digitalWrite(AIR_PUMP_DEFLATE, false);
    flag = false; // prevent any more digitalwrite low
    // Serial.println("reset after 500 ms");
  }

  Serial.print(Sensor1.readRangeContinuousMillimeters());
  Serial.print(',');
  Serial.print(Sensor2.readRangeContinuousMillimeters());
  Serial.print(',');
  Serial.println(Sensor3.readRangeContinuousMillimeters());


}
