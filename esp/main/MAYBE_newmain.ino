#include <Arduino.h>

#include <WiFi.h>
#include <WebServer.h>

#include "requests.h"

#include "camera.h"


// todo
// convert main to newmain
// set up actual interface for handling all (useful) instructions from the pi
// then, after that, figure out what tools the ai will actually use. 



unsigned long last_cmd_ms = 0;
const unsigned long TIMEOUT_MS = 300;

void setup() {
  Serial.begin(115200);
}

void loop() {
  // Safety timeout
  if (millis() - last_cmd_ms > TIMEOUT_MS) {
    stopMotors();
  }

  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    last_cmd_ms = millis();
    handleCommand(line);
  }
}

void handleCommand(const String& line) {
  // Example: Forward 0.2 0.1
  float v, w;
  if (sscanf(line.c_str(), "Forward %f %f", &v, &w) == 2) {
    setVelocity(v, w);
    Serial.println("OK");
  }
}

void LED_on() {
    // turn led on
}

void LED_off() {
    // turn led off
}

void setVelocity(float v, float w) {
  // convert v,w -> wheel speeds
  // apply PID / motor driver here
}

void stopMotors() {
  // immediately disable motor outputs
}
