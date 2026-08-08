#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "esp_timer.h"
#include <esp_arduino_version.h>
#include <DFRobotDFPlayerMini.h>

// ---------------- LEDC COMPATIBILITY WRAPPERS ----------------
//
// Arduino-ESP32 2.x uses channel-based LEDC calls.
// Arduino-ESP32 3.x uses pin-based LEDC calls.

const int AUDIO_PWM_CHANNEL = 0;

void audioPwmAttach(uint8_t pin, uint32_t freq, uint8_t bits) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcAttach(pin, freq, bits);
#else
  ledcSetup(AUDIO_PWM_CHANNEL, freq, bits);
  ledcAttachPin(pin, AUDIO_PWM_CHANNEL);
#endif
}

void audioPwmWrite(uint8_t pin, uint32_t duty) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcWrite(pin, duty);
#else
  ledcWrite(AUDIO_PWM_CHANNEL, duty);
#endif
}

void audioPwmTone(uint8_t pin, uint32_t freq) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcWriteTone(pin, freq);
#else
  ledcWriteTone(AUDIO_PWM_CHANNEL, freq);
#endif
}

// ---------------- USER SETTINGS ----------------

const int PIN_LEFT  = D2;
const int PIN_RIGHT = D3;

// This is the max allowed difference between LEFT and RIGHT pulse rising edges.
const uint32_t COINC_WINDOW_US = 3;

// Delayed-coincidence lag used to estimate false positives.
// 500 ms is far longer than a true annihilation coincidence, but short enough
// that detector rates should not drift much.
const uint64_t FALSE_LAG_US = 500000ULL;

// Rolling-rate window for CPM display.
const uint64_t RATE_WINDOW_US = 60ULL * 1000000ULL;

// Serial speed. USB CDC usually handles this easily.
const uint32_t SERIAL_BAUD = 230400;

// OLED settings.
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
const uint8_t OLED_ADDR = 0x3C;

// ---------------- LIVE COINCIDENCE ALERT ----------------

const bool ENABLE_BUZZER_CHIRP = true;    // local chirp on D6 passive buzzer
const bool ENABLE_DFPLAYER_AUDIO = true;  // play /MP3/0001.mp3 on DFPlayer
const bool TEST_ALERT_ON_BOOT = false;    // set true to test alert at startup

const int ALERT_LED_PIN = D5;
const int AUDIO_PIN = D6;                 // passive buzzer signal pin

// Simple chirp settings for the passive buzzer.
const uint32_t CHIRP_FREQ_HZ = 2500;
const uint32_t CHIRP_MS = 80;
const uint8_t CHIRP_PWM_BITS = 8;
const uint8_t CHIRP_DUTY = 128;           // 50% duty for 8-bit PWM

// LED flash duration.
const uint32_t ALERT_FLASH_MS = 120;

uint32_t alertOffLedAt_ms = 0;
uint32_t chirpOffAt_ms = 0;
bool chirpActive = false;

