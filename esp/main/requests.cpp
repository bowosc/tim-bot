#include <Arduino.h>
#include "requests.h"

void handleOn() {
    // we don't need to declare pinMode bc we did it in setup.
    pinMode(2, OUTPUT);
    digitalWrite(2, HIGH);
    server.send(200, "text/plain", "ON");
    Serial.print("Someone used ON\n");
}

void handleOff() {
    digitalWrite(2, LOW);
    server.send(200, "text/plain", "OFF");
    Serial.print("Someone used OFF\n");
}
