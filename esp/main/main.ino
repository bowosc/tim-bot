#include <WiFi.h>
#include <WebServer.h>

#include "requests.h"

WebServer server(80);

void setup() {
  Serial.begin(115200);
  pinMode(2, OUTPUT);

  //WiFi.softAP("TimBot", "password");  // SSID + password
  //Serial.print("AP IP address: ");
  //Serial.println(WiFi.softAPIP());        // usually 192.168.4.1

  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin("fishnet", "fishnet1!");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("Wi-Fi connected!");

  Serial.print("ESP32 IP address: ");
  Serial.println(WiFi.localIP());


  server.on("/on", handleOn);
  server.on("/off", handleOff);
  server.begin();

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
  server.handleClient();
}
