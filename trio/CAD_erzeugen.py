"""PING Trio: zweiteiliges AirTag-Cover in sechs Frontmotiven.

Mit der Python-Laufzeit von FreeCAD ausführen. Alle Maße sind Millimeter.
Die STEP-Dateien zeigen die Montage; die STL-Dateien liegen auf dem Druckbett.
"""

import json
import math
from pathlib import Path

import FreeCAD as App
import MeshPart
import Part


HERE = Path(__file__).resolve().parent
OUT = HERE / "CAD"
OUT.mkdir(exist_ok=True)
V = App.Vector

# Geometrie und Hardware. Die Oberfläche der Metallkappe zeigt zur Motivfront.
TAG_D = 31.9
TAG_H = 8.0
CAVITY_D = 32.5
HALF_H = 5.5
FLOOR = 1.2
DISC_R = 19.2
EDGE_R = 0.45
SCREWS = ((-15.0, -14.0), (15.0, -14.0))
SCREW_BORE_R = 1.7
HEAD_POCKET_R = 3.15
HEAD_POCKET_DEPTH = {8: 2.4, 10: 1.0}
HEAD_HEIGHT = 3.0
NUT_AF = 5.8
NUT_ROOF_Z = 4.0
MOTIFS = ("Halo", "Komet", "Signal", "Herzaugen", "Schock", "Peek")
SCREW_LENGTHS = (8, 10)


def cylinder(radius, height, x=0, y=0, z=0):
    return Part.makeCylinder(radius, height, V(x, y, z))


def rounded_disk(radius, height, x=0, y=0, z=0):
    shape = cylinder(radius, height, x, y, z)
    rims = [edge for edge in shape.Edges if edge.BoundBox.ZLength < 1e-6]
    return shape.makeFillet(EDGE_R, rims)


def polygon(points, z, height):
    vertices = [V(x, y, z) for x, y in points]
    return Part.Face(Part.makePolygon(vertices + [vertices[0]])).extrude(V(0, 0, height))


def capsule(start, end, radius, z, height):
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    nx, ny = -dy * radius / length, dx * radius / length
    corners = [
        (start[0] + nx, start[1] + ny),
        (end[0] + nx, end[1] + ny),
        (end[0] - nx, end[1] - ny),
        (start[0] - nx, start[1] - ny),
    ]
    return polygon(corners, z, height).multiFuse(
        [cylinder(radius, height, *start, z), cylinder(radius, height, *end, z)]
    ).removeSplitter()


def arc_window(radius, width, begin, end, z, height):
    """Ringsegment mit runden Enden, Winkel in Grad."""
    steps = max(12, int((end - begin) / 5))
    angles = [math.radians(begin + (end - begin) * i / steps) for i in range(steps + 1)]
    outer = [(math.cos(a) * (radius + width / 2), math.sin(a) * (radius + width / 2)) for a in angles]
    inner = [(math.cos(a) * (radius - width / 2), math.sin(a) * (radius - width / 2)) for a in reversed(angles)]
    a, b = angles[0], angles[-1]
    ends = [cylinder(width / 2, height, radius * math.cos(t), radius * math.sin(t), z) for t in (a, b)]
    return polygon(outer + inner, z, height).multiFuse(ends).removeSplitter()


def ellipse(x, y, rx, ry, z, height):
    points = [(x + rx * math.cos(2 * math.pi * i / 64),
               y + ry * math.sin(2 * math.pi * i / 64)) for i in range(64)]
    return polygon(points, z, height)


def heart(x, y, z, height, scale=0.17):
    # Klassische Herzkurve als geschlossene, druckbare Metallöffnung.
    points = []
    for i in range(96):
        t = 2 * math.pi * i / 96
        hx = 16 * math.sin(t) ** 3
        hy = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        points.append((x + scale * hx, y + scale * hy))
    return polygon(points, z, height)


def hex_trap(x, y, z, height):
    radius = NUT_AF / math.sqrt(3)
    points = [(x + radius * math.cos(math.radians(30 + n * 60)),
               y + radius * math.sin(math.radians(30 + n * 60))) for n in range(6)]
    return polygon(points, z, height)


