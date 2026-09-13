# Entwurf, Herkunft und Entscheidungen

## Auftrag

Ein schönes, stabiles AirTag-Cover für den Schlüsselbund, druckbar auf einem 3D-Drucker, gerne überraschend oder mit Witz. Schrauben waren erlaubt. Die Konstruktion sollte in FreeCAD entstehen. Anschließend wurde eine öffentliche Dokumentation für die Überprüfung durch Dritte beauftragt.

## Ergebnis

„PING“ ist eine verschraubte Grinse-Kapsel. Die Öse gehört zum Rückteil; eine umlaufende Lippe führt die Front. Zwei seitliche Verschraubungen liegen außerhalb des AirTag-Raums. Augen und Mund sind zugleich Schallöffnungen. Die zweiteilige Bauweise erlaubt zwei Farben ohne Mehrmaterialdruck.

Eine alleinige Schnappverbindung wurde wegen ihrer Abhängigkeit von Material und Drucktoleranz nicht gewählt. Ein umlaufendes gedrucktes Gewinde hätte mehr Bedienraum benötigt. Die verschraubte Lösung ist wartbar, dafür größer und beim Batteriewechsel werkzeugabhängig.

## Herkunft und Werkzeuge

Entwurf am 13.09.2026 im Dialog mit OpenAI Codex. Das native CAD wurde mit FreeCAD 1.1.3 über dessen Python-API konstruiert. Es handelt sich um native Skizzen-/PartDesign-Operationen, keine bloß importierte STL. Die Produktansichten wurden mit VTK/Pillow aus den realen CAD-Körpern gerendert; eine weitere Ansicht direkt in der FreeCAD-GUI.

Die Face-/AirTag-Darstellungen sind keine Hersteller-CAD-Daten. Für den AirTag wurde der von Apple veröffentlichte Hüllzylinder angenommen. PETG und die 0,4-mm-Düse sind Entwurfsannahmen; ein konkreter Drucker wurde nicht festgelegt. Quellen stehen in der Druck-/Montageanleitung.

## Während der Entwicklung behobener Fehler

Die zweidimensionale Vereinigung koplanarer FreeCAD-Flächen hinterließ zunächst mehrere Teilflächen. Die Übernahme allein der ersten Teilfläche in eine Skizze ließ Teile der Öse bzw. Schraubenohren fehlen. Der Fehler wurde durch einen Vergleich mit den erwarteten Außenmaßen erkannt. Das veröffentlichte Makro vereinigt stattdessen kurz extrudierte Körper und übernimmt ihre vollständige Bodenfläche. Zusätzliche Außenmaßprüfungen schützen vor demselben Fehler.

Die Dokumentation erwähnt diesen Befund, damit nachvollziehbar bleibt, warum eine allgemeine „Shape valid“-Prüfung allein nicht ausgereicht hätte. Die veröffentlichten Produktdateien enthalten die korrigierte Kontur.

## Änderungen für die Veröffentlichung

Keine Änderung der Produktgeometrie. Generator-Ausgaben wurden nach `build/` verlegt; Prüf-/Renderprogramme erhielten Eingabe- und Ausgabeoptionen. Lokale Installationspfade wurden durch die dokumentierte FreeCAD-Laufzeit bzw. `FREECAD_LIB` ersetzt. Zusätzlich wurden Exportvergleiche und Dateiintegrität aufgenommen. Interne App-Logs, Backups und private Workspace-Notizen gehören nicht zu diesem Repository.

## Änderungsdisziplin

Bei Varianten Generator und Sollprüfungen bewusst anpassen, neu erzeugen und prüfen. Alte Berichte nicht als Beleg für eine neue Geometrie übernehmen. Gedruckte Testteile möglichst mit Commit-ID, Material und Slicerprofil dokumentieren.
