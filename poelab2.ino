#include <Servo.h>

Servo tilt;
Servo pan; 
byte sensor_pin = A0;

void setup() {
  Serial.begin(9600);
  Serial.println("Set up");
  tilt.attach(9);
  pan.attach(10);
  middle_servos();
}

void loop() {
  for(int tilt_pos = 60; tilt_pos < 120; tilt_pos += 2) {
    tilt.write(tilt_pos);
    delay(100);
    for(int pan_pos = 20; pan_pos < 160; pan_pos += 5) {
      pan.write(pan_pos);
      delay(100);
      int sensorValue = analogRead(sensor_pin);
      Serial.print(tilt_pos);
      Serial.print(',');
      Serial.print(pan_pos);
      Serial.print(',');
      Serial.println(sensorValue);
    }
  }  
}

void middle_servos() {
   tilt.write(90);
   pan.write(90);
}
