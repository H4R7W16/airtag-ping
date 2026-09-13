# Prüfmethode und Aussagegrenzen

`verify_model.py` wird mit einer FreeCAD-Python-Laufzeit ausgeführt und öffnet die FCStd-Datei erneut. Es prüft den dokumentierten **Ausgangsentwurf**, kein beliebig geändertes parametrisches Modell. Die Prüfmaße sind bewusst unabhängig vom Generator als Sollwerte hinterlegt.

| Prüfung | Kriterium |
|---|---|
| CAD-Körper | Zwei Bodies; je genau ein gültiger Solid, Volumen > 1000 mm³ |
| Vollständige Rückteilkontur | Breite 50,6 und Höhe 57,0 mm, Toleranz 0,01 mm |
| Hälften | Überschneidungsvolumen < 0,00001 mm³ |
| AirTag-Passraum | Vollständiger Hüllzylinder Ø31,9 × 8,0 mm, von Z=2,4 bis 10,4, kollisionsfrei |
| Schrauben | Zwei vereinfachte Ø2,5×10-Schäfte, Kopf Ø4,5×1,5 mm, kollisionsfrei |
| Muttern | Sechskant SW5×3,8 mm, Z=1 bis 4,8, kollisionsfrei |
| Gewindeeingriff | Nominale axiale Maßkette: 0,6 mm Überstand durch Mutter, Schraubenspitze 0,4 mm innerhalb der Rückseite |
| Beispielring | Geschlossener Torus, Außen-Ø29,2 mm, Draht-Ø2,2 mm, kollisionsfrei |
| STEP | Zwei gültige Solids; beidseitige CAD/STEP-Volumendifferenz jeweils < 0,0001 mm³ |
| STL | Geschlossenes Netz, eine Komponente, Zmin innerhalb 0,0001 mm auf dem Druckbett |
| Exporttreue STL/CAD | Symmetrische Volumendifferenz < 0,3 % und alle sechs Bounding-Box-Grenzen innerhalb 0,05 mm |
| Neuberechnung | Kein Objektstatus mit `Invalid` oder `Error` |

Die STL-Geometrie wird als Volumenkörper rekonstruiert und mit der CAD-Geometrie in Drucklage verglichen. Ein nur geschlossener, aber geometrisch falscher Export reicht damit nicht aus. Die 0,3 % berücksichtigen die Tessellierung; sie sind **keine Fertigungstoleranz**.

Hardware wird vereinfacht geprüft: keine Gewindegeometrie, keine Nylon-Verformung, kein Einschraubmoment und kein detaillierter Splitring-Montagevorgang. Der nominelle Schraubenüberstand ist eine Maßkettenprüfung, kein Test der tatsächlichen Sicherungswirkung. Ein geteilter Ring kann beim Aufziehen mehr Platz benötigen als der modellierte geschlossene Torus.

## Öffentliche Nachweise

- `Pruefbericht.json`: Test auf den veröffentlichten Produktdateien.
- `Reproduktionsbericht.json`: Test auf separaten, frisch aus dem veröffentlichten Makro erzeugten Produktdateien.
- `SHA256SUMS`: Integritätsmanifest der versionierten Projektdateien.
- GitHub-Workflow: prüft das Manifest sowie die Syntax der Python-Programme/des Makros. Er installiert kein FreeCAD und behauptet keine automatische CAD-Prüfung.

Die Berichte stammen aus der Erstellung dieses Projekts. Sie sind nachvollziehbar und erneut ausführbar, aber keine externe Zertifizierung oder unabhängige Laborprüfung.

## Offene physische Validierung

Kein realer Druck, keine Fall-/Zug-/Dauerbelastung, keine FEM, kein Test der Temperaturbeständigkeit, keine Messung des Signaltons oder der Funkfunktion. Materialdaten eines PETG-Filaments übertragen sich nicht automatisch auf den gedruckten Bauteilquerschnitt.

Die [Probedruck-Vorlage](PROBEDRUCK_PROTOKOLL.md) trennt Beobachtungen von Schlussfolgerungen. Änderungen an Material, Druckausrichtung, Schichtbindung, Passung oder Verschraubung erfordern eine erneute praktische Bewertung.
