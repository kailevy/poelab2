#include <Servo.h>

Servo tilt;
Servo pan; 
byte sensor_pin = A0;

// range of angles for servos
int pan_max = 120;
int pan_min = 60;
int tilt_max = 140;
int tilt_min = 60;
int pan_step = 1;
int tilt_step = 1; // should be odd!

void setup() {
  Serial.begin(9600);
  tilt.attach(9);
  pan.attach(10);
  middle_servos();
  while (wait_for_start() != 1){
    delay(50);
  }
  serialFlush();
}

void loop() {
  for(int tilt_pos = tilt_min; tilt_pos <= tilt_max; tilt_pos += tilt_step) {
    tilt.write(tilt_pos);
    byte odd = tilt_pos % 2;
    // goes from low pan to high pan on odd tilt angles
    if (odd) {
      for(int pan_pos = pan_min; pan_pos <= pan_max; pan_pos += pan_step) {
        pan_and_write(tilt_pos,pan_pos);
      }
    }
    // otherwise high pan to low pan
    else {
      for(int pan_pos = pan_max; pan_pos >= pan_min; pan_pos -= pan_step) {
        pan_and_write(tilt_pos,pan_pos);
      }
    }
    //signals that it has finished one sweep and then waits for python
    while (wait_for_start() != 1){
      delay(50);
      Serial.println('a');
    }
    serialFlush();
  }
  //sends signal to python that it is finished and stalls
  Serial.println('b');
  while(wait_for_start() != 1){
    delay(50);
  }
  serialFlush();
}

void pan_and_write(int tilt_pos,int pan_pos) {
  // pans and then records three readings
  pan.write(pan_pos);
  delay(50);
  int sensorValue1 = analogRead(sensor_pin);
  delay(20);
  int sensorValue2 = analogRead(sensor_pin);
  delay(20);
  int sensorValue3 = analogRead(sensor_pin);
  Serial.print(tilt_pos);
  Serial.print(',');
  Serial.print(pan_pos);
  Serial.print(',');
  Serial.print(sensorValue1);
  Serial.print(',');
  Serial.print(sensorValue2);
  Serial.print(',');
  Serial.println(sensorValue3);
}

void middle_servos() {
  // set servos to neutral positions for calibration
   tilt.write(90);
   pan.write(90);
}

byte wait_for_start() {
  //waits for serial input
   if (Serial.available() > 0) {
     return 1;
   }
   else {
     return 0;
   }
}

void serialFlush() {
  // flushes serial backlog
  while(Serial.available() > 0) {
    char t = Serial.read();
  }
} 