def outer(with_lug, motif=None):
    pieces = [rounded_disk(DISC_R, HALF_H)]
    pieces += [rounded_disk(4.8, HALF_H, x, y) for x, y in SCREWS]
    if motif in ("Schock", "Peek"):
        # Die beiden Hände prägen die Außenkontur statt nur Striche auf der Scheibe.
        hand_y = -3.0 if motif == "Schock" else -4.0
        pieces += [rounded_disk(4.4, HALF_H, x, hand_y) for x in (-17.4, 17.4)]
    if with_lug:
        pieces += [polygon([(-8, 14), (8, 14), (5.8, 25), (-5.8, 25)], 0, HALF_H),
                   rounded_disk(6.5, HALF_H, 0, 25)]
    return pieces[0].multiFuse(pieces[1:]).removeSplitter()


def back_shape():
    shape = outer(True)
    shape = shape.cut(cylinder(CAVITY_D / 2, HALF_H - FLOOR + 0.1, z=FLOOR))
    lip = cylinder(17.35, 0.8, z=HALF_H).cut(cylinder(CAVITY_D / 2, 1.0, z=HALF_H - 0.1))
    shape = shape.fuse(lip).removeSplitter()
    shape = shape.cut(cylinder(3.25, HALF_H + 0.2, 0, 25, -0.1))
    for x, y in SCREWS:
        shape = shape.cut(cylinder(SCREW_BORE_R, HALF_H + 0.2, x, y, -0.1))
        shape = shape.cut(hex_trap(x, y, -0.1, NUT_ROOF_Z + 0.1))
    # Drei kleine Öffnungen auf der weißen Seite helfen bei Schall und Gewicht.
    for angle in (30, 150, 270):
        a = math.radians(angle)
        start = (5.2 * math.cos(a), 5.2 * math.sin(a))
        end = (9.5 * math.cos(a), 9.5 * math.sin(a))
        shape = shape.cut(capsule(start, end, 0.9, -0.1, FLOOR + 0.2))
    return shape.removeSplitter()


def motif_cutters(name):
    z, h = -0.1, FLOOR + 0.2
    if name == "Halo":
        # Die Metallkappe bildet die runde, spiegelnde Mitte.
        return [cylinder(11.3, h, z=z), arc_window(14.1, 0.85, 28, 152, z, 0.38)]
    if name == "Komet":
        # Versetzter Metallkern mit drei diagonal auslaufenden Lichtspuren.
        return [cylinder(5.4, h, 5.0, 4.0, z),
                capsule((-3.0, 2.0), (-9.0, -1.0), 0.9, z, h),
                capsule((-2.0, -2.0), (-10.0, -5.0), 0.8, z, h),
                capsule((-1.0, -5.0), (-8.0, -9.0), 0.7, z, h)]
    if name == "Signal":
        # Drei gestaffelte Bögen: je nach Blickwinkel blitzt das Metall auf.
        return [arc_window(4.3, 1.8, 25, 155, z, h),
                arc_window(8.1, 1.9, 20, 160, z, h),
                arc_window(12.0, 2.0, 15, 165, z, h),
                cylinder(1.65, h, 0, -4.0, z)]
    if name == "Herzaugen":
        return [heart(-5.7, 6.0, z, h, 0.07), heart(5.7, 6.0, z, h, 0.07),
                arc_window(8.1, 3.4, 205, 335, z, h)]
    if name == "Schock":
        return [ellipse(-5.2, 5.1, 2.5, 3.1, z, h),
                ellipse(5.2, 5.1, 2.5, 3.1, z, h),
                ellipse(0, -4.3, 3.4, 5.2, z, h)]
    if name == "Peek":
        return [cylinder(2.2, h, 6.3, 5.6, z),
                capsule((-8.8, 6.5), (-0.3, 3.5), 0.85, z, h),
                capsule((-9.5, 3.1), (1.8, 0.6), 0.85, z, h),
                capsule((-8.5, -0.7), (2.5, -3.4), 0.8, z, h),
                capsule((-6.5, -4.6), (2.0, -7.4), 0.75, z, h),
                capsule((4.1, -5.2), (6.0, -5.8), 0.55, z, h)]
    raise ValueError(name)


