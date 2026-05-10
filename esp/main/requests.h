#pragma once

#include <WebServer.h>

// This tells other files “there is a WebServer called server somewhere”
extern WebServer server;


extern int motor2pin1;
extern int motor2pin2;

extern int motor1pin1;
extern int motor1pin2;

void handleLEDOn();

void handleLEDOff();

void handleMoveForward();

void handleMoveBackward();

void handleTurnLeft();

void handleTurnRight();
