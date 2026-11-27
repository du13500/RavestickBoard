"""WLAN-Einstellungen mit dem ECHTEN Sketch-Code (Abschnitt "WLAN-Passwort einstellbar" und die zugehoerigen Variablen):
Passwort, Puffer-Umschalter (eigene Initialisierung des WLAN-Treibers vor Arduino), WPA2/WPA3 mit Rueckfall,
BOOT-Taste, Routen /api/wifi, /api/wifi/password, /api/wifi/settings. NVS, WiFi, esp_wifi und Webserver sind
Attrappen; ob der echte Treiber die Werte uebernimmt, zeigt nur die Hardware (Diagnosezeile "WLAN-Puffer")."""
from pathlib import Path
import json, subprocess, tempfile

ROOT = Path(__file__).resolve().parents[1]
fw = ROOT / 'firmware' / 'RavestickBoard_v0_8_1'
ino = (fw / 'RavestickBoard_v0_8_1.ino').read_text(encoding='utf8')

g_a = ino.index('static char wifiPassword[64] = "";')
g_b = ino.index('static String wifiBufText();')
g_b = ino.index('\n', g_b) + 1
w_a = ino.index('// ---- WLAN-Passwort einstellbar')
w_b = ino.index('// ---- Tafelverwaltung (Speicher und HTTP)')
part = ino[g_a:g_b] + ino[w_a:w_b]

