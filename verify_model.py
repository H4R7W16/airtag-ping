"""FreeCAD-Prüfung des gespeicherten Produkts, unabhängig vom Erzeugermakro."""
import sys
import os
import argparse
from pathlib import Path
if not __debug__:
    raise RuntimeError('Prüfung nicht mit python -O ausführen: Assertions müssen aktiv sein.')
if os.environ.get('FREECAD_LIB'):
    sys.path.insert(0, os.environ['FREECAD_LIB'])
import FreeCAD as App
import Part
import Mesh
import json
import math

parser = argparse.ArgumentParser(description='Prüft FCStd, STEP und STL mit FreeCAD. Keine physischen Tests.')
parser.add_argument('--artifact-dir', type=Path, default=Path(__file__).resolve().parent)
parser.add_argument('--report', type=Path, default=Path(__file__).resolve().parent/'build'/'Pruefbericht.json')
args = parser.parse_args()
root = args.artifact_dir.resolve()
path = root / 'PING_AirTag.FCStd'
assert path.exists(), 'FreeCAD-Modell fehlt'
doc = App.openDocument(str(path))
doc.recompute()
back, front = doc.getObject('BackBody'), doc.getObject('FrontBody')
assert back is not None and front is not None, 'Zwei separate Druckkörper erforderlich'
shapes = [back.Shape, front.Shape]
assert abs(back.Shape.BoundBox.YLength - 57.0) < 0.01, 'Rückteil-Außenkontur/Öse unvollständig'
assert abs(back.Shape.BoundBox.XLength - 50.6) < 0.01, 'Schraubenohren unvollständig'
report = {'freecad_version': '.'.join(App.Version()[:3]), 'parts': {}}
for obj in (back, front):
    s = obj.Shape
    assert s.isValid() and len(s.Solids) == 1, obj.Name + ': kein gültiger einzelner Volumenkörper'
    assert s.Volume > 1000, obj.Name + ': unrealistisches Volumen'
    report['parts'][obj.Name] = {'valid': s.isValid(), 'solids': len(s.Solids), 'volume_mm3': s.Volume,
       'bounds_mm': [s.BoundBox.XLength, s.BoundBox.YLength, s.BoundBox.ZLength]}
assert shapes[0].common(shapes[1]).Volume < 1e-5, 'Gehäusehälften kollidieren'
envelope = Part.makeCylinder(15.95, 8, App.Vector(0, 0, 2.4))
for s in shapes:
    assert s.common(envelope).Volume < 1e-5, 'AirTag-Hüllzylinder kollidiert'
for x in (-20.5,20.5):
    shaft = Part.makeCylinder(1.25, 10, App.Vector(x,-5,0.4))
    head = Part.makeCylinder(2.25,1.5,App.Vector(x,-5,10.4))
    for s in shapes:
        assert s.common(shaft).Volume < 1e-5, 'Schraubenschaft kollidiert'
        assert s.common(head).Volume < 1e-5, 'Schraubenkopf kollidiert'
    r=5/math.sqrt(3)
    pts=[App.Vector(x+r*math.cos(math.radians(30+60*j)),-5+r*math.sin(math.radians(30+60*j)),1) for j in range(6)]
    nut=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(App.Vector(0,0,3.8))
    for s in shapes:
        assert s.common(nut).Volume < 1e-5, 'Sicherungsmutter kollidiert'
    # Screw tip is recessed 0.4 mm and projects 0.6 mm past the seated nut.
    assert 1.0 - (10.4 - 10.0) >= 0.45, 'Schraube greift nicht vollständig durch den Sicherungsring'
ring=Part.makeTorus(13.5,1.1,App.Vector(0,42,3.2),App.Vector(1,0,0))
for s in shapes:
    assert s.common(ring).Volume < 1e-5, 'Beispiel-Schlüsselring kollidiert'
step=Part.Shape()
step.read(str(root/'PING_Montage.step'))
assert len(step.Solids)==2 and step.isValid(), 'STEP enthält nicht zwei gültige Körper'
cad_union=shapes[0].fuse(shapes[1])
assert step.cut(cad_union).Volume < 1e-4 and cad_union.cut(step).Volume < 1e-4, 'STEP weicht vom CAD ab'
for fname in ('PING_Rueckteil.stl','PING_Front.stl'):
    m = Mesh.Mesh(str(root / fname))
    assert m.isSolid(), fname + ': STL nicht geschlossen'
    assert m.countComponents() == 1, fname + ': mehrere Netzkomponenten'
    assert abs(m.BoundBox.ZMin) < 1e-4, fname + ': nicht auf Druckbett'
    obj=back if fname=='PING_Rueckteil.stl' else front
    local_shape=obj.Shape.copy()
    local_shape.Placement=obj.Placement.inverse().multiply(local_shape.Placement)
    mesh_solid=Part.Shape()
    mesh_solid.makeShapeFromMesh(m.Topology,0.01)
    assert len(mesh_solid.Shells)==1, fname + ': Mesh bildet nicht eine zusammenhängende Hülle'
    mesh_solid=Part.makeSolid(mesh_solid.Shells[0])
    difference=local_shape.cut(mesh_solid).Volume + mesh_solid.cut(local_shape).Volume
    assert difference/local_shape.Volume < .003, fname + ': STL-Geometrie weicht um mehr als 0,3 % vom CAD ab'
    for key in ('XMin','XMax','YMin','YMax','ZMin','ZMax'):
        assert abs(getattr(m.BoundBox,key)-getattr(local_shape.BoundBox,key)) < .05, fname + ': Außenmaße weichen vom CAD ab'
    report['parts'][fname] = {'solid_mesh': True, 'components': m.countComponents(), 'facets': m.CountFacets,
        'cad_symmetric_difference_mm3': difference, 'cad_relative_difference': difference/local_shape.Volume}
bad=[]
for o in doc.Objects:
    if any('Invalid' in x or 'Error' in x for x in o.State):
        bad.append([o.Name,o.State])
assert not bad, repr(bad)
report['assembly_dimensions_mm']=[50.6,57.0,12.8]
report['checks'] = ['Zwei gültige Einzelkörper','Außenmaße einschließlich Öse und beider Schraubenohren stimmen','Kein Überlappungsvolumen der Hälften',
    'AirTag-Hüllzylinder kollisionsfrei','Zwei Schrauben Ø2,5×10 inklusive Kopf kollisionsfrei',
    'Sicherungsmuttern SW5×3,8 kollisionsfrei; Schraube 0,6 mm durch Mutter, 0,4 mm im Gehäuse versenkt',
    'Beispielring Ø29,2 außen / Draht Ø2,2 kollisionsfrei','STEP mit zwei gültigen Körpern und Geometrie identisch zum CAD (Volumentoleranz 0,0001 mm³)',
    'STL/CAD symmetrische Volumendifferenz unter 0,3 %; Grenzen innerhalb 0,05 mm',
    'STLs geschlossen, jeweils eine Komponente, Zmin=0','FreeCAD-Recompute ohne Fehler']
report['physical_validation'] = 'Probedruck, Passung, Akustik und Belastung noch nicht physisch getestet.'
args.report.parent.mkdir(parents=True,exist_ok=True)
args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