// ---------------- DFPLAYER AUDIO ----------------
//
// Install library: Arduino IDE -> Library Manager -> "DFRobotDFPlayerMini".
//
// Recommended SD card file:
//   /MP3/0001.mp3   when DFPLAYER_USE_MP3_FOLDER = true
//
// For a WAV file, either convert it to /MP3/0001.mp3 for best compatibility,
// or set DFPLAYER_USE_MP3_FOLDER = false and place a numbered file such as
//   /0001.wav
// on the card.
//
// Wiring concept:
//   Nano/ESP32 DFPLAYER_TX_PIN -> 1k resistor -> DFPlayer RX
//   Nano/ESP32 DFPLAYER_RX_PIN <- DFPlayer TX
//   Nano/ESP32 GND             -> DFPlayer GND
//   5V/VBUS/VIN-side power     -> DFPlayer VCC
//   DFPlayer SPK_1/SPK_2       -> speaker terminals
//
// IMPORTANT: choose pins that are actually free on your Nano ESP32.
// D2 and D3 are already Geiger inputs, D5 is LED, D6 is buzzer, A4/A5 are OLED I2C.
// D7/D8 are suggested here, but change them if your wiring uses different pins.
const int DFPLAYER_RX_PIN = A1;   // physical A1 = ESP32-S3 GPIO2; receives DFPlayer TX
const int DFPLAYER_TX_PIN = A2;   // physical A2 = ESP32-S3 GPIO3; sends to DFPlayer RX through ~1k
const uint32_t DFPLAYER_BAUD = 9600;
const uint8_t DFPLAYER_VOLUME = 24;        // 0..30
const bool DFPLAYER_USE_MP3_FOLDER = true; // true => /MP3/0001.mp3, false => indexed root track
const uint16_t DFPLAYER_FILE_NUMBER = 1;   // /MP3/0001.mp3 or /0001.wav depending on mode
const uint32_t DFPLAYER_RETRIGGER_GUARD_MS = 7000; // avoid restarting long clip

HardwareSerial dfSerial(1);
DFRobotDFPlayerMini dfPlayer;
bool dfPlayerOK = false;
uint32_t lastDfPlayerTrigger_ms = 0;

void setupDfPlayer() {
  dfSerial.begin(DFPLAYER_BAUD, SERIAL_8N1, DFPLAYER_RX_PIN, DFPLAYER_TX_PIN);

  // Give the DFPlayer a moment after power-up before initialization.
  delay(500);

  // isACK=false avoids waiting for command acknowledgments, keeping operation snappy.
  // doReset=true resets the module during initialization.
  if (!dfPlayer.begin(dfSerial, false, true)) {
    dfPlayerOK = false;
    Serial.println("# DFPlayer init failed; continuing without DFPlayer audio");
    return;
  }

  dfPlayerOK = true;
  dfPlayer.volume(DFPLAYER_VOLUME);
  Serial.println("# DFPlayer OK");
}

void playDfPlayerPhotonSound() {
  if (!ENABLE_DFPLAYER_AUDIO || !dfPlayerOK) {
    return;
  }

  uint32_t now_ms = millis();

  // Do not restart the clip repeatedly if coincidences arrive during playback.
  if (lastDfPlayerTrigger_ms != 0 &&
      (uint32_t)(now_ms - lastDfPlayerTrigger_ms) < DFPLAYER_RETRIGGER_GUARD_MS) {
    return;
  }

  lastDfPlayerTrigger_ms = now_ms;

  if (DFPLAYER_USE_MP3_FOLDER) {
    // Plays /MP3/0001.mp3 when DFPLAYER_FILE_NUMBER is 1.
    dfPlayer.playMp3Folder(DFPLAYER_FILE_NUMBER);
  } else {
    // Plays indexed root-level track, e.g. /0001.wav or /0001.mp3.
    dfPlayer.play(DFPLAYER_FILE_NUMBER);
  }
}

void startSimpleChirp() {
  audioPwmAttach(AUDIO_PIN, CHIRP_FREQ_HZ, CHIRP_PWM_BITS);
  audioPwmWrite(AUDIO_PIN, CHIRP_DUTY);

  chirpActive = true;
  chirpOffAt_ms = millis() + CHIRP_MS;
}

void stopSimpleChirp() {
  audioPwmWrite(AUDIO_PIN, 0);
  chirpActive = false;
  chirpOffAt_ms = 0;
}

void serviceSimpleChirp() {
  if (chirpActive &&
      chirpOffAt_ms != 0 &&
      (int32_t)(millis() - chirpOffAt_ms) >= 0) {
    stopSimpleChirp();
  }
}