def decoration(name):
    """Flache Farbmasken: bündig für Multimaterialdruck, als Vertiefung auch einfarbig lesbar."""
    z, h = 0, 0.4
    if name == "Herzaugen":
        rings = [heart(x, 6.0, z, h, 0.225).cut(heart(x, 6.0, -0.1, h + 0.2, 0.07))
                 for x in (-5.7, 5.7)]
        return {"Rot": Part.makeCompound(rings)}
    if name == "Schock":
        hands = []
        for side in (-1, 1):
            hand = [cylinder(3.5, h, side * 17.1, -3.6, z)]
            hand += [capsule((side * (18.3 - i * 1.35), -1.1),
                             (side * (17.0 - i * 1.55), 4.0 + (1 if i == 2 else 0)),
                             0.85, z, h) for i in range(4)]
            hands.append(hand[0].multiFuse(hand[1:]).removeSplitter())
        blue = ellipse(0, 12.4, 11.2, 2.9, z, h)
        return {"Orange": Part.makeCompound(hands), "Blau": blue}
    if name == "Peek":
        left = [cylinder(3.9, h, -14.2, -5.2, z)]
        left += [capsule((-12.0, y0), (x1, y1), 1.25, z, h)
                 for y0, x1, y1 in ((0.5, 0.3, 7.3), (-1.8, 1.8, 3.3),
                                    (-4.0, 2.3, -0.8), (-6.3, 2.1, -4.6))]
        right = [cylinder(3.7, h, 14.0, -5.3, z),
                 capsule((12.5, -2.0), (6.3, -0.3), 1.2, z, h),
                 capsule((11.5, -4.4), (4.3, -3.3), 1.2, z, h),
                 capsule((11.2, -6.4), (5.1, -6.3), 1.15, z, h)]
        hands = Part.makeCompound([left[0].multiFuse(left[1:]).removeSplitter(),
                                   right[0].multiFuse(right[1:]).removeSplitter()])
        return {"Ocker": hands}
    return {}


def fitted_decoration(name):
    """Farbkörper auf den Umriss begrenzen und Metallfenster offen lassen."""
    result = {}
    boundary = outer(False, name)
    for color, raw in decoration(name).items():
        shape = raw.common(boundary)
        for window in motif_cutters(name):
            shape = shape.cut(window)
        result[color] = shape.removeSplitter()
    return result


def front_shape(name, screw_length):
    shape = outer(False, name)
    shape = shape.cut(cylinder(CAVITY_D / 2, HALF_H - FLOOR + 0.1, z=FLOOR))
    shape = shape.cut(cylinder(17.65, 1.05, z=HALF_H - 0.95))
    for x, y in SCREWS:
        shape = shape.cut(cylinder(SCREW_BORE_R, HALF_H + 0.2, x, y, -0.1))
        shape = shape.cut(cylinder(HEAD_POCKET_R, HEAD_POCKET_DEPTH[screw_length] + 0.1, x, y, -0.1))
    for cutter in motif_cutters(name):
        shape = shape.cut(cutter)
    for mask in fitted_decoration(name).values():
        shape = shape.cut(mask)
    return shape.removeSplitter()


def add_piece(doc, name, label, shape, color):
    body = doc.addObject("PartDesign::Body", name)
    body.Label = label
    feature = body.newObject("PartDesign::Feature", name + "Solid")
    feature.Label = label + " · erzeugte Volumengeometrie"
    feature.Shape = shape
    body.Tip = feature
    if feature.ViewObject is not None:
        feature.ViewObject.ShapeColor = color
        feature.ViewObject.LineColor = (0.10, 0.12, 0.15)
        feature.ViewObject.DisplayMode = "Flat Lines"
    return body


def export_mesh(shape, path):
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.05,
                                  AngularDeflection=0.15, Relative=False)
    mesh.write(str(path))
    return mesh


