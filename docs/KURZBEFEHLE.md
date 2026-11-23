# Kurzbefehle: das RavestickBoard ohne Browser steuern

Mit einem Kurzbefehl schickst du einen Lauftext, startest eine Kurzwahl oder spielst eine Animation ab, ohne die Oberfläche zu öffnen. Auf dem iPhone geht das mit der App **Kurzbefehle** (auch per Siri), auf Android mit einer App, die Internetanfragen auf den Startbildschirm legt.

Wichtig vorab:

- Das Handy muss mit dem WLAN **RavestickBoard** verbunden sein. Ohne diese Verbindung erreicht der Kurzbefehl das Board nicht.
- Das Board hat immer die Adresse **http://192.168.4.1**.
- Dieses WLAN hat kein Internet. Das Handy bleibt trotzdem verbunden, wenn du beim Hinweis „Kein Internetzugang“ die Verbindung behältst. Siri braucht für die Spracherkennung meist mobile Daten; die Anfrage an das Board läuft trotzdem über das WLAN.
- Nicht auf echter Hardware geprüft (Stand v0.7.0). Bitte beim Hardwaretest ausprobieren.

## Was geht

| Was | Adresse | Felder |
|---|---|---|
| Lauftext senden | `http://192.168.4.1/api/text` | `text` = der Text |
| Kurzwahl auslösen | `http://192.168.4.1/api/shortcuts/run` | `slot` = Nummer der Kurzwahl, 1 bis 8 |
| Animation abspielen | `http://192.168.4.1/api/anim/send` | `id` = ID der Animation |

Alle drei sind **POST**-Anfragen mit den Feldern als Formular.

**Lauftext:** Es reicht das Feld `text`. Das Board nimmt dann die Standardwerte der Oberfläche: weiße Schrift, Lauftext, Schrift „Original - Normal“. Helligkeit und Tempo bleiben, wie sie gerade eingestellt sind. Umlaute gehen.

**Kurzwahl:** Die Kacheln der Startseite zählen von links oben nach rechts unten: 1 und 2 in der ersten Reihe, 3 und 4 in der zweiten, bis 7 und 8 in der letzten. Unbelegte Kacheln zeigen ihre Nummer. Was auf der Kachel liegt (Text, Blocktext, Programm, Ambiente oder Animation), startet der Kurzbefehl.

**Animation:** Die ID steht in der Oberfläche unter **Animationen** in der Zeile der Animation und unter der Vorschau („ID 3“). Sie bleibt gleich, wenn du die Animation umbenennst, verschiebst oder bearbeitest. Nach dem Löschen kann eine neue Animation die frei gewordene ID bekommen; dann passt der Kurzbefehl nicht mehr. Eine Kurzwahl ist deshalb oft die bessere Wahl: Sie zeigt immer auf das, was du ihr zugewiesen hast.

## iPhone: Kurzbefehle-App

### Lauftext per Siri

1. App **Kurzbefehle** öffnen, unten **Kurzbefehle**, oben rechts **+**.
2. **Aktion hinzufügen** → nach **Nach Eingabe fragen** suchen und antippen. Als Frage zum Beispiel „Was soll auf die Tafel?“ eintragen.
3. Nächste Aktion: **Inhalte von URL abrufen**. Als URL `http://192.168.4.1/api/text` eintragen.
4. Auf den kleinen Pfeil bei der Aktion tippen: **Methode** auf **POST**, **Hauptteil der Anfrage** auf **Formular**.
5. **Neues Feld** → **Text**. Schlüssel: `text`. Als Wert die Variable **Bereitgestellte Eingabe** wählen (über der Tastatur antippen).
6. Oben den Namen setzen, zum Beispiel „Tafeltext“. Danach reicht: „Hey Siri, Tafeltext“. Siri fragt nach dem Text und schickt ihn ab.

### Kurzwahl oder Animation

Wie oben, aber ohne **Nach Eingabe fragen**:

- Kurzwahl: URL `http://192.168.4.1/api/shortcuts/run`, Feld `slot` mit der Nummer, zum Beispiel `1`.
- Animation: URL `http://192.168.4.1/api/anim/send`, Feld `id` mit der ID, zum Beispiel `3`.

Den Kurzbefehl kannst du auch auf den Home-Bildschirm legen (Teilen-Knopf → **Zum Home-Bildschirm**).

## Android: App „HTTP Shortcuts“

Android hat keine eingebaute App dafür. Gut geeignet ist die kostenlose App **HTTP Shortcuts** (bei Google Play und F-Droid, quelloffen). Sie legt eine Anfrage als Symbol auf den Startbildschirm.

### Kurzwahl oder Animation

1. App öffnen, **+** → **Normaler Kurzbefehl** (bzw. „Regular Shortcut“).
2. Name zum Beispiel „Kurzwahl 1“. Methode **POST**, URL `http://192.168.4.1/api/shortcuts/run`.
3. Unter **Anfragetext / Body** den Typ **Formular (x-www-form-urlencoded)** wählen und ein Feld anlegen: Schlüssel `slot`, Wert `1`.
4. Speichern. Danach in der Liste lange drücken → **Auf dem Startbildschirm platzieren**.

Für eine Animation dasselbe mit der URL `http://192.168.4.1/api/anim/send` und dem Feld `id`.

### Lauftext mit Eingabe

1. In der App unter **Variablen** eine neue Variable vom Typ **Text-Eingabe** anlegen, Name zum Beispiel `tafeltext`.
2. Kurzbefehl wie oben anlegen, URL `http://192.168.4.1/api/text`, Formularfeld `text`, als Wert die Variable `{tafeltext}` einfügen.
3. Beim Antippen fragt die App nach dem Text und schickt ihn ab.

Falls Android die Anfrage über mobile Daten schickt und sie deshalb nicht ankommt: In den Einstellungen des Kurzbefehls gibt es die Option, nur WLAN zu verwenden.

## Antworten des Boards

| Antwort | Bedeutung | Was tun |
|---|---|---|
| 202 | Angenommen, die Übertragung an die Tafel läuft. | Nichts. |
| 409 | Das Board überträgt gerade etwas. Läuft ein Programm, endet es nach dem laufenden Schritt. | Nach ein paar Sekunden noch einmal auslösen. |
| 503 | Gerade zu wenig Speicher frei oder das Dateisystem ist nicht bereit. | Kurz warten, dann noch einmal. |
| 400 | Feld fehlt oder ist ungültig (leerer Text, Kurzwahl außerhalb 1 bis 8). | Kurzbefehl prüfen. |
| 404 | Kurzwahl leer oder Animation nicht vorhanden. | Kurzwahl belegen bzw. ID prüfen. |

## Für Entwickler: feste Routen

Diese Routen und Felder bleiben über Versionen gleich. Der Test `tests/host_routes_0700.py` prüft sie gegen den Sketch.

<!-- ROUTEN-ANFANG -->
| Methode | Pfad | Pflichtfelder | Optionale Felder |
|---|---|---|---|
| POST | /api/text | text | color, color2, mode, layout, line2 |
| POST | /api/shortcuts/run | slot | |
| POST | /api/anim/send | id | |
| GET | /api/status | | |
<!-- ROUTEN-ENDE -->

Optionale Felder für `/api/text`: `color` 1 bis 7 (1 Blau, 2 Grün, 3 Cyan, 4 Rot, 5 Magenta, 6 Gelb, 7 Weiß; Standard 7), `mode` `scroll` oder `static` (Standard `scroll`), `layout` 0 bis 4 (Standard 3 = „Original - Normal“), `line2` und `color2` nur bei `layout` 1 (zweizeilig).
