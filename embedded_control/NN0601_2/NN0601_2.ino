#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <FastLED.h>

#define NUM_LEDS 1
#define DATA_PIN 4
CRGB leds[NUM_LEDS];

unsigned int localPort = 1234;
WiFiUDP Udp;
char packetBuffer[UDP_TX_PACKET_MAX_SIZE + 1];

const char* ssid = "iPhone (322)";
const char* password = "1122334455";

const int M1 = 5;
const int M2 = 14;

int power1 = 0;
int power2 = 0;
bool flash = false;

void LED_red_flash() {
  if (flash) {
    leds[0] = CRGB::Red;
  } else {
    leds[0] = CRGB::Black;
  }
  FastLED.show();
  flash = !flash;
}

void setup() {
  Serial.begin(9600);
  FastLED.addLeds<WS2811, DATA_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(50);

  pinMode(M1, OUTPUT);
  pinMode(M2, OUTPUT);

  connectToWiFi();

  Udp.begin(localPort);
}

void loop() {
  maintainWiFiConnection();
  
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    int n = Udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE);
    packetBuffer[n] = 0;
    Serial.print("Received packet: ");
    Serial.println(packetBuffer);

    sscanf(packetBuffer, "M1:%d,M2:%d", &power1, &power2);
    if (power1 < 0) {
      analogWrite(M1, -power1);
      analogWrite(M2, -power2);
      delay(100); // 控制振动频率
      analogWrite(M1, 0);
      analogWrite(M2, 0);
    } else {
      analogWrite(M1, power1);
      analogWrite(M2, power2);
    }
    Serial.print("M1 power: ");
    Serial.println(power1);
    Serial.print("M2 power: ");
    Serial.println(power2);
  }
}

void connectToWiFi() {
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    LED_red_flash();
  }

  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  leds[0] = CRGB::Blue;
  FastLED.show();
}

void maintainWiFiConnection() {
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
  }
}