void triggerCoincidenceAlert() {
  // Visual flash.
  digitalWrite(ALERT_LED_PIN, HIGH);
  alertOffLedAt_ms = millis() + ALERT_FLASH_MS;

  // Local buzzer chirp and external DFPlayer audio are independent.
  if (ENABLE_BUZZER_CHIRP) {
    startSimpleChirp();
  }

  if (ENABLE_DFPLAYER_AUDIO) {
    playDfPlayerPhotonSound();
  }
}

void serviceCoincidenceAlert() {
  if (alertOffLedAt_ms != 0 &&
      (int32_t)(millis() - alertOffLedAt_ms) >= 0) {
    digitalWrite(ALERT_LED_PIN, LOW);
    alertOffLedAt_ms = 0;
  }

  serviceSimpleChirp();
}

// ---------------- OLED ----------------

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
bool oledOK = false;

// ---------------- EVENT QUEUE FROM INTERRUPTS ----------------

struct RawEvent {
  uint64_t t_us;
  uint8_t channel; // 0 = left, 1 = right
};

const uint16_t EVENT_Q_SIZE = 512;

// Explicit prototypes prevent the Arduino preprocessor from generating
// prototypes above the RawEvent struct.
bool popEvent(RawEvent &ev);
void processEvent(const RawEvent &ev);

RawEvent eventQ[EVENT_Q_SIZE];

volatile uint16_t qHead = 0;
volatile uint16_t qTail = 0;
volatile uint32_t droppedEvents = 0;

portMUX_TYPE queueMux = portMUX_INITIALIZER_UNLOCKED;

void IRAM_ATTR pushEventFromISR(uint8_t channel) {
  uint64_t t = (uint64_t)esp_timer_get_time();

  portENTER_CRITICAL_ISR(&queueMux);

  uint16_t nextHead = (uint16_t)((qHead + 1) % EVENT_Q_SIZE);

  if (nextHead != qTail) {
    eventQ[qHead].t_us = t;
    eventQ[qHead].channel = channel;
    qHead = nextHead;
  } else {
    droppedEvents++;
  }

  portEXIT_CRITICAL_ISR(&queueMux);
}

void IRAM_ATTR leftISR() {
  pushEventFromISR(0);
}

void IRAM_ATTR rightISR() {
  pushEventFromISR(1);
}

bool popEvent(RawEvent &ev) {
  portENTER_CRITICAL(&queueMux);

  if (qTail == qHead) {
    portEXIT_CRITICAL(&queueMux);
    return false;
  }

  ev = eventQ[qTail];
  qTail = (uint16_t)((qTail + 1) % EVENT_Q_SIZE);

  portEXIT_CRITICAL(&queueMux);
  return true;
}

// ---------------- RING BUFFER FOR TIMESTAMPS ----------------

template <size_t N>
class TimeRing {
public:
  uint64_t times[N];
  size_t head = 0;
  size_t count = 0;

  void add(uint64_t t) {
    times[head] = t;
    head = (head + 1) % N;
    if (count < N) count++;
  }

  // Count timestamps >= cutoff.
  size_t countSince(uint64_t cutoff) const {
    size_t n = 0;

    for (size_t i = 0; i < count; i++) {
      size_t idx = (head + N - 1 - i) % N;
      uint64_t t = times[idx];

      if (t < cutoff) break;
      n++;
    }

    return n;
  }

  // Count timestamps in [lo, hi].
  size_t countInRange(uint64_t lo, uint64_t hi) const {
    size_t n = 0;

    for (size_t i = 0; i < count; i++) {
      size_t idx = (head + N - 1 - i) % N;
      uint64_t t = times[idx];

      if (t < lo) break;
      if (t <= hi) n++;
    }

    return n;
  }
};

// These sizes are intentionally generous for 60 seconds of data.
// At 900 CPM, one detector has ~900 events/minute.
const size_t DETECTOR_RING_SIZE = 8092;
const size_t COINC_RING_SIZE = 512;

