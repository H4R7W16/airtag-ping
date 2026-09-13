# Dateien und Geometrie reproduzieren

## Referenzumgebung

Getestet unter Windows mit FreeCAD **1.1.3**, Build `145529fe741292ff0b3977a01195bf0247425794`, dessen eingebauter Python-3.11-Laufzeit und OpenCASCADE. Für die optionalen CAD-Renderings wurden VTK 9.3.1 und Pillow 12.0.0 verwendet. Es werden keine externen FreeCAD-Add-ons benötigt.

FreeCAD enthält C++-Python-Module. Ein beliebiges `pip install` oder der normale System-Python ersetzt diese Laufzeit nicht. Die Dokumentation beschreibt die tatsächlich getestete Windows-Konfiguration. Andere FreeCAD-Versionen und Betriebssysteme wurden nicht ausgeführt. Die Skripte unterstützen optional `FREECAD_LIB` als Modul-Suchpfad; passende Binärversionen und abhängige Bibliotheken bleiben Voraussetzung.

## 1. Dateistand prüfen

Im entpackten Repository mit Python 3:

```console
python verify_files.py
```

Das Skript prüft alle in `SHA256SUMS` gelisteten Dateien. Ein abweichender Hash beendet die Prüfung mit Fehler. Dafür ist kein FreeCAD nötig. Bei beabsichtigten Änderungen lässt sich das Manifest mit `python verify_files.py --write` neu erstellen; anschließend dokumentieren, was geändert und neu geprüft wurde.

## 2. Mitgelieferte Geometrie prüfen

PowerShell im Repository-Ordner:

```powershell
$pingPython = 'C:\Program Files\FreeCAD 1.1\bin\python.exe'
& $pingPython .\verify_model.py
```

Die Prüfung liest die versionierte FCStd-, STEP- und STL-Dateien. Sie verändert das CAD nicht. Standardmäßig schreibt sie ihren Bericht nach `build/Pruefbericht.json`. Ohne `-O` ausführen, damit Assertions aktiv bleiben. Das Skript verweigert einen optimierten Python-Lauf.

```powershell
& $pingPython .\verify_model.py --artifact-dir . --report .\build\mein-pruefbericht.json
```

## 3. Konstruktion neu erzeugen

```powershell
& $pingPython .\PING_erzeugen.FCMacro
& $pingPython .\verify_model.py --artifact-dir .\build --report .\build\neu-erzeugt-pruefung.json
```

Der Generator legt standardmäßig `build/` an und erstellt dort FCStd, STEP, STL sowie BREP-Zwischenexporte. Die versionierten Originaldateien bleiben dadurch erhalten. Wiederholungen überschreiben gleichnamige Dateien innerhalb von `build/`. Der Generator baut seine dokumentierten Ausgangswerte; Änderungen an einer FCStd-Datei werden nicht als Eingabe übernommen.

Ein anderer Zielordner kann pro Sitzung gewählt werden:

```powershell
$env:PING_OUTPUT_DIR = Join-Path (Get-Location) 'build-variante'
& $pingPython .\PING_erzeugen.FCMacro
Remove-Item Env:PING_OUTPUT_DIR
```

Alternativ das Erzeugermakro in FreeCAD über **Makro → Makros** auswählen und ausführen. Auch dort ist `build/` neben dem Makro der Standard-Ausgabeordner. Bei der Kommandozeilenausführung wird die FreeCAD-GUI für Ansichtsattribute im Offscreen-Modus initialisiert. Die Referenzumgebung meldete dabei Qt-/OpenGL-Warnungen; die maßgebliche Erfolgskontrolle sind die exportierten Dateien und die anschließende Geometrieprüfung.

## 4. Ergebnisse vergleichen

FCStd/STEP können Zeitstempel, Ansichtsmetadaten oder Serialisierungsdetails enthalten. Deshalb ist ein identischer SHA-256-Hash eines **neu erzeugten** CAD-Containers nicht garantiert. Die Prüfsummen gelten für den veröffentlichten Stand. Für die Reproduktion vergleichen wir Geometrie, Volumina, Außenmaße und gültige Exporte innerhalb der [dokumentierten Toleranzen](PRUEFUNG.md).

`Pruefbericht.json` enthält die Prüfung des veröffentlichten Dateistands. `Reproduktionsbericht.json` enthält denselben Test auf einem separaten frisch erzeugten Satz. Kleine Gleitkommaabweichungen sind möglich. Das allein beweist keine echte mechanische Robustheit.

## 5. Optionale Vorschau erzeugen

Die Referenzinstallation enthielt VTK und Pillow. Mit diesen Bibliotheken in derselben FreeCAD-Python-Laufzeit:

```powershell
& $pingPython .\render_preview.py
```

Die Bilder entstehen unter `build/previews/`. Für einen neu erzeugten Datensatz:

```powershell
& $pingPython .\render_preview.py --artifact-dir .\build --output-dir .\build\neue-ansichten
```

Schriften: standardmäßig Windows Segoe UI, alternativ DejaVu Sans; eigene TTF-Pfade über `PING_FONT_REGULAR` und `PING_FONT_BOLD`. Grafiktreiber, VTK und Schrift beeinflussen die Bildausgabe. Renderings werden nicht als pixelidentisch reproduzierbar behauptet. Die mitgelieferte `PING_FreeCAD_Ansicht.png` ist eine separat aus der echten FreeCAD-GUI gespeicherte Modellansicht; das VTK-Skript erzeugt die vier übrigen Bilder.
