# PING Trio · drei schlanke AirTag-Cover

![Die drei CAD-Varianten Halo, Komet und Signal](PING_Trio_Uebersicht.png)

**Drei Frontmotive, ein gemeinsames Rückteil.** Die polierte Edelstahl-Batterieabdeckung des AirTags zeigt zur Motivfront und bildet den sichtbaren Metallakzent. Die Vorschau zeigt die gespeicherte CAD-Geometrie; AirTag und Schrauben sind darin vereinfacht dargestellt. Diese Varianten sind digital geprüft, **noch nicht probeweise gedruckt oder belastungsgeprüft**.

## Varianten und Dateien

| Motiv | Wirkung | FreeCAD | Front-STL | STEP | Vorschau |
|---|---|---|---|---|---|
| Halo | Große runde Öffnung als Metallspiegel, feine Bogenrille | [FCStd](CAD/PING_Trio_Halo.FCStd) | [STL](CAD/PING_Trio_Halo_Front.stl) | [STEP](CAD/PING_Trio_Halo.step) | [PNG](CAD/PING_Trio_Halo_Vorschau.png) |
| Komet | Versetzter Metallkern mit drei diagonalen Spuren | [FCStd](CAD/PING_Trio_Komet.FCStd) | [STL](CAD/PING_Trio_Komet_Front.stl) | [STEP](CAD/PING_Trio_Komet.step) | [PNG](CAD/PING_Trio_Komet_Vorschau.png) |
| Signal | Drei gestaffelte Bögen mit Metallglanz | [FCStd](CAD/PING_Trio_Signal.FCStd) | [STL](CAD/PING_Trio_Signal_Front.stl) | [STEP](CAD/PING_Trio_Signal.step) | [PNG](CAD/PING_Trio_Signal_Vorschau.png) |

Für jedes Motiv einmal das [gemeinsame Rückteil](CAD/PING_Trio_Rueckteil.stl) und die jeweilige Front drucken. Der [Generator](CAD_erzeugen.py) erzeugt alle CAD-, STEP- und STL-Dateien neu. Der [Prüfcode](pruefen.py) prüft die gespeicherten Dateien. [Erzeugungsbericht](CAD/Erzeugungsbericht.json) und [Prüfbericht](CAD/Pruefbericht.json) dokumentieren den vorliegenden Stand.

## Maße und Konstruktion

| Merkmal | Trio | Bisheriges PING |
|---|---:|---:|
| Außenmaß des Kunststoffs ohne Ring | 39,6 × 50,7 × 11,0 mm | 50,6 × 57,0 × 12,8 mm |
| Höhe mit M3-Linsenköpfen | ca. 11,65 mm | 12,8 mm mit versenkten M2,5-Köpfen |
| Hauptscheibe | Ø38,4 mm | Ø43,0 mm |
| AirTag-Aufnahme | Ø32,5 × 8,6 mm | Ø32,5 × 8,6 mm |
| Außenkanten der runden Scheiben | Radius 0,45 mm | Fase 0,65 mm |
| Rechnerisches Kunststoffvolumen, je nach Motiv | 6,34–6,67 cm³ | 12,77 cm³ |

Das modellierte Kunststoffvolumen sinkt um **47,8–50,3 %**. Das ist eine CAD-Volumenrechnung, keine gemessene Druckmasse. Die Schraubpunkte liegen diagonal im Rand der Scheibe, statt als seitliche Ohren weit herauszuragen. Die AirTag-Aufnahme behält das bisherige Nennspiel: Ø31,9 × 8,0 mm AirTag-Hüllraum in Ø32,5 × 8,6 mm Aufnahme, also 0,3 mm radial und axial je Seite. Die Front hält den AirTag mit einem umlaufenden Rand fest; eine Zentrierlippe führt die Hälften.

Die runden Außenkanten sind verrundet. Die Ränder der Motivöffnungen sind drucktechnisch bewusst scharf: Sie liegen in der nur 1,2 mm starken Frontfläche und sollen ihre Form behalten. Sichtbare Schnittkanten können nach dem Druck vorsichtig entgratet werden.

## Schrauben und Muttern

Benötigt werden **zwei gleiche M3-Linsenkopfschrauben** mit 8 **oder** 10 mm Länge unter dem Kopf, dazu zwei normale M3-Sechskantmuttern. Die Konstruktion nimmt beide Längen auf. Empfohlen ist **M3×10**, weil die Schraube die Mutter vollständig durchgreift und nominell bündig an der Rückseite endet. M3×8 greift rechnerisch 2,0 mm in eine am Taschenende sitzende 2,4-mm-Mutter; das muss am echten Teil geprüft werden.

| Hardwaremaß | CAD-Annahme |
|---|---:|
| Schraubendurchgang | Ø3,4 mm |
| Kopf (ISO 7380-1 / vergleichbarer Linsenkopf) | Ø≤5,7 mm, Höhe ≤1,65 mm |
| Kopftasche | Ø6,3 × 1,0 mm tief |
| Kopfüberstand bei 1,65 mm Kopfhöhe | 0,65 mm |
| Mutter (DIN 934 / vergleichbar) | SW5,5 mm, Höhe etwa 2,4 mm |
| Mutternfalle | SW5,8 × 4,0 mm tief |
| Gewindeeingriff M3×8, Mutter am Taschenende | 2,0 mm |
| Schraubenende M3×10 | bündig zur Rückseite, ohne Toleranzreserve |

