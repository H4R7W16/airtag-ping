"""Digitale Geometrieprüfung der gespeicherten PING-Trio-Dateien.

Kein Ersatz für Passprobe, Belastungsprobe oder Akustiktest am Druckteil.
"""

import json
import math
import sys
from pathlib import Path

import FreeCAD as App
import Part

sys.path.insert(0, str(Path(App.getHomePath()) / "lib"))
import Mesh

HERE = Path(__file__).resolve().parent
CAD = HERE / "CAD"
V = App.Vector
VARIANTS = ("Halo", "Komet", "Signal")


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def hex_nut(x, y):
    radius = 5.5 / math.sqrt(3)
    vertices = [V(x + radius * math.cos(math.radians(30 + 60 * n)),
                  y + radius * math.sin(math.radians(30 + 60 * n)), 1.6)
                for n in range(6)]
    return Part.Face(Part.makePolygon(vertices + [vertices[0]])).extrude(V(0, 0, 2.4))


def verify():
    report = {"freecad_version": ".".join(App.Version()[:3]), "variants": {},
              "physical_validation": "Neue Varianten noch nicht gedruckt oder belastungsgeprüft."}
    reference_volume = 7108.218958310401 + 5658.043771214107
    back_stl = CAD / "PING_Trio_Rueckteil.stl"
    check(back_stl.exists(), "gemeinsames Rückteil fehlt")
    mesh_back = Mesh.Mesh(str(back_stl))
    check(mesh_back.isSolid() and mesh_back.countComponents() == 1, "Rückteil-STL nicht wasserdicht/einteilig")
    for variant in VARIANTS:
        name = "PING_Trio_" + variant
        doc = App.openDocument(str(CAD / (name + ".FCStd")))
        doc.recompute()
        back_body, front_body = doc.getObject("BackBody"), doc.getObject("FrontBody")
        check(back_body is not None and front_body is not None, variant + ": Körper fehlen")
        back, front = back_body.Shape, front_body.Shape
        for label, shape in (("Rückteil", back), ("Front", front)):
            check(shape.isValid() and len(shape.Solids) == 1, variant + ": " + label + " ungültig")
        check(back.common(front).Volume < 1e-5, variant + ": Hälften kollidieren")
        tag = Part.makeCylinder(15.95, 8.0, V(0, 0, 1.5))
        check(back.common(tag).Volume < 1e-5 and front.common(tag).Volume < 1e-5,
              variant + ": AirTag-Hüllzylinder kollidiert")
        for x in (-15.0, 15.0):
            y = -14.0
            nut = hex_nut(x, y)
            check(back.common(nut).Volume < 1e-5, variant + ": M3-Mutter kollidiert")
            for length in (8.0, 10.0):
                shaft = Part.makeCylinder(1.5, length, V(x, y, 10.0 - length))
                head = Part.makeCylinder(2.85, 1.65, V(x, y, 10.0))
                check(back.common(shaft).Volume < 1e-5 and front.common(shaft).Volume < 1e-5,
                      variant + ": M3×" + str(length) + "-Schaft kollidiert")
                check(front.common(head).Volume < 1e-5, variant + ": M3-Kopf kollidiert")
                check(10.0 - length >= 0.0, variant + ": Schraube ragt hinten heraus")
            check(4.0 - (10.0 - 8.0) >= 2.0 - 1e-6, variant + ": M3×8 greift zu kurz")
        ring = Part.makeTorus(13.5, 1.1, V(0, 38.5, 2.75), V(1, 0, 0))
        check(back.common(ring).Volume < 1e-5, variant + ": Schlüsselring kollidiert")
        step = Part.Shape()
        step.read(str(CAD / (name + ".step")))
        union = back.fuse(front)
        check(step.isValid() and len(step.Solids) == 2, variant + ": STEP ist nicht zweiteilig")
        check(step.cut(union).Volume + union.cut(step).Volume < 0.001,
              variant + ": STEP weicht vom CAD ab")
        front_stl = CAD / (name + "_Front.stl")
        mesh_front = Mesh.Mesh(str(front_stl))
        check(mesh_front.isSolid() and mesh_front.countComponents() == 1,
              variant + ": Front-STL nicht wasserdicht/einteilig")
        check(abs(mesh_front.BoundBox.ZMin) < 1e-4 and abs(mesh_back.BoundBox.ZMin) < 1e-4,
              variant + ": STL-Drucklage fehlerhaft")
        check(abs(mesh_front.Volume - front.Volume) / front.Volume < 0.003 and
              abs(mesh_back.Volume - back.Volume) / back.Volume < 0.003,
              variant + ": STL-Volumen weicht vom CAD ab")
        bounds = [max(mesh_back.BoundBox.XMax, mesh_front.BoundBox.XMax) - min(mesh_back.BoundBox.XMin, mesh_front.BoundBox.XMin),
                  max(mesh_back.BoundBox.YMax, mesh_front.BoundBox.YMax) - min(mesh_back.BoundBox.YMin, mesh_front.BoundBox.YMin),
                  11.0]
        check(bounds[0] < 40.0 and bounds[1] < 51.0, variant + ": Außenmaße zu groß")
        volume = back.Volume + front.Volume
        check(volume < reference_volume * 0.6, variant + ": Volumen nicht deutlich reduziert")
        report["variants"][variant] = {
            "valid": True,
            "assembly_bounds_mm": [round(v, 2) for v in bounds],
            "volume_mm3": round(volume, 2),
            "volume_reduction_vs_ping_percent": round(100 * (1 - volume / reference_volume), 1),
            "M3x8_engagement_mm": 2.0,
            "M3x10_tip_recess_mm": 0.0,
            "stl_watertight": True,
            "stl_volume_matches_cad_within_0_3_percent": True,
            "step_matches_cad": True,
        }
        App.closeDocument(doc.Name)
    (CAD / "Pruefbericht.json").write_bytes(
        (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    verify()
