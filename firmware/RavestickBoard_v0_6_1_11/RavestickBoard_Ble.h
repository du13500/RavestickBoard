// RavestickBoard_Ble.h – Bluetooth-Unterbau (seit 0.6.1.10: NimBLE-Arduino von h2zero statt Bluedroid)
//
// Alles, was von der Version der NimBLE-Bibliothek abhaengt, steht hier an einer Stelle. Der Sketch ruft nur
// die kleinen Funktionen rbBle...() auf; Abfolge, Meldungen und Zeiten des Sketches bleiben wie in 0.6.1.9.
//
//   RB_NIMBLE_V1 0 (Standard)  NimBLE-Arduino 2.x   (Bibliotheksverwalter: "NimBLE-Arduino", Version 2.x)
//   RB_NIMBLE_V1 1             NimBLE-Arduino 1.4.x (nur falls 2.x nicht zum installierten Arduino-Core passt;
//                              dann vor dem Include "#define RB_NIMBLE_V1 1" in den Sketch schreiben)
//
// Unterschiede, die hier verdeckt werden (2.x gegenueber 1.4.x):
//   * Scan-Rueckrufe: NimBLEScanCallbacks::onResult(const NimBLEAdvertisedDevice*) statt
//     NimBLEAdvertisedDeviceCallbacks::onResult(NimBLEAdvertisedDevice*); Anmeldung per setScanCallbacks().
//   * Zeitangaben (Scan-Dauer, Verbindungs-Timeout) in Millisekunden statt Sekunden.
//   * Der Scan wird nicht blockierend gestartet; gewartet wird im Sketch (so muss stop() nie aus dem Rueckruf
//     heraus aufgerufen werden, was in aelteren 2.x-Staenden zu Abstuerzen fuehren konnte).
//   * Benachrichtigungen: subscribe(true, Rueckruf) statt registerForNotify().
#ifndef RAVESTICKBOARD_BLE_H
#define RAVESTICKBOARD_BLE_H

#include <Arduino.h>
#include <string>

#if defined(__has_include)
#if !__has_include(<NimBLEDevice.h>)
#error "Bibliothek NimBLE-Arduino (h2zero) fehlt: Arduino IDE > Bibliotheksverwalter > 'NimBLE-Arduino' installieren (siehe README)."
#endif
#endif
#include <NimBLEDevice.h>

#ifndef RB_NIMBLE_V1
#define RB_NIMBLE_V1 0
#endif

// 0.6.1.11: Version der installierten NimBLE-Arduino-Bibliothek fuer die Diagnose. Ab 2.4 gibt es NimBLECppVersion.h mit
// Versions-Makros. Die Namen der Makros sind aus der Beschreibung der Bibliothek uebernommen und nicht am Quelltext geprueft;
// passen sie nicht, meldet die Diagnose "nicht abfragbar" (kein Compile-Fehler). Getestet wurde 0.6.1.10 mit 2.5.2.
#if defined(__has_include)
#if __has_include(<NimBLECppVersion.h>)
#include <NimBLECppVersion.h>
#endif
#endif
static inline const char *rbBleLibVersion() {
#if defined(NIMBLE_CPP_VERSION_STR)
  return NIMBLE_CPP_VERSION_STR;
#elif defined(NIMBLE_CPP_VERSION_MAJOR) && defined(NIMBLE_CPP_VERSION_MINOR) && defined(NIMBLE_CPP_VERSION_PATCH)
  static char v[16];
  snprintf(v, sizeof(v), "%d.%d.%d", (int)NIMBLE_CPP_VERSION_MAJOR, (int)NIMBLE_CPP_VERSION_MINOR, (int)NIMBLE_CPP_VERSION_PATCH);
  return v;
#else
  return nullptr;
#endif
}

