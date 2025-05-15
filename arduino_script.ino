const int buttonPin = 2;
const int in1 = 8;
const int in2 = 9;
const int ena = 10;

int lastButtonState = HIGH;
bool goingForward = true;

// Time to move 30cm at 5.7mm/s ≈ 53 seconds
// Set to 57 seconds as actuaotor is not very accurate
const unsigned long travelDurationMs = 57000;

void setup() {
  Serial.begin(9600);
  pinMode(buttonPin, INPUT_PULLUP);  // Using internal pull-up
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(ena, OUTPUT);

  // Ensure motor is stopped
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  analogWrite(ena, 0);

  Serial.println("🔘 Ready. Press button to move actuator.");
}

void loop() {
  int currentState = digitalRead(buttonPin);

  if (currentState == LOW && lastButtonState == HIGH) {
    if (goingForward) {
      Serial.println("⬆️ Moving forward 30cm...");
      Serial.println("START");  // Signal Python to start recording (optional)
      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW);
    } else {
      Serial.println("⬇️ Returning (reverse) 30cm...");
      digitalWrite(in1, LOW);
      digitalWrite(in2, HIGH);
    }

    analogWrite(ena, 255);             // Full speed
    delay(travelDurationMs);           // ~53 seconds
    analogWrite(ena, 0);               // Stop motor
    digitalWrite(in1, LOW);
    digitalWrite(in2, LOW);

    Serial.println("🛑 Motion complete.");
    goingForward = !goingForward;      // Toggle direction
  }

  lastButtonState = currentState;
}



// BUTTON PRESS TESTING
// This is a simple button press example to demonstrate the button functionality.

// const int buttonPin = 2;
// int lastButtonState = HIGH;

// void setup() {
//   Serial.begin(9600);
//   pinMode(buttonPin, INPUT_PULLUP);  // Enable internal pull-up resistor
//   Serial.println("🔘 Waiting for button press...");
// }

// void loop() {
//   int currentState = digitalRead(buttonPin);

//   if (currentState == LOW && lastButtonState == HIGH) {
//     Serial.println("✅ Button Pressed");
//     delay(50);  // Simple debounce
//   }

//   lastButtonState = currentState;
// }

// RESET ACTUATOR
// const int in1 = 8;
// const int in2 = 9;
// const int ena = 10;

// void setup() {
//   pinMode(in1, OUTPUT);
//   pinMode(in2, OUTPUT);
//   pinMode(ena, OUTPUT);

//   // Run in reverse (retract)
//   digitalWrite(in1, LOW);
//   digitalWrite(in2, HIGH);
//   analogWrite(ena, 255);
// }

// void loop() {
//   // nothing — let it run continuously
// }
