#include <WiFi.h>
#include <WebServer.h>

#include "requests.h"

// #include "camera.h"


WebServer server(80); // init webserver object


// To be used in case of no good wifi network.
bool offgrid = false;


void connectToNetwork() {

  Serial.println("Connecting to Wi-Fi...");
  //WiFi.begin("fishnet", "fishnet1!");
  WiFi.begin("bingus", "raspeyes");
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
}


void hostOwnNetwork() {
  WiFi.softAP("TimBot", "password"); // SSID + password
  Serial.print("AP IP address: ");
  Serial.println(WiFi.softAPIP()); // usually gonna be 192.168.4.1
}

void setup() {

  // Start er up
  Serial.begin(115200); // baud rate

  pinMode(2, OUTPUT); // get them pins up
  pinMode(motor1pin1, OUTPUT);
  pinMode(motor1pin2, OUTPUT);
  pinMode(motor2pin1, OUTPUT);
  pinMode(motor2pin2, OUTPUT);

  // initCamera(); // guess what this does

  

  if (offgrid == true) {

    // Host own network

    hostOwnNetwork();

  } else {

    // Connect to preset network

    connectToNetwork();

  };
  


  // define HTTP endpoints 
  server.on("/led_on", handleLEDOn);
  server.on("/led_off", handleLEDOff);
  server.on("/turn_right", handleTurnRight);
  server.on("/turn_left", handleTurnLeft);
  server.on("/move_forward", handleMoveForward);
  server.on("/move_backward", handleMoveBackward);
  server.on("/switch_to_existing_network", connectToNetwork);
  server.on("/switch_to_local_network", hostOwnNetwork);


  // server.on("/capture", HTTP_GET, []() {
  //   handle_capture(server);
  // });

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

  // delay(3000);
  // handleMoveForward();
  // // delay(2000);
  // // handleMoveBackward();
  // // delay(2000);
  // handleTurnRight();
  // // delay(2000);
  // handleTurnLeft();

  server.handleClient(); // yeah. i got this
}