// Verbindungs-Timeout in ms. NimBLE 2.5 und neuer wiederholt einen fehlgeschlagenen Verbindungsaufbau bis zu 2 mal selbst;
// 3 x 7 s bleiben unter dem Hang-Waechter (RB_HANG_RESTART_MS = 25 s). In 0.6.1.9 waren es 10 s (Bluedroid, ohne Wiederholung).
#ifndef RB_BLE_CONNECT_MS
#define RB_BLE_CONNECT_MS 7000UL
#endif

#if RB_NIMBLE_V1
typedef NimBLEAdvertisedDeviceCallbacks RbScanCallbacksBase;
typedef NimBLEAdvertisedDevice *RbAdvArg;
#else
typedef NimBLEScanCallbacks RbScanCallbacksBase;
typedef const NimBLEAdvertisedDevice *RbAdvArg;
#endif

// Scan vorbereiten: nur Rueckrufe, keine gespeicherte Ergebnisliste (spart Heap), 100 ms Intervall, 99 ms Fenster wie bisher.
static inline void rbBleScanConfig(NimBLEScan *scan, RbScanCallbacksBase *callbacks, bool active) {
#if RB_NIMBLE_V1
  scan->setAdvertisedDeviceCallbacks(callbacks, false);
#else
  scan->setScanCallbacks(callbacks, false);
#endif
  scan->setActiveScan(active);
  scan->setInterval(100);
  scan->setWindow(99);
  scan->setMaxResults(0);
}

// Scan starten (kehrt sofort zurueck). false = Start nicht moeglich.
static inline bool rbBleScanBegin(NimBLEScan *scan, uint32_t ms) {
#if RB_NIMBLE_V1
  return scan->start((ms + 999UL) / 1000UL, nullptr, false);
#else
  return scan->start(ms, false, true);
#endif
}

// Wartet auf das Ende des Scans (hoechstens ms + 1,5 s) oder bis *stopFlag gesetzt wird; ein dann noch laufender Scan wird gestoppt.
static inline void rbBleScanWait(NimBLEScan *scan, uint32_t ms, volatile bool *stopFlag) {
  const uint32_t t0 = millis();
  while (scan->isScanning() && !(stopFlag && *stopFlag) && millis() - t0 < ms + 1500UL) delay(5);
  if (scan->isScanning()) { scan->stop(); delay(20); }   // dem Controller einen Augenblick geben, bevor verbunden wird
}

// Verbindung zur Tafel. Die Adressart (public/random) muss stimmen; sie stammt aus dem Vor-Scan.
static inline NimBLEAddress rbBleAddress(const char *text, uint8_t addrType) {
  return NimBLEAddress(std::string(text), addrType);
}
static inline bool rbBleConnect(NimBLEClient *client, const NimBLEAddress &address) {
#if RB_NIMBLE_V1
  client->setConnectTimeout((uint8_t)(RB_BLE_CONNECT_MS / 1000UL));
#else
  client->setConnectTimeout(RB_BLE_CONNECT_MS);
#endif
  return client->connect(address);
}

// MTU abfragen. NimBLE handelt die MTU nach dem Verbindungsaufbau asynchron aus; ein sofortiges getMTU() koennte noch den
// Standardwert (23) liefern und die einmalige Neuverbindung des Sketches ausloesen. Daher bis zu maxMs warten, bis der Wert reicht.
static inline uint16_t rbBleWaitMtu(NimBLEClient *client, uint16_t minMtu, uint32_t maxMs) {
  const uint32_t t0 = millis();
  uint16_t mtu = client->getMTU();
  while (mtu < minMtu && client->isConnected() && millis() - t0 < maxMs) { delay(25); mtu = client->getMTU(); }
  return mtu;
}

// Benachrichtigungen der Tafel anmelden (Bestaetigung je Paket).
static inline bool rbBleSubscribe(NimBLERemoteCharacteristic *c,
                                  void (*callback)(NimBLERemoteCharacteristic *, uint8_t *, size_t, bool)) {
  return c->subscribe(true, callback);
}

#endif  // RAVESTICKBOARD_BLE_H
