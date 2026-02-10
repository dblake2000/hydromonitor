//##################################################################################################################
//##                                      ELET2415 DATA ACQUISITION SYSTEM CODE                                   ##
//##################################################################################################################

// LIBRARY IMPORTS
#include <rom/rtc.h>
#include <math.h>
#include <ctype.h>

// ADD YOUR IMPORTS HERE
#include <Arduino.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <FastLED.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// DEFINE VARIABLES
#define ARDUINOJSON_USE_DOUBLE 1

// DEFINE THE CONTROL PINS FOR THE DHT22
#define DHTPIN 4
#define DHTTYPE DHT22

// FASTLED CONFIG
#define LED_PIN 5
#define NUM_LEDS 7
CRGB leds[NUM_LEDS];

// -------------------- EDIT THESE (CTRL+F) --------------------
static const char *STUDENT_ID = "620167361";
static const char *PUB_TOPIC = "620167361";
static const char *subtopic[] = {"620167361_sub", "/elet2415"};

static const char *mqtt_server = "www.yanacreations.com";
static uint16_t mqtt_port = 1883;

const char *ssid = "LAB02";
const char *password = "AirCon519";
// ------------------------------------------------------------


WiFiClient espClient;
PubSubClient mqtt(espClient);


TaskHandle_t xMQTT_Connect = NULL;
TaskHandle_t xNTPHandle = NULL;
TaskHandle_t xLOOPHandle = NULL;
TaskHandle_t xUpdateHandle = NULL;
TaskHandle_t xButtonCheckeHandle = NULL;

// FUNCTION DECLARATION
void checkHEAP(const char *Name);
void initMQTT(void);
unsigned long getTimeStamp(void);
void callback(char *topic, byte *payload, unsigned int length);
void initialize(void);
bool publish(const char *topic, const char *payload);
void vButtonCheck(void *pvParameters);
void vUpdate(void *pvParameters);

double convert_Celsius_to_fahrenheit(double c);
double convert_fahrenheit_to_Celsius(double f);
double calcHeatIndex(double Temp, double Humid);

// DHT instance
DHT dht(DHTPIN, DHTTYPE);

// Include your template headers ONCE (after globals exist)
#include "NTP.h"
#include "mqtt.h"

void setup() {
  Serial.begin(115200);
  delay(200);

  dht.begin();

  FastLED.addLeds<WS2812, LED_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(64);
  fill_solid(leds, NUM_LEDS, CRGB::Black);
  FastLED.show();

  initialize(); // starts NTP, WiFi, MQTT tasks, vUpdate task
}

void loop() {
  vTaskDelay(1000 / portTICK_PERIOD_MS);
}

//####################################################################
//#                          UTIL FUNCTIONS                           #
//####################################################################
void vButtonCheck(void *pvParameters) {
  configASSERT(((uint32_t)pvParameters) == 1);
  for (;;) vTaskDelay(200 / portTICK_PERIOD_MS);
}

void vUpdate(void *pvParameters) {
  configASSERT(((uint32_t)pvParameters) == 1);

  for (;;) {
    double h = dht.readHumidity();
    double t = dht.readTemperature(); // Celsius

    if (!isnan(t) && !isnan(h)) {
      JsonDocument doc;
      char message[256];

      doc["id"] = STUDENT_ID;
      doc["timestamp"] = (unsigned long)getTimeStamp();
      doc["temperature"] = t;
      doc["humidity"] = h;
      doc["heatindex"] = calcHeatIndex(t, h);

      serializeJson(doc, message, sizeof(message));
      publish(PUB_TOPIC, message);

      Serial.printf("PUBLISHED %s -> %s\n", PUB_TOPIC, message);
    } else {
      Serial.println("DHT read failed (NaN)");
    }

    vTaskDelay(1000 / portTICK_PERIOD_MS);
  }
}

unsigned long getTimeStamp(void) {
  time_t now;
  time(&now);
  return now;
}

void callback(char *topic, byte *payload, unsigned int length) {
  Serial.printf("\nMessage received : ( topic: %s ) \n", topic);

  char *received = new char[length + 1]{0};
  for (unsigned int i = 0; i < length; i++) received[i] = (char)payload[i];
  Serial.printf("Payload : %s \n", received);

  JsonDocument doc;
  DeserializationError error = deserializeJson(doc, received);
  delete[] received;

  if (error) {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
    return;
  }

  const char *type = doc["type"] | "";

  if (strcmp(type, "controls") == 0) {
    int brightness = doc["brightness"] | 0;
    int nodes = doc["leds"] | 0;
    int r = doc["color"]["r"] | 0;
    int g = doc["color"]["g"] | 0;
    int b = doc["color"]["b"] | 0;

    brightness = constrain(brightness, 0, 255);
    nodes = constrain(nodes, 0, NUM_LEDS);
    r = constrain(r, 0, 255);
    g = constrain(g, 0, 255);
    b = constrain(b, 0, 255);

    FastLED.setBrightness((uint8_t)brightness);

    for (int i = 0; i < NUM_LEDS; i++) {
      leds[i] = (i < nodes) ? CRGB((uint8_t)r, (uint8_t)g, (uint8_t)b)
                            : CRGB::Black;
      FastLED.show();
      vTaskDelay(20 / portTICK_PERIOD_MS);
    }

    Serial.printf("Controls applied: bright=%d nodes=%d rgb=(%d,%d,%d)\n",
                  brightness, nodes, r, g, b);
  }
}

bool publish(const char *topic, const char *payload) {
  bool res = mqtt.publish(topic, payload);
  if (!res) Serial.println("Publish failed");
  return res;
}

//***** util functions *****
double convert_Celsius_to_fahrenheit(double c) {
  return (c * 9.0 / 5.0) + 32.0;
}

double convert_fahrenheit_to_Celsius(double f) {
  return (f - 32.0) * 5.0 / 9.0;
}

double calcHeatIndex(double Temp, double Humid) {
  double T = convert_Celsius_to_fahrenheit(Temp);
  double R = Humid;

  double HI =
      -42.379 + 2.04901523 * T + 10.14333127 * R - 0.22475541 * T * R -
      0.00683783 * T * T - 0.05481717 * R * R + 0.00122874 * T * T * R +
      0.00085282 * T * R * R - 0.00000199 * T * T * R * R;

  if (R < 13.0 && T >= 80.0 && T <= 112.0) {
    HI -= ((13.0 - R) / 4.0) * sqrt((17.0 - fabs(T - 95.0)) / 17.0);
  } else if (R > 85.0 && T >= 80.0 && T <= 87.0) {
    HI += ((R - 85.0) / 10.0) * ((87.0 - T) / 5.0);
  }

  return convert_fahrenheit_to_Celsius(HI);
}