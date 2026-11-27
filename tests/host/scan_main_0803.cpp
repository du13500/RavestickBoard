
static void fakeNotify(NimBLERemoteCharacteristic *, uint8_t *, size_t, bool) {}
int main(){
 NimBLEScan*sc=NimBLEDevice::getScan();
 // 1) Tafel gesehen (nach zwei fremden Geraeten, Adressart random) -> Warteschleife stoppt, kein Stop aus dem Rueckruf
 sc->script={{"11:22:33:44:55:66",-80},{"aa:bb:cc:dd:ee:ff",-70},{"C0:FF:EE:00:00:01",-55,"",false,1},{"99:99:99:99:99:99",-40}};
 int8_t v=bleScanForSign(); assert(!sc->active); assert(v==1); assert(scanLastMs==920); assert(scanLastRssi==-55);
 assert(scanAnyAdv==3);                 // 4. Geraet nach dem Stopp nicht mehr gezaehlt
 assert(sc->stopCalls==1 && !sc->isScanning());
 assert(bleSignAddrType==1);            // Adressart der Tafel gemerkt (fuer NimBLEAddress beim Verbinden)
 assert(sc->maxResults==0 && sc->wantDup==false);   // nur Rueckrufe, keine Ergebnisliste, keine Doppelmeldungen
 // 2) nur fremde Geraete -> nicht gesehen, volle Zeit (3 s), Scan lief von selbst aus
 sc->stopCalls=0; sc->script={{"11:22:33:44:55:66",-80},{"aa:bb:cc:dd:ee:ff",-70}};
 v=bleScanForSign(); assert(v==0); assert(scanLastMs>=3000&&scanLastMs<=3010); assert(scanLastRssi==0); assert(sc->stopCalls==0);
 // 3) gar nichts gehoert -> ohne Aussage
 sc->script={}; v=bleScanForSign(); assert(v==-1);
 // 4) Scan laesst sich nicht starten -> ohne Aussage, kein Haenger
 sc->failStart=true; sc->script={{"C0:FF:EE:00:00:01",-55}}; v=bleScanForSign(); assert(v==-1); sc->failStart=false;
 assert(diagnostics.scanRuns==4&&diagnostics.scanSeen==1&&diagnostics.scanMissed==1&&diagnostics.scanInconclusive==2);

 // Hilfsdatei: Adresse mit Art, Verbindungs-Timeout, MTU-Warten, Anmelden
 NimBLEAddress ad=rbBleAddress("c0:ff:ee:00:00:01",1); assert(ad.type==1 && ad.a=="c0:ff:ee:00:00:01");
 NimBLEClient cl; assert(rbBleConnect(&cl,ad)); assert(cl.timeoutMs==RB_BLE_CONNECT_MS && RB_BLE_CONNECT_MS==7000); assert(cl.last.type==1);
 assert(cl.getMTU()==23);                                  // sofort nach dem Verbinden noch Standardwert (NimBLE handelt asynchron aus)
 uint32_t t=fakeMs; uint16_t m=rbBleWaitMtu(&cl,247-0,1500); assert(m==247); assert(fakeMs-t>=200&&fakeMs-t<400);
 NimBLEClient cl2; cl2.connected=true; cl2.mtuReadyAt=0xFFFFFFFFu; t=fakeMs; m=rbBleWaitMtu(&cl2,247,1500); assert(m==23); assert(fakeMs-t>=1500&&fakeMs-t<1600);   // MTU kommt nie: begrenzt
 NimBLEClient cl3; cl3.connected=false; t=fakeMs; m=rbBleWaitMtu(&cl3,247,1500); assert(fakeMs==t);     // nicht verbunden: kein Warten
 NimBLERemoteCharacteristic rc; assert(rbBleSubscribe(&rc,fakeNotify)&&rc.subCalls==1); rc.subOk=false; assert(!rbBleSubscribe(&rc,fakeNotify));
 for(auto&e:events)puts(e.c_str());
 puts("PASS scan host"); return 0; }