def build():
    back = back_shape()
    assert back.isValid() and len(back.Solids) == 1
    back_mesh = export_mesh(back, OUT / "PING_Trio_Rueckteil.stl")
    results = {"freecad_version": ".".join(App.Version()[:3]), "variants": {}}
    for name in MOTIFS:
      masks = fitted_decoration(name)
      for color, mask in masks.items():
        assert mask.isValid() and all(solid.Volume > 0 for solid in mask.Solids), (name, color)
        export_mesh(mask, OUT / ("PING_Trio_" + name + "_" + color + "_Farbmaske.stl"))
      for screw_length in SCREW_LENGTHS:
        front = front_shape(name, screw_length)
        assert front.isValid() and len(front.Solids) == 1, (name, screw_length)
        doc_name = "PING_" + name + "_M3x" + str(screw_length)
        doc = App.newDocument(doc_name)
        doc.Label = "PING Trio · " + name + " · M3×" + str(screw_length)
        doc.Comment = "Druckprototyp: AirTag-Metallseite zur Motivfront; Passung und Belastung real prüfen."
        sheet = doc.addObject("Spreadsheet::Sheet", "Parameters")
        sheet.Label = "Nennmaße · Erzeugercode ist maßgeblich"
        for row, (key, value) in enumerate([
            ("AirTag Ø", TAG_D), ("AirTag Höhe", TAG_H), ("Aufnahme Ø", CAVITY_D),
            ("Höhe je Schale", HALF_H), ("Bodenstärke", FLOOR),
            ("Hauptscheibe Ø", 2 * DISC_R), ("M3 Durchgang Ø", 2 * SCREW_BORE_R),
            ("M3 Kopf-Tasche Ø", 2 * HEAD_POCKET_R), ("M3 Kopf-Höhe", HEAD_HEIGHT),
            ("M3 Kopf-Tasche Tiefe", HEAD_POCKET_DEPTH[screw_length]),
            ("M3 Mutter SW", NUT_AF),
            ("Schraubenlänge", "M3×" + str(screw_length))], 1):
            sheet.set("A" + str(row), key)
            sheet.set("B" + str(row), str(value))
        back_body = add_piece(doc, "BackBody", "Rückteil · universell", back, (0.08, 0.20, 0.25))
        face_color = (0.95, 0.70, 0.13) if name in ("Herzaugen", "Schock", "Peek") else (0.92, 0.36, 0.21)
        front_body = add_piece(doc, "FrontBody", "Front · " + name, front, face_color)
        front_body.Placement = App.Placement(V(0, 0, 2 * HALF_H), App.Rotation(V(0, 1, 0), 180))
        for color, mask in masks.items():
            guide = doc.addObject("Part::Feature", "ColorMask_" + color)
            guide.Label = "Optionale Farbmaske · " + color
            guide.Shape = mask
            guide.Placement = front_body.Placement
            if guide.ViewObject is not None:
                guide.ViewObject.Visibility = False
        doc.recompute()
        file_base = "PING_Trio_" + name + ("" if screw_length == 8 else "_M3x10")
        doc.saveAs(str(OUT / (file_base + ".FCStd")))
        Part.export([back_body, front_body], str(OUT / (file_base + ".step")))
        front_mesh = export_mesh(front, OUT / (file_base + "_Front.stl"))
        bounds = [
            max(back_mesh.BoundBox.XMax, front_mesh.BoundBox.XMax) - min(back_mesh.BoundBox.XMin, front_mesh.BoundBox.XMin),
            max(back_mesh.BoundBox.YMax, front_mesh.BoundBox.YMax) - min(back_mesh.BoundBox.YMin, front_mesh.BoundBox.YMin),
            2 * HALF_H,
        ]
        results["variants"][name + "_M3x" + str(screw_length)] = {
            "back_volume_mm3": round(back.Volume, 2),
            "front_volume_mm3": round(front.Volume, 2),
            "assembly_bounds_mm": [round(dimension, 2) for dimension in bounds],
            "head_projection_mm": round(HEAD_HEIGHT - HEAD_POCKET_DEPTH[screw_length], 2),
        }
        App.closeDocument(doc.Name)
    (OUT / "Erzeugungsbericht.json").write_bytes(
        (json.dumps(results, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build()
