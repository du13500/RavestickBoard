// Attrappe der NimBLE-Arduino-2.x-Klassen (nur das, was RavestickBoard_Ble.h und der Sketch-Scan brauchen).
// Zeit laeuft nur ueber delay(): Der Scan "hoert" dabei die Geraete aus dem Skript, eines je stepMs.
// Signaturen entsprechen der Dokumentation von NimBLE-Arduino 2.x (Annahme, hier nicht gegen die echte Bibliothek uebersetzbar).
#pragma once
#include <string>
#include <vector>
#include <cstdint>
static uint32_t fakeMs = 1000;
struct NimBLEUUID { uint16_t u; NimBLEUUID(uint16_t x) : u(x) {} };
struct NimBLEAddress {
  std::string a; uint8_t type = 0;
  NimBLEAddress() {}
  NimBLEAddress(const std::string &s, uint8_t t = 0) : a(s), type(t) {}
  std::string toString() const { return a; }
};
struct NimBLEAdvertisedDevice {
  std::string addr; int rssi; std::string name = ""; bool ffo = false; uint8_t type = 0;
  NimBLEAddress getAddress() const { return NimBLEAddress(addr, type); }
  uint8_t getAddressType() const { return type; }
  int getRSSI() const { return rssi; }
  bool haveName() const { return !name.empty(); }
  std::string getName() const { return name; }
  bool haveServiceUUID() const { return ffo; }
  bool isAdvertisingService(const NimBLEUUID &u) const { return ffo && u.u == 0xFFF0; }
};
struct NimBLEScanCallbacks { virtual ~NimBLEScanCallbacks() {} virtual void onResult(const NimBLEAdvertisedDevice *) {} };
struct NimBLEScan {
  NimBLEScanCallbacks *cb = nullptr; bool active = false, scanning = false, wantDup = true; unsigned maxResults = 99;
  std::vector<NimBLEAdvertisedDevice> script; uint32_t stepMs = 300, durMs = 0, startMs = 0; size_t next = 0; int stopCalls = 0, startCalls = 0; bool failStart = false;
  void setScanCallbacks(NimBLEScanCallbacks *c, bool dup = false) { cb = c; wantDup = dup; }
  void setActiveScan(bool b) { active = b; }
  void setInterval(uint16_t) {} void setWindow(uint16_t) {}
  void setMaxResults(uint8_t n) { maxResults = n; }
  bool start(uint32_t ms, bool isContinue = false, bool restart = true) {
    ++startCalls; if (failStart) return false;
    scanning = true; durMs = ms; startMs = fakeMs; next = 0; return true; }
  bool isScanning() const { return scanning; }
  bool stop() { ++stopCalls; scanning = false; return true; }
  void clearResults() {}
  void pump() {   // wird von delay() aufgerufen: die im Zeitraum "gehoerten" Geraete an den Rueckruf geben
    if (!scanning) return;
    while (scanning && next < script.size() && fakeMs - startMs >= stepMs * (next + 1)) { cb->onResult(&script[next]); ++next; }
    if (scanning && fakeMs - startMs >= durMs) scanning = false;
  }
};
struct NimBLERemoteCharacteristic {
  bool subOk = true; int subCalls = 0;
  bool subscribe(bool, void (*)(NimBLERemoteCharacteristic *, uint8_t *, size_t, bool), bool = true) { ++subCalls; return subOk; }
};
struct NimBLEClient {
  bool connected = false, connectOk = true; uint32_t timeoutMs = 0; uint16_t mtu = 23; uint32_t mtuReadyAt = 0; NimBLEAddress last;
  void setConnectTimeout(uint32_t ms) { timeoutMs = ms; }
  bool connect(const NimBLEAddress &a) { last = a; connected = connectOk; mtuReadyAt = fakeMs + 200; return connectOk; }
  bool isConnected() const { return connected; }
  uint16_t getMTU() const { return fakeMs >= mtuReadyAt && connected ? 247 : mtu; }
};
struct NimBLEDevice { static NimBLEScan *getScan() { static NimBLEScan s; return &s; } };
