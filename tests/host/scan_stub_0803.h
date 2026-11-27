
#include <string>
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <strings.h>
#include <vector>
#include <cassert>
#define RB_PRESCAN 1
#define RB_PRESCAN_S 3
struct SignRef { char addr[18]; char name[24]; };
static SignRef signMine = {}; static SignRef signActive = {"c0:ff:ee:00:00:01",""};
#include <ctype.h>
#include "NimBLEDevice.h"   // Attrappe (tests/host/nimble), definiert auch fakeMs
struct String{std::string s;String(){}String(const char*c):s(c){}String(unsigned long v):s(std::to_string(v)){}String(unsigned v):s(std::to_string(v)){}String(int v):s(std::to_string(v)){}
 String&operator+=(const String&o){s+=o.s;return *this;}String&operator+=(const char*c){s+=c;return *this;}String&operator+=(char c){s+=c;return *this;}String(const std::string&x):s(x){}String operator+(const char*c)const{return String((s+c).c_str());}String operator+(const String&o)const{return String((s+o.s).c_str());}const char*c_str()const{return s.c_str();}};
static std::vector<std::string> events; static std::string phase;
struct { uint32_t scanRuns=0,scanSeen=0,scanMissed=0,scanInconclusive=0; } diagnostics;
static void diagnosticEvent(const char*c,const String&d,bool e=false){events.push_back(std::string(c)+": "+d.s);}
static void rbPhase(const char*p){phase=p;}
static int scanLastRssi=0; static uint32_t scanLastMs=0;
static uint32_t millis(){return fakeMs;}
static void delay(uint32_t ms){fakeMs+=ms;NimBLEDevice::getScan()->pump();}
#include "RavestickBoard_Ble.h"   // die ECHTE Hilfsdatei des Sketches (gegen die Attrappe uebersetzt)
static volatile uint8_t bleSignAddrType=0;
