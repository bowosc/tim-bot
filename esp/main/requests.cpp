#include <Arduino.h>
#include "requests.h"

// int motor2pin1 = 27;
// int motor2pin2 = 14;
// int motor1pin1 = 26;
// int motor1pin2 = 25;
int motor2pin1 = 25; // flpd
int motor2pin2 = 26;
int motor1pin1 = 27; // flpd
int motor1pin2 = 33;

void handleLEDOn() {
    // we don't need to declare pinMode bc we did it in setup.
    // pinMode(2, OUTPUT);
    digitalWrite(2, HIGH);
    server.send(200, "text/plain", "ON");
    Serial.print("Someone used ON\n");
}

void handleLEDOff() {
    digitalWrite(2, LOW);
    server.send(200, "text/plain", "OFF");
    Serial.print("Someone used OFF\n");
}



void handleMoveForward() {
    Serial.println("Moving forward");

    // turn on left motor
    digitalWrite(motor1pin1, LOW);
    digitalWrite(motor1pin2, HIGH);

    // turn on right motor
    digitalWrite(motor2pin1, LOW);
    digitalWrite(motor2pin2, HIGH);

    // go for a second
    delay(1000);

    // turn off left motor
    digitalWrite(motor1pin1, LOW);
    digitalWrite(motor1pin2, LOW);

    // turn off right motor
    digitalWrite(motor2pin1, LOW);
    digitalWrite(motor2pin2, LOW);

    server.send(200, "text/plain", "Moved forward");
}

void handleMoveBackward() {
    Serial.println("Moving backward");

    // turn on left motor
    digitalWrite(motor1pin1, HIGH);
    digitalWrite(motor1pin2, LOW);

    // turn on right motor
    digitalWrite(motor2pin1, HIGH);
    digitalWrite(motor2pin2, LOW);

    // go for a second
    delay(1000);

    // turn off left motor
    digitalWrite(motor1pin1, LOW);
    digitalWrite(motor1pin2, LOW);

    // turn off right motor
    digitalWrite(motor2pin1, LOW);
    digitalWrite(motor2pin2, LOW);

    server.send(200, "text/plain", "Moved backward");
}
void handleTurnRight() {
    Serial.println("Turning Right");

     // turn on left motor
    digitalWrite(motor1pin1, LOW);
    digitalWrite(motor1pin2, HIGH);

    // leave off right motor
    digitalWrite(motor2pin1, LOW);
    digitalWrite(motor2pin2, LOW);

    // go for a half second
    delay(500);

    // turn off left motor
    digitalWrite(motor1pin1, LOW);
    digitalWrite(motor1pin2, LOW);

    // turn off right motor
    digitalWrite(motor2pin1, LOW);
    digitalWrite(motor2pin2, LOW);

    server.send(200, "text/plain", "Turned right");
}

void handleTurnLeft() {
    Serial.println("Turning Left");

     // turn on left motor
    digitalWrite(motor1pin1, LOW);
    digitalWrite(motor1pin2, LOW);

    // leave off right motor
    digitalWrite(motor2pin1, LOW);
    digitalWrite(motor2pin2, HIGH);

    // go for a half second
    delay(500);

    // turn off left motor
    digitalWrite(motor1pin1, LOW);
    digitalWrite(motor1pin2, LOW);

    // turn off right motor
    digitalWrite(motor2pin1, LOW);
    digitalWrite(motor2pin2, LOW);

    server.send(200, "text/plain", "Turned left");
}