stub = r'''
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <string>
#include <map>
#include <vector>
#include <cassert>
#include <iostream>
class String {
public:
  std::string s;
  String() {}
  String(const char *c) : s(c ? c : "") {}
  String(const std::string &x) : s(x) {}
  String(int v) : s(std::to_string(v)) {}
  String(unsigned v) : s(std::to_string(v)) {}
  String(unsigned long v) : s(std::to_string(v)) {}
  String(unsigned char v) : s(std::to_string((int)v)) {}
  const char *c_str() const { return s.c_str(); }
  size_t length() const { return s.size(); }
  bool operator==(const char *o) const { return s == o; }
  String &operator+=(const String &o) { s += o.s; return *this; }
  String &operator+=(const char *o) { s += o; return *this; }
};
inline String operator+(const String &a, const String &b) { return String(a.s + b.s); }
inline String operator+(const String &a, const char *b) { return String(a.s + b); }
inline String operator+(const char *a, const String &b) { return String(std::string(a) + b.s); }
inline String operator+(const String &a, int b) { return String(a.s + std::to_string(b)); }
inline String operator+(const String &a, unsigned char b) { return String(a.s + std::to_string((int)b)); }
static std::map<std::string, std::map<std::string, std::string>> nvs;
static bool nvsFail = false;
struct Preferences {
  std::string ns; bool ro = false;
  bool begin(const char *n, bool r) { if (nvsFail) return false; ns = n; ro = r; if (r && !nvs.count(ns)) return false; nvs[ns]; return true; }
  void end() {}
  String getString(const char *k, const char *d) { auto &m = nvs[ns]; return m.count(k) ? String(m[k]) : String(d); }
  size_t putString(const char *k, const char *v) { nvs[ns][k] = v; return strlen(v); }
  uint8_t getUChar(const char *k, uint8_t d) { auto &m = nvs[ns]; return m.count(k) ? (uint8_t)std::stoi(m[k]) : d; }
  size_t putUChar(const char *k, uint8_t v) { nvs[ns][k] = std::to_string((int)v); return 1; }
  bool isKey(const char *k) { return nvs[ns].count(k) > 0; }
  bool remove(const char *k) { return nvs[ns].erase(k) > 0; }
  bool clear() { nvs[ns].clear(); return true; }
};
typedef int esp_err_t;
static constexpr esp_err_t ESP_OK = 0;
typedef enum { WIFI_AUTH_WPA2_PSK = 3, WIFI_AUTH_WPA2_WPA3_PSK = 7 } wifi_auth_mode_t;
struct wifi_init_config_t { int static_rx_buf_num = 10, dynamic_rx_buf_num = 32, tx_buf_type = 1, static_tx_buf_num = 0,
                            dynamic_tx_buf_num = 32, cache_tx_buf_num = 0, rx_ba_win = 6; };
#define WIFI_INIT_CONFIG_DEFAULT() wifi_init_config_t()
static wifi_init_config_t lastCfg; static int wifiInitCalls = 0; static esp_err_t wifiInitResult = ESP_OK;
static esp_err_t esp_wifi_init(const wifi_init_config_t *c) { lastCfg = *c; ++wifiInitCalls; return wifiInitResult; }
static int deauthCalls = 0; static void esp_wifi_deauth_sta(int) { ++deauthCalls; }
struct NetworkStub { bool ok = true; int calls = 0; bool begin() { ++calls; return ok; } } Network;
struct ApCall { std::string ssid, pw; int max; wifi_auth_mode_t auth; };
struct WiFiStub {
  std::vector<ApCall> calls; bool failWpa3 = false; int disconnects = 0;
  bool softAP(const char *s, const char *p, int, int, int m, bool, wifi_auth_mode_t a) {
    calls.push_back({s, p, m, a}); return !(failWpa3 && a == WIFI_AUTH_WPA2_WPA3_PSK); }
  bool softAPdisconnect(bool) { ++disconnects; return true; }
} WiFi;
static constexpr char WIFI_SSID[] = "RavestickBoard";
static constexpr char WIFI_PASSWORD[] = "Standard-1234";
static constexpr int RB_AP_MAX_CLIENTS = 2;
static uint32_t nowMs = 1000;
static uint32_t millis() { return nowMs; }
static void delay(uint32_t) {}
static int pinLevel = 1; static constexpr int LOW = 0;
static int digitalRead(int) { return pinLevel; }
static std::vector<std::string> events;
static void diagnosticEvent(const char *t, const String &m, bool = false) { events.push_back(std::string(t) + ": " + m.s); }
struct SerialStub { void println(const char *) {} } Serial;
static int restarts = 0;
struct EspStub { void restart() { ++restarts; } } ESP;
enum Job { NONE, TEXT };
static Job nextJob = NONE;
struct WebStub {
  std::map<std::string, std::string> args; int status = 0; std::string body;
  String arg(const char *k) { return args.count(k) ? String(args[k]) : String(""); }
  bool hasArg(const char *k) { return args.count(k) > 0; }
  void sendHeader(const char *, const char *) {}
  void send(int c, const char *, const String &b) { status = c; body = b.s; }
} web;
static String jsonQuote(const String &x) { return String("\"" + x.s + "\""); }
static void respond(bool ok, const String &m, int st = 200) { web.status = st; web.body = std::string("{\"ok\":") + (ok ? "true" : "false") + ",\"message\":\"" + m.s + "\"}"; }
'''

