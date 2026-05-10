#include <LiquidCrystal.h>
#include <Arduino.h>

// RS, E, D4, D5, D6, D7 (change pins to match your wiring)
// LiquidCrystal lcd(
//   16,  // RS
//   17,  // E
//   18,  // D4
//   19,  // D5
//   20,  // D6
//   47   // D7
// );
LiquidCrystal lcd(
  10,  // RS
  11,  // E
  12,  // D4
  13,  // D5
  14,  // D6
  21   // D7
);


int ENAR = 16;
int ENAL = 17;
int IN1 = 18;
int IN2 = 19;
int IN3 = 20;
int IN4 = 47;

int speedval = 255;
// 5x8 full block: each row uses all 5 pixels (LSBs)
byte eyesL[8] = {
  0b11111,
  0b10011,
  0b10011,
  0b10011,
  0b10011,
  0b10011,
  0b00011,
  0b11111
};


byte eyesR[8] = {
  0b11111,
  0b11001,
  0b11001,
  0b11001,
  0b11001,
  0b11001,
  0b11001,
  0b11111
};


byte mouth[8] = {
  0b00000,
  0b00000,
  0b11111,
  0b11111,
  0b11111,
  0b00000,
  0b00000,
  0b00000
};

byte eyesC[8] = {
  0b00000,
  0b00000,
  0b01110,
  0b11111,
  0b00000,
  0b00000,
  0b00000,
  0b00000
};


void setup() {
  Serial.begin(9600);
  delay(1000);
  Serial.println("Began setup.");
  lcd.begin(16, 2);
  
  pinMode(ENAR, OUTPUT);
  pinMode(ENAL, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  Serial.println("Finished setup. fr");
}

void forward() {
  // digitalWrite(ENAR, HIGH);
  // digitalWrite(ENAL, HIGH);

  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);

  analogWrite(ENAR, speedval);
  analogWrite(ENAL, speedval);
}

void motors_off() {
  digitalWrite(ENAR, LOW);
  digitalWrite(ENAL, LOW);

  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void loop() {
  //Serial.println("Higheee");
  Serial.println("Moving forward.");
  forward();

  delay(2000);
  // motors_off();
  lcd.clear();
  lcd.print("Hello");
  Serial.println("Showing Hello.");

  delay(2000);
  lcd.clear();
  // lcd.createChar(0, eyesL);
  // lcd.createChar(1, mouth);
  // lcd.createChar(2, eyesR);
  // lcd.createChar(3, eyesC);
  lcd.print("Not hello.");
  
  Serial.println("Showing not Hello.");

}