**Keine Senkkopfschrauben und keine M3-Sicherungsmuttern ohne erneute Maßprüfung verwenden.** Die Taschen sind auf normale Sechskantmuttern ausgelegt. Ein selbstsichernder Nylonring wird mit M3×8 nicht vollständig erreicht. Da normale Muttern sich lockern können, die Verschraubung am realen Schlüsselbund regelmäßig kontrollieren. Bei abweichenden Schraubenköpfen oder Muttern die Teile zuerst messen; insbesondere M3×10 hat am Rücken keine zusätzliche Längenreserve.

## Drucken und montieren

1. Beide STLs in Millimetern bei 100 % importieren. Sie liegen mit der flachen Außenseite auf **Z=0** und der offenen Innenseite nach oben. PETG mit 0,4-mm-Düse und 0,20-mm-Schichten ist der konstruktive Ausgangspunkt. Für die 1,2-mm-Flächen mindestens sechs geschlossene Schichten vorsehen. Die Öse und die Schraubpunkte in der Schichtvorschau prüfen; ein konkretes Druckerprofil ist noch nicht erprobt.
2. Die Teile entgraten. Die zwei M3-Muttern von hinten in die Sechskanttaschen bis an deren Dach drücken. Front und Rückteil ohne AirTag probeweise zusammenfügen. Die Zentrierlippe muss leicht hineingehen, ohne die Fuge offen zu halten.
3. Den AirTag mit der **polierten Edelstahlseite zur Motivfront** einlegen. Die drei kleinen Öffnungen im Rückteil zeigen zur weißen Seite. Bei klapperndem Sitz allenfalls eine dünne weiche Auflage ausprobieren und danach prüfen, ob die Hälften vollständig schließen.
4. Zwei gleich lange M3-Schrauben von vorne abwechselnd handfest anziehen. Die Köpfe stehen nominell 0,65 mm über der Front. M3×10 muss am Rücken bündig bleiben; M3×8 muss sicher in beiden Muttern greifen. Keinesfalls durch stärkeres Anziehen eine offene Fuge erzwingen.
5. Einen Schlüsselring durch Ø6,5 mm Ösenloch führen. Danach Sitz, Lockerung, AirTag-Erkennung, Signalton und gegebenenfalls Präzisionssuche am eigenen Gerät prüfen. Vor dem täglichen Einsatz einen Probedruck mit Dummy und Belastungsprobe der Öse machen.

Die Metallseite bleibt durch die Motivöffnungen berührbar und kann verkratzen. Das Gehäuse ist nicht dicht. Akustik, Funk, Passung, Verschleiß der Öse und Dauerfestigkeit sind noch nicht physisch gemessen.

## Reproduktion und Bearbeitung

Getestet mit **FreeCAD 1.0.1** und dessen gebündeltem Python unter Windows:

```powershell
& 'C:\Program Files\FreeCAD 1.0\bin\python.exe' .\trio\CAD_erzeugen.py
& 'C:\Program Files\FreeCAD 1.0\bin\python.exe' .\trio\pruefen.py
& 'C:\Program Files\FreeCAD 1.0\bin\python.exe' .\trio\rendern.py
python .\verify_files.py
```

Die FCStd-Dateien enthalten pro Variante zwei native FreeCAD-Bodies und eine Maßtabelle. Die Körper sind durch den Python-Generator erzeugte `PartDesign::Feature`-Volumenkörper. **Die Maßtabelle steuert die Geometrie nicht automatisch**; für Änderungen an Durchmessern, Motiven oder Schraubentyp den Generator anpassen und CAD, STLs, STEP, Prüfung und Prüfsummen neu erzeugen. Das bisherige PING im Repository bleibt als eigener Stand erhalten.

## Quellen und Annahmen

- Apple nennt für AirTag und AirTag (2. Generation) jeweils Ø31,9 × 8,0 mm: [AirTag](https://support.apple.com/en-ca/111847), [AirTag 2](https://support.apple.com/de-de/126203). Apple bezeichnet den Batteriedeckel als polierten Edelstahl: [Batteriewechsel](https://support.apple.com/en-us/102600).
- Die für den Entwurf angesetzten M3-Linsenkopfmaße Ø5,7 / H1,65 mm stammen aus dem [ISO-7380-1-Datenblatt von Böllhoff](https://eshop-ro.boellhoff.com/out/media/pdf/ISO_7380-1_Stahl_10.9_Innensechskant___en.pdf).
- Für die normale M3-Sechskantmutter werden SW5,5 mm und H2,4 mm aus dem [DIN-934-Datenblatt von Böllhoff](https://eshop-ro.boellhoff.com/out/media/pdf/DIN_934_Messing_ni___en.pdf) angesetzt. Tatsächliche Lieferteile können abweichen.
- Die 0,4-mm-Düse, PETG, alle Spielmaße, Ösen- und Motivgeometrie sind eigene konstruktive Festlegungen; es gibt keinen mechanischen Sicherheitsnachweis.
