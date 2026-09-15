#include <Arduino.h>

// Vertical Axis (Distance: 55 cm)
// Sensor 1 (Top)
const int TRIG_PIN_1 = 9;
const int ECHO_PIN_1 = 10;

// Sensor 2 (Bottom)
const int TRIG_PIN_2 = 7;
const int ECHO_PIN_2 = 8;

// Horizontal Axis (Distance: 49 cm)
// Sensor 3 (Left)
const int TRIG_PIN_3 = 3;
const int ECHO_PIN_3 = 4;

// Sensor 4 (Right)
const int TRIG_PIN_4 = 5;
const int ECHO_PIN_4 = 6;

float readDistance(int trigPin, int echoPin) {
  // Clear trigger pin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  // Send 10µs pulse to trigger
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Measure echo pulse (8000µs timeout: covers up to ~137cm; plenty for ~50-55cm rig with burst headroom)
  unsigned long duration = pulseIn(echoPin, HIGH, 8000);

  if (duration == 0) {
    return -1.0; // Out of range or no echo
  }

  // Speed of sound: 343 m/s = 0.0343 cm/µs
  return (duration * 0.0343) / 2.0;
}

void setup() {
  Serial.begin(115200);

  // Vertical sensors
  pinMode(TRIG_PIN_1, OUTPUT);
  pinMode(ECHO_PIN_1, INPUT);
  pinMode(TRIG_PIN_2, OUTPUT);
  pinMode(ECHO_PIN_2, INPUT);

  // Horizontal sensors
  pinMode(TRIG_PIN_3, OUTPUT);
  pinMode(ECHO_PIN_3, INPUT);
  pinMode(TRIG_PIN_4, OUTPUT);
  pinMode(ECHO_PIN_4, INPUT);
}

void loop() {
  // Sensor 1 (Top)
  float dist1 = readDistance(TRIG_PIN_1, ECHO_PIN_1);
  delay(18);

  // Sensor 2 (Bottom)
  float dist2 = readDistance(TRIG_PIN_2, ECHO_PIN_2);
  delay(18);

  // Sensor 3 (Left)
  float dist3 = readDistance(TRIG_PIN_3, ECHO_PIN_3);
  delay(18);

  // Sensor 4 (Right)
  float dist4 = readDistance(TRIG_PIN_4, ECHO_PIN_4);

  // Print all 4 readings tab-separated: dist1 \t dist2 \t dist3 \t dist4
  Serial.print(dist1, 1);
  Serial.print('\t');
  Serial.print(dist2, 1);
  Serial.print('\t');
  Serial.print(dist3, 1);
  Serial.print('\t');
  Serial.println(dist4, 1);

  // Settle delay before next sampling frame
  delay(18);
}