TimeRing<DETECTOR_RING_SIZE> leftTimes;
TimeRing<DETECTOR_RING_SIZE> rightTimes;
TimeRing<COINC_RING_SIZE> promptCoincTimes;
TimeRing<COINC_RING_SIZE> delayedCoincTimes;

// ---------------- TOTAL COUNTS ----------------

uint64_t totalLeft = 0;
uint64_t totalRight = 0;
uint64_t totalPromptCoinc = 0;
uint64_t totalDelayedCoinc = 0;

uint64_t start_us = 0;

// ---------------- UTILITY ----------------

double cpmFromCount(size_t count, uint64_t now_us) {
  uint64_t elapsed = now_us - start_us;
  uint64_t denom = (elapsed < RATE_WINDOW_US) ? elapsed : RATE_WINDOW_US;

  if (denom == 0) return 0.0;

  return ((double)count) * 60.0 * 1000000.0 / (double)denom;
}

void updateDisplayAndSummary() {
  uint64_t now = (uint64_t)esp_timer_get_time();

  uint64_t cutoff = (now > RATE_WINDOW_US) ? (now - RATE_WINDOW_US) : 0;

  size_t left60   = leftTimes.countSince(cutoff);
  size_t right60  = rightTimes.countSince(cutoff);
  size_t prompt60 = promptCoincTimes.countSince(cutoff);
  size_t delay60  = delayedCoincTimes.countSince(cutoff);

  double leftCPM   = cpmFromCount(left60, now);
  double rightCPM  = cpmFromCount(right60, now);
  double promptCPM = cpmFromCount(prompt60, now);
  double delayCPM  = cpmFromCount(delay60, now);

  uint32_t dropped;
  portENTER_CRITICAL(&queueMux);
  dropped = droppedEvents;
  portEXIT_CRITICAL(&queueMux);

  // USB summary line.
  Serial.printf(
    "S,%llu,%.3f,%.3f,%.3f,%.3f,%llu,%llu,%llu,%llu,%lu\n",
    (unsigned long long)now,
    leftCPM,
    rightCPM,
    promptCPM,
    delayCPM,
    (unsigned long long)totalLeft,
    (unsigned long long)totalRight,
    (unsigned long long)totalPromptCoinc,
    (unsigned long long)totalDelayedCoinc,
    (unsigned long)dropped
  );

  if (!oledOK) return;

  long truePairEstimate = totalPromptCoinc - totalDelayedCoinc;

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);

  display.print("Left:  ");
  display.print(leftCPM, 1);
  display.println(" CPM");

  display.print("Right: ");
  display.print(rightCPM, 1);
  display.println(" CPM");

  display.println("");

  display.print("Pairs: ");
  display.print(promptCPM, 2);
  display.println(" CPM");

  display.print("False: ");
  display.print(delayCPM, 2);
  display.println(" CPM");

  display.println("");

  display.print("Detections: ");
  display.print(truePairEstimate);

  //display.print("Win: ");
  //display.print(COINC_WINDOW_US);
  //display.print(" us");

  //display.setCursor(0, 50);
  //display.print("Drop:");
  //display.print(dropped);

  display.display();
}

