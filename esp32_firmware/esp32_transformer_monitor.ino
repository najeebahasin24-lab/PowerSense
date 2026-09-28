/*
 * ==============================================================================
 * Project: AI-Based Smart Transformer Health Monitoring System
 * Target Board: ESP32 Dev Module (30-pin / 38-pin)
 * Description: Real-time sensor data acquisition & wireless transmission to
 *              the AI/ML Cloud / Local FastAPI Backend Server.
 *
 * Sensors Connected:
 *  1. Temperature Sensor (LM35 / DS18B20) -> Analog Pin GPIO 34 (ADC1_CH6)
 *  2. Secondary Current Sensor (ACS712-05A/20A) -> Analog Pin GPIO 35 (ADC1_CH7)
 *  3. AC Voltage Potential Sensor (ZMPT101B) -> Analog Pin GPIO 32 (ADC1_CH4)
 *  4. Dielectric Oil Level Sensor (Ultrasonic HC-SR04 or Float) -> Pins GPIO 5 (Trig) & 18 (Echo)
 *
 * Can also be tested directly in the WOKWI online simulator:
 * https://wokwi.com/ (Select ESP32, Connect to Wokwi-GUEST Wi-Fi)
 * ==============================================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h> // Recommended ArduinoJson library v6 or v7

// --------------------------------------------------------------------------
// Wi-Fi Credentials (Change to your mobile hotspot or Wi-Fi router)
// For Wokwi Online Simulator: SSID="Wokwi-GUEST", Password=""
// --------------------------------------------------------------------------
const char* WIFI_SSID     = "Transformer_WiFi"; 
const char* WIFI_PASSWORD = "Password123";

// --------------------------------------------------------------------------
// Backend Server Configuration
// Replace with your laptop's local IP address (e.g., http://192.168.1.15:8000/api/telemetry)
// If running locally, check IP using 'ipconfig' in command prompt.
// --------------------------------------------------------------------------
const char* SERVER_URL = "http://192.168.1.50:8000/api/telemetry";
const char* TRANSFORMER_ID = "TR-001";

// Pin Assignments
const int PIN_TEMP_LM35     = 34; // ADC1 CH6
const int PIN_CURRENT_ACS   = 35; // ADC1 CH7
const int PIN_VOLTAGE_ZMPT  = 32; // ADC1 CH4
const int PIN_OIL_TRIG      = 5;  // Ultrasonic Trigger
const int PIN_OIL_ECHO      = 18; // Ultrasonic Echo

// Calibration Constants
const float ADC_VREF = 3.3;             // ESP32 ADC Reference Voltage (3.3V)
const int   ADC_RESOLUTION = 4095;      // 12-bit ADC (0 - 4095)
const float ACS712_SENSITIVITY = 0.185; // 185 mV/A for 5A module (0.100 for 20A, 0.066 for 30A)
const float OIL_TANK_DEPTH_CM = 20.0;   // Height of the mini transformer oil reservoir

// Non-blocking sampling interval
unsigned long lastSendTime = 0;
const unsigned long SEND_INTERVAL_MS = 2000; // Send telemetry every 2 seconds

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n=======================================================");
  Serial.println(" AI-Based Smart Transformer Health Monitoring System ");
  Serial.println(" ESP32 Telemetry Transmitter Initializing...          ");
  Serial.println("=======================================================");

  pinMode(PIN_TEMP_LM35, INPUT);
  pinMode(PIN_CURRENT_ACS, INPUT);
  pinMode(PIN_VOLTAGE_ZMPT, INPUT);
  pinMode(PIN_OIL_TRIG, OUTPUT);
  pinMode(PIN_OIL_ECHO, INPUT);

  // Set ADC attenuation to 11dB for full 0 - 3.3V range
  analogSetAttenuation(ADC_11db);

  connectToWiFi();
}

void loop() {
  // Reconnect Wi-Fi if lost
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
  }

  // Periodic sensor acquisition & cloud transmission
  if (millis() - lastSendTime >= SEND_INTERVAL_MS) {
    lastSendTime = millis();

    // 1. Read Physical Sensors
    float temperature = readTemperature();
    float current     = readCurrentRMS();
    float voltage     = readVoltageRMS();
    float oilLevel    = readOilLevelPercentage();

    Serial.printf("\n[SENSORS] Temp: %.2f °C | Oil: %.2f %% | Volt: %.2f V | Curr: %.2f A\n",
                  temperature, oilLevel, voltage, current);

    // 2. Transmit to Backend
    sendTelemetryToServer(temperature, oilLevel, voltage, current);
  }
}

// --------------------------------------------------------------------------
// Wi-Fi Connection Helper
// --------------------------------------------------------------------------
void connectToWiFi() {
  Serial.printf("Connecting to Wi-Fi SSID: %s ", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[Wi-Fi] Connected successfully!");
    Serial.print("[Wi-Fi] ESP32 IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[Wi-Fi] Connection timed out. Retrying in next loop...");
  }
}

// --------------------------------------------------------------------------
// Sensor Reading Functions
// --------------------------------------------------------------------------

// 1. LM35 Temperature Sensor (10mV per °C)
float readTemperature() {
  long sum = 0;
  for (int i = 0; i < 20; i++) {
    sum += analogRead(PIN_TEMP_LM35);
    delay(2);
  }
  float avgRaw = (float)sum / 20.0;
  float voltageMilliVolts = (avgRaw / (float)ADC_RESOLUTION) * (ADC_VREF * 1000.0);
  float temperatureC = voltageMilliVolts / 10.0; // LM35: 10 mV / °C
  
  // Boundary checks for mini transformer
  if (temperatureC < 0) temperatureC = 25.0;
  return temperatureC;
}

// 2. ACS712 Secondary Current Sensor (RMS sampling over 50Hz AC cycle)
float readCurrentRMS() {
  long sumSq = 0;
  int samples = 200;
  for (int i = 0; i < samples; i++) {
    int raw = analogRead(PIN_CURRENT_ACS);
    float v = (raw / (float)ADC_RESOLUTION) * ADC_VREF;
    float offset = 1.65; // Nominal quiescent voltage at 3.3V supply (or 2.5V for 5V with divider)
    float instantaneousCurrent = (v - offset) / ACS712_SENSITIVITY;
    sumSq += (instantaneousCurrent * instantaneousCurrent);
    delayMicroseconds(100);
  }
  float rmsCurrent = sqrt(sumSq / samples);
  if (rmsCurrent < 0.05) rmsCurrent = 0.0; // Noise suppression
  return rmsCurrent;
}

// 3. ZMPT101B AC Voltage Sensor
float readVoltageRMS() {
  long sumSq = 0;
  int samples = 200;
  for (int i = 0; i < samples; i++) {
    int raw = analogRead(PIN_VOLTAGE_ZMPT);
    float v = (raw / (float)ADC_RESOLUTION) * ADC_VREF;
    float offset = 1.65; // Mid-rail reference
    float acInstantaneous = (v - offset);
    sumSq += (acInstantaneous * acInstantaneous);
    delayMicroseconds(100);
  }
  float rmsVoltsSensor = sqrt(sumSq / samples);
  // Calibration multiplier for 230V mains or step-down secondary
  float calibrationFactor = 230.0 / 0.707; // Scale to match nominal AC line
  float acLineVoltage = rmsVoltsSensor * calibrationFactor;
  if (acLineVoltage < 20.0) acLineVoltage = 0.0;
  return acLineVoltage;
}

// 4. Ultrasonic HC-SR04 Oil Level Sensor
float readOilLevelPercentage() {
  digitalWrite(PIN_OIL_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_OIL_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_OIL_TRIG, LOW);

  long duration = pulseIn(PIN_OIL_ECHO, HIGH, 30000); // 30ms timeout
  if (duration == 0) return 85.0; // Fallback default if sensor echo disconnected

  // Speed of sound = 0.0343 cm/us
  float distanceCm = (duration * 0.0343) / 2.0;
  
  // Calculate oil percentage: level = (TankDepth - Distance) / TankDepth * 100
  float oilLevelCm = OIL_TANK_DEPTH_CM - distanceCm;
  float percentage = (oilLevelCm / OIL_TANK_DEPTH_CM) * 100.0;
  
  if (percentage > 100.0) percentage = 100.0;
  if (percentage < 0.0) percentage = 0.0;
  return percentage;
}

// --------------------------------------------------------------------------
// HTTP JSON Telemetry Transmission
// --------------------------------------------------------------------------
void sendTelemetryToServer(float temp, float oil, float volt, float curr) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[HTTP] Cannot send telemetry: Wi-Fi not connected.");
    return;
  }

  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  // Construct JSON Payload
  StaticJsonDocument<256> doc;
  doc["transformer_id"] = TRANSFORMER_ID;
  doc["temperature"]    = temp;
  doc["oil_level"]      = oil;
  doc["voltage"]        = volt;
  doc["current"]        = curr;

  String jsonPayload;
  serializeJson(doc, jsonPayload);

  Serial.print("[HTTP POST] Transmitting payload: ");
  Serial.println(jsonPayload);

  int httpCode = http.POST(jsonPayload);

  if (httpCode > 0) {
    String response = http.getString();
    Serial.printf("[HTTP Response] Code %d: %s\n", httpCode, response.c_str());
  } else {
    Serial.printf("[HTTP Error] POST failed, error: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
}