main = r'''
static void req(std::map<std::string, std::string> a) { web.args = a; web.status = 0; web.body.clear(); }
static int fails = 0;
#define CHECK(c, m) do { if (!(c)) { std::cout << "FAIL " << m << "\n"; ++fails; } } while (0)
static void boot() { wifiPasswordLoad(); wifiSettingsLoad(); wifiBuffersInit(); WiFi.calls.clear(); wifiApStart(); }
int main() {
  // 1. Leerer Speicher: Standardpasswort, Puffer begrenzt (Voreinstellung), WPA2
  boot();
  CHECK(!wifiCustom && std::string(wifiPassword) == WIFI_PASSWORD, "Standardpasswort ohne NVS");
  CHECK(wifiBufMode == 1 && wifiBufActive == 1 && wifiInitCalls == 1 && Network.calls == 1, "begrenzt ist Voreinstellung und wird initialisiert");
  CHECK(lastCfg.static_rx_buf_num == 4 && lastCfg.dynamic_rx_buf_num == 8 && lastCfg.dynamic_tx_buf_num == 32 &&
        lastCfg.static_tx_buf_num == 0 && lastCfg.cache_tx_buf_num == 4 && lastCfg.tx_buf_type == 1, "Werte wie Arduino, nur 8 dynamische Empfangspuffer");
  CHECK(lastCfg.dynamic_rx_buf_num >= lastCfg.static_rx_buf_num, "dynamisch >= statisch (Kconfig-Regel)");
  CHECK(WiFi.calls.size() == 1 && WiFi.calls[0].auth == WIFI_AUTH_WPA2_PSK && WiFi.calls[0].max == 2, "WPA2, zwei Geraete");
  CHECK(wifiBufText().s.find("begrenzt (4 statisch, 8 dynamisch)") == 0, "Diagnosetext begrenzt");
  // 2. GET /api/wifi: nie das Passwort
  req({}); onWifiInfo();
  CHECK(web.status == 200 && web.body.find("\"buf\":1") != std::string::npos && web.body.find("\"bufActive\":1") != std::string::npos &&
        web.body.find("\"rxDynamic\":8") != std::string::npos && web.body.find("\"sec\":0") != std::string::npos, "Info enthaelt Puffer und Sicherheit");
  {  // nur das öffentliche Standardpasswort, und nur im Feld "standard" (Hinweis in den Einstellungen)
    const std::string std_ = std::string("\"standard\":\"") + WIFI_PASSWORD + "\"";
    const size_t at = web.body.find(WIFI_PASSWORD);
    CHECK(at != std::string::npos && web.body.find(std_) != std::string::npos && web.body.find(WIFI_PASSWORD, at + 1) == std::string::npos, "Info nennt nur das Standardpasswort im Feld standard");
  }
  snprintf(wifiPassword, sizeof(wifiPassword), "%s", "Geheim-Eigen-77"); wifiCustom = true;
  req({}); onWifiInfo();
  CHECK(web.body.find("Geheim-Eigen-77") == std::string::npos, "eigenes Passwort steht nie in der Info");
  wifiPasswordUseDefault();
  // 3. Puffer auf Arduino-Standard: gespeichert, wirkt erst nach Neustart
  req({{"buf", "0"}}); onWifiSettings();
  CHECK(web.status == 200 && nvs["rbwifi"]["buf"] == "0" && wifiBufMode == 0 && wifiBufActive == 1, "Standard gespeichert, noch begrenzt aktiv");
  CHECK(web.body.find("nächsten Neustart") != std::string::npos && !wifiRebootAt, "Hinweis auf Neustart, kein automatischer Neustart");
  CHECK(wifiBufText().s.find("ab Neustart Arduino-Standard") != std::string::npos, "Diagnose nennt den Unterschied");
  // 4. Neustart mit restart=1
  req({{"buf", "0"}, {"restart", "1"}}); onWifiSettings();
  CHECK(wifiRebootAt != 0 && web.body.find("startet gleich neu") != std::string::npos, "Neustart vorgemerkt");
  nextJob = TEXT; nowMs += 5000; wifiPoll(); CHECK(restarts == 0, "kein Neustart waehrend eines Auftrags");
  nextJob = NONE; wifiPoll(); CHECK(restarts == 1 && deauthCalls == 1, "Neustart nach dem Auftrag, Geraete abgemeldet");
  wifiRebootAt = 0;
  // 5. Nach dem Neustart: Arduino-Standard, keine eigene Initialisierung
  wifiInitCalls = 0; boot();
  CHECK(wifiBufActive == 0 && wifiInitCalls == 0 && wifiBufText().s.find("Arduino-Standard (4 statisch, 32 dynamisch)") == 0, "Standard: Arduino initialisiert selbst");
  // 6. Eigene Initialisierung scheitert -> Standard, Fehler in der Diagnose
  nvs["rbwifi"]["buf"] = "1"; wifiInitResult = 0x101; boot();
  CHECK(wifiBufActive == 0 && wifiBufInitErr == 0x101 && wifiBufText().s.find("fehlgeschlagen") != std::string::npos, "Fehler sichtbar, Rueckfall Standard");
  wifiInitResult = ESP_OK;
  Network.ok = false; boot(); CHECK(wifiBufActive == 0 && wifiBufInitErr == -1, "Network.begin scheitert"); Network.ok = true;
  // 7. WPA2/WPA3: speichert, startet das WLAN neu
  boot(); WiFi.calls.clear();
  req({{"sec", "1"}}); onWifiSettings();
  CHECK(web.status == 200 && nvs["rbwifi"]["sec"] == "1" && wifiApRestartAt != 0, "WPA3 gespeichert, WLAN-Neustart vorgemerkt");
  nowMs += 2000; wifiPoll();
  CHECK(WiFi.calls.size() == 1 && WiFi.calls[0].auth == WIFI_AUTH_WPA2_WPA3_PSK && wifiSecActive == 1, "AP mit WPA2/WPA3");
  // 8. WPA3-Start scheitert -> WPA2
  WiFi.failWpa3 = true; WiFi.calls.clear(); wifiApStart();
  CHECK(WiFi.calls.size() == 2 && WiFi.calls[1].auth == WIFI_AUTH_WPA2_PSK && wifiSecActive == 0 && wifiSecMode == 1, "Rueckfall auf WPA2");
  WiFi.failWpa3 = false;
  // 9. Eigenes Passwort; Zuruecksetzen loescht nur "pw", nicht die anderen Einstellungen
  req({{"pw", "geheim-12345"}}); onWifiPassword();
  CHECK(web.status == 200 && wifiCustom && nvs["rbwifi"]["pw"] == "geheim-12345", "eigenes Passwort gespeichert");
  CHECK(web.body.find("geheim-12345") == std::string::npos, "Antwort ohne Passwort");
  wifiApRestartAt = 0;
  req({{"reset", "1"}}); onWifiPassword();
  CHECK(!nvs["rbwifi"].count("pw") && nvs["rbwifi"]["buf"] == "1" && nvs["rbwifi"]["sec"] == "1", "Reset loescht nur das Passwort");
  wifiApRestartAt = 0;
  req({{"reset", "1"}}); onWifiPassword(); CHECK(web.status == 200, "Reset ohne gespeichertes Passwort ist kein Fehler");
  wifiApRestartAt = 0;
  // 10. BOOT-Taste: Standardpasswort und WPA2
  nvs["rbwifi"]["pw"] = "anderes-pw-1"; boot(); WiFi.calls.clear();
  pinLevel = LOW; wifiPoll(); nowMs += 5001; wifiPoll();
  CHECK(!wifiCustom && nvs["rbwifi"]["sec"] == "0" && wifiSecMode == 0 && !nvs["rbwifi"].count("pw"), "BOOT: Standardpasswort und WPA2");
  CHECK(!WiFi.calls.empty() && WiFi.calls.back().auth == WIFI_AUTH_WPA2_PSK && WiFi.calls.back().pw == WIFI_PASSWORD, "AP neu mit Standard und WPA2");
  pinLevel = 1; wifiPoll();
  // 11. Ungueltige Anfragen
  req({}); onWifiSettings(); CHECK(web.status == 400, "ohne Einstellung 400");
  req({{"pw", "kurz"}}); onWifiPassword(); CHECK(web.status == 400, "zu kurzes Passwort 400");
  nvsFail = true; req({{"buf", "1"}}); onWifiSettings(); CHECK(web.status == 500, "NVS nicht beschreibbar 500"); nvsFail = false;
  std::cout << "FAILS: " << fails << "\n";
  return fails ? 1 : 0;
}
'''

tmp = Path(tempfile.mkdtemp())
(tmp / 't.cpp').write_text(stub + part + main, encoding='utf8')
subprocess.run(['g++', '-std=c++17', '-Wall', '-Wextra', '-Wno-unused', '-Wno-unused-function', '-o', str(tmp / 't'), str(tmp / 't.cpp')], check=True)
r = subprocess.run([str(tmp / 't')], capture_output=True, text=True)
print(r.stdout.strip())
assert r.returncode == 0
print('PASS WLAN-Einstellungen (echter Sketch-Code): Puffer begrenzt/Standard, Neustart, WPA2/WPA3 mit Rueckfall, Passwort, BOOT-Taste')
