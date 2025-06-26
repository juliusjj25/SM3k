#include <Arduino.h>
#include <SD.h>
#include <ArduinoJson.h>

bool loggingStarted = false;
File logFile;
String logFilename = "/default.csv";

void setup() {
  Serial.begin(115200);
  while (!Serial);
  
  if (!SD.begin()) {
    Serial.println("SD Init failed!");
    return;
  }

  Serial.println("ESP Ready. Awaiting start command...");
}

void loop() {
  if (!loggingStarted && Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.length() > 0) {
      StaticJsonDocument<128> doc;
      DeserializationError err = deserializeJson(doc, input);
      if (!err) {
        if (doc["command"] == "start") {
          String fn = doc["filename"] | "log.csv";
          logFilename = "/" + fn;

          logFile = SD.open(logFilename, FILE_WRITE);
          if (logFile) {
            loggingStarted = true;
            Serial.println("Logging started: " + logFilename);
          } else {
            Serial.println("Failed to open file.");
          }
        }
      } else {
        Serial.println("Invalid JSON input.");
      }
    }
  }

  if (loggingStarted) {
    StaticJsonDocument<128> doc;
    doc["chamber"] = 225.3;
    doc["meat1"] = 145.6;
    doc["meat2"] = nullptr;
    doc["meat3"] = nullptr;
    doc["meat4"] = nullptr;

    String jsonStr;
    serializeJson(doc, jsonStr);

    logFile.println(jsonStr);
    Serial.println(jsonStr);
    delay(1000);
  }
}
