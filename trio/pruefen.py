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
VARIANTS = ("Halo", "Komet", "Signal", "Herzaugen", "Schock", "Peek")
SCREW_LENGTHS = (8, 10)
HEAD_POCKET_DEPTH = {8: 2.4, 10: 1.0}
MASKS = {"Herzaugen": ("Rot",), "Schock": ("Orange", "Blau"), "Peek": ("Ocker",)}


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
      for screw_length in SCREW_LENGTHS:
        key = variant + "_M3x" + str(screw_length)
        name = "PING_Trio_" + variant + ("" if screw_length == 8 else "_M3x10")
        doc = App.openDocument(str(CAD / (name + ".FCStd")))
        doc.recompute()
        back_body, front_body = doc.getObject("BackBody"), doc.getObject("FrontBody")
        check(back_body is not None and front_body is not None, key + ": Körper fehlen")
        back, front = back_body.Shape, front_body.Shape
        for label, shape in (("Rückteil", back), ("Front", front)):
            check(shape.isValid() and len(shape.Solids) == 1, key + ": " + label + " ungültig")
        check(back.common(front).Volume < 1e-5, key + ": Hälften kollidieren")
        tag = Part.makeCylinder(15.95, 8.0, V(0, 0, 1.5))
        check(back.common(tag).Volume < 1e-5 and front.common(tag).Volume < 1e-5,
              key + ": AirTag-Hüllzylinder kollidiert")
        for x in (-15.0, 15.0):
            y = -14.0
            nut = hex_nut(x, y)
            check(back.common(nut).Volume < 1e-5, key + ": M3-Mutter kollidiert")
            head_underside = 11.0 - HEAD_POCKET_DEPTH[screw_length]
            tip_z = head_underside - screw_length
            shaft = Part.makeCylinder(1.5, screw_length, V(x, y, tip_z))
            head = Part.makeCylinder(2.75, 3.0, V(x, y, head_underside))
            check(back.common(shaft).Volume < 1e-5 and front.common(shaft).Volume < 1e-5,
                  key + ": M3-Schaft kollidiert")
            check(front.common(head).Volume < 1e-5, key + ": Zylinderkopf kollidiert")
            check(tip_z >= -1e-6, key + ": Schraube ragt hinten heraus")
            check(tip_z <= 1.6, key + ": Schraube durchgreift Mutter nicht")
        ring = Part.makeTorus(13.5, 1.1, V(0, 38.5, 2.75), V(1, 0, 0))
        check(back.common(ring).Volume < 1e-5, key + ": Schlüsselring kollidiert")
        step = Part.Shape()
        step.read(str(CAD / (name + ".step")))
        union = back.fuse(front)
        check(step.isValid() and len(step.Solids) == 2, key + ": STEP ist nicht zweiteilig")
        check(step.cut(union).Volume + union.cut(step).Volume < 0.001,
              key + ": STEP weicht vom CAD ab")
        front_stl = CAD / (name + "_Front.stl")
        mesh_front = Mesh.Mesh(str(front_stl))
        check(mesh_front.isSolid() and mesh_front.countComponents() == 1,
              key + ": Front-STL nicht wasserdicht/einteilig")
        check(abs(mesh_front.BoundBox.ZMin) < 1e-4 and abs(mesh_back.BoundBox.ZMin) < 1e-4,
              key + ": STL-Drucklage fehlerhaft")
        check(abs(mesh_front.Volume - front.Volume) / front.Volume < 0.003 and
              abs(mesh_back.Volume - back.Volume) / back.Volume < 0.003,
              key + ": STL-Volumen weicht vom CAD ab")
        bounds = [max(mesh_back.BoundBox.XMax, mesh_front.BoundBox.XMax) - min(mesh_back.BoundBox.XMin, mesh_front.BoundBox.XMin),
                  max(mesh_back.BoundBox.YMax, mesh_front.BoundBox.YMax) - min(mesh_back.BoundBox.YMin, mesh_front.BoundBox.YMin),
                  11.0]
        check(bounds[0] < 44.0 and bounds[1] < 51.0, key + ": Außenmaße zu groß")
        combined_front = front
        for color in MASKS.get(variant, ()):
            mask = doc.getObject("ColorMask_" + color)
            check(mask is not None and mask.Shape.isValid() and mask.Shape.Volume > 0,
                  key + ": Farbmaske " + color + " fehlt/ist ungültig")
            check(front.common(mask.Shape).Volume < 1e-5,
                  key + ": Farbmaske " + color + " kollidiert mit der Front")
            mask_mesh = Mesh.Mesh(str(CAD / ("PING_Trio_" + variant + "_" + color + "_Farbmaske.stl")))
            check(mask_mesh.isSolid(), key + ": Farbmaske " + color + " nicht wasserdicht")
            check(abs(mask_mesh.Volume - mask.Shape.Volume) / mask.Shape.Volume < 0.003,
                  key + ": Farbmasken-STL weicht vom CAD ab")
            combined_front = combined_front.fuse(mask.Shape)
        check(combined_front.isValid() and len(combined_front.Solids) == 1,
              key + ": Front und Farbmasken bilden keinen geschlossenen Körper")
        volume = back.Volume + front.Volume
        check(volume < reference_volume * 0.6, key + ": Volumen nicht deutlich reduziert")
        report["variants"][key] = {
            "valid": True,
            "assembly_bounds_mm": [round(v, 2) for v in bounds],
            "volume_mm3": round(volume, 2),
            "volume_reduction_vs_ping_percent": round(100 * (1 - volume / reference_volume), 1),
            "screw_length_mm": screw_length,
            "head_projection_mm": round(3.0 - HEAD_POCKET_DEPTH[screw_length], 2),
            "tip_recess_mm": round(tip_z, 2),
            "nut_thread_engagement_mm": 2.4,
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