void processEvent(const RawEvent &ev) {
  TimeRing<DETECTOR_RING_SIZE> &myTimes  = (ev.channel == 0) ? leftTimes : rightTimes;
  TimeRing<DETECTOR_RING_SIZE> &oppTimes = (ev.channel == 0) ? rightTimes : leftTimes;

  const char *name = (ev.channel == 0) ? "L" : "R";
  int pin = (ev.channel == 0) ? PIN_LEFT : PIN_RIGHT;

  // Count prompt coincidences against opposite-channel events that happened
  // within COINC_WINDOW_US before this event.
  uint64_t promptLo = (ev.t_us > COINC_WINDOW_US) ? (ev.t_us - COINC_WINDOW_US) : 0;
  uint64_t promptHi = ev.t_us;

  size_t promptMatches = oppTimes.countInRange(promptLo, promptHi);

  for (size_t i = 0; i < promptMatches; i++) {
    promptCoincTimes.add(ev.t_us);
  }

  totalPromptCoinc += promptMatches;

  if (promptMatches > 0) {
    triggerCoincidenceAlert();
  }

  // Count delayed/lagged coincidences.
  // This must use the same effective window width as the prompt count.
  // Prompt uses a one-sided window: [t - COINC_WINDOW_US, t].
  // So the lag estimate should also use a one-sided window of the same width,
  // not center ± COINC_WINDOW_US, which would be twice as wide.
  size_t delayedMatches = 0;
  
  if (ev.t_us > FALSE_LAG_US + COINC_WINDOW_US) {
    uint64_t lagHi = ev.t_us - FALSE_LAG_US;
    uint64_t lagLo = lagHi - COINC_WINDOW_US;
  
    delayedMatches = oppTimes.countInRange(lagLo, lagHi);
  
    for (size_t i = 0; i < delayedMatches; i++) {
      delayedCoincTimes.add(ev.t_us);
    }

    totalDelayedCoinc += delayedMatches;
  }

  // Now record this event in its own detector history.
  myTimes.add(ev.t_us);

  if (ev.channel == 0) {
    totalLeft++;
  } else {
    totalRight++;
  }

  // Raw event line over USB.
  // Format:
  // E,board_time_us,detector_name,pin,prompt_matches,delayed_matches
  Serial.printf(
    "E,%llu,%s,%d,%u,%u\n",
    (unsigned long long)ev.t_us,
    name,
    pin,
    (unsigned int)promptMatches,
    (unsigned int)delayedMatches
  );
}

// ---------------- SETUP / LOOP ----------------

void setup() {
  Serial.begin(SERIAL_BAUD);
  delay(1000);

  start_us = (uint64_t)esp_timer_get_time();

  pinMode(PIN_LEFT, INPUT);
  pinMode(PIN_RIGHT, INPUT);

  attachInterrupt(digitalPinToInterrupt(PIN_LEFT), leftISR, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_RIGHT), rightISR, RISING);

  Wire.begin(); // Nano ESP32 default I2C: SDA=A4, SCL=A5.

  oledOK = display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR);
  if (oledOK) {
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);
    display.println("Geiger logger");
    display.println("OLED OK");
    display.display();
  }

  pinMode(ALERT_LED_PIN, OUTPUT);
  digitalWrite(ALERT_LED_PIN, LOW);

  if (ENABLE_BUZZER_CHIRP) {
    audioPwmAttach(AUDIO_PIN, CHIRP_FREQ_HZ, CHIRP_PWM_BITS);
    audioPwmWrite(AUDIO_PIN, 0);
  }

  if (ENABLE_DFPLAYER_AUDIO) {
    setupDfPlayer();
  }

  if (TEST_ALERT_ON_BOOT) {
    delay(2000);
    triggerCoincidenceAlert();
  }

  Serial.println("# Geiger coincidence logger");
  Serial.println("# E,t_us,detector,pin,prompt_matches,delayed_matches");
  Serial.println("# S,t_us,left_cpm,right_cpm,prompt_cpm,delayed_cpm,total_left,total_right,total_prompt,total_delayed,dropped");
  Serial.print("# COINC_WINDOW_US=");
  Serial.println(COINC_WINDOW_US);
  Serial.print("# FALSE_LAG_US=");
  Serial.println((unsigned long)FALSE_LAG_US);

}

void loop() {
  RawEvent ev;

  while (popEvent(ev)) {
    processEvent(ev);
  }

  serviceCoincidenceAlert();

  static uint64_t lastUpdate_us = 0;
  uint64_t now = (uint64_t)esp_timer_get_time();

  if (now - lastUpdate_us >= 1000000ULL) {
    lastUpdate_us = now;
    updateDisplayAndSummary();
  }
}