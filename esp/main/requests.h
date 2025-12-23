#pragma once

#include <WebServer.h>

// This tells other files “there is a WebServer called server somewhere”
extern WebServer server;

void handleOn();

void handleOff();

void handleCameraSnapshot();

void handleMoveForward();

void handleTurn();