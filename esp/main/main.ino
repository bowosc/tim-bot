#include <WiFi.h>
#include <WebServer.h>

#include "requests.h"

#include "camera.h"


WebServer server(80); // init webserver object


// To be used in case of no good wifi network.
bool offgrid = false;


void setup() {

  // Start er up
  Serial.begin(115200); // baud rate
  pinMode(2, OUTPUT); // get that pin up
  initCamera(); // guess what this does

  if (offgrid == true) {

    // Host own network

    WiFi.softAP("TimBot", "password"); // SSID + password
    Serial.print("AP IP address: ");
    Serial.println(WiFi.softAPIP()); // usually gonna be 192.168.4.1

  } else {

    // Connect to preset network

    Serial.println("Connecting to Wi-Fi...");
    //WiFi.begin("fishnet", "fishnet1!");
    WiFi.begin("bingus", "raspeyes")
    WiFi.mode(WIFI_STA); // we no want dropped packets
    WiFi.setSleep(false);

    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
    Serial.println(); // line break for pretty printing

    Serial.println("Wi-Fi connected!\n");

    Serial.print("ESP32 IP address: ");
    Serial.println(WiFi.localIP());
    Serial.println(); // line break for pretty printing

  };
  


  // define HTTP endpoints 
  server.on("/on", handleOn);
  server.on("/off", handleOff);
  server.on("/turn", handleTurn);
  server.on("/moveforward", handleMoveForward);

  server.on("/capture", HTTP_GET, []() {
    handle_capture(server);
  });

  server.begin();


  // yeah we awake. flicka flicka
  digitalWrite(2, HIGH);
  delay(200);
  digitalWrite(2, LOW);
  delay(200);
  digitalWrite(2, HIGH);
  delay(200);
  digitalWrite(2, LOW);
  delay(200);
  digitalWrite(2, HIGH);
  delay(200);
  digitalWrite(2, LOW);
  delay(200);
}

void loop() {
  server.handleClient(); // yeah. i got this
}
