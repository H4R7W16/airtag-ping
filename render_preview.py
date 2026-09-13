"""Deterministic technical product render from the actual saved CAD geometry."""
from pathlib import Path
import sys,math,os,argparse
if os.environ.get('FREECAD_LIB'):
    sys.path.insert(0,os.environ['FREECAD_LIB'])
import FreeCAD as App
import Part
import vtk
from PIL import Image,ImageDraw,ImageFont
parser=argparse.ArgumentParser(description='Rendert die tatsächliche CAD-Geometrie mit VTK und Pillow.')
parser.add_argument('--artifact-dir',type=Path,default=Path(__file__).resolve().parent)
parser.add_argument('--output-dir',type=Path,default=Path(__file__).resolve().parent/'build'/'previews')
args=parser.parse_args()
ROOT=args.output_dir.resolve()
ROOT.mkdir(parents=True,exist_ok=True)
doc=App.openDocument(str(args.artifact_dir.resolve()/'PING_AirTag.FCStd'))
V=App.Vector
BG=(.949,.941,.914)
CORAL=(.94,.27,.18)
TEAL=(.055,.22,.235)

def actor(shape,color,metal=False):
    verts,faces=shape.tessellate(.045)
    points=vtk.vtkPoints()
    for v in verts: points.InsertNextPoint(v.x,v.y,v.z)
    cells=vtk.vtkCellArray()
    for face in faces:
        cells.InsertNextCell(3)
        for i in face: cells.InsertCellPoint(i)
    poly=vtk.vtkPolyData(); poly.SetPoints(points); poly.SetPolys(cells)
    normals=vtk.vtkPolyDataNormals(); normals.SetInputData(poly)
    normals.SetFeatureAngle(40); normals.SplittingOn(); normals.ConsistencyOn()
    mapper=vtk.vtkPolyDataMapper(); mapper.SetInputConnection(normals.GetOutputPort())
    a=vtk.vtkActor(); a.SetMapper(mapper)
    p=a.GetProperty(); p.SetColor(*color); p.SetAmbient(.23); p.SetDiffuse(.74)
    p.SetSpecular(.75 if metal else .22); p.SetSpecularPower(70 if metal else 28)
    return a

def moved(shape,xyz):
    s=shape.copy(); s.translate(V(*xyz)); return s

def hexprism(af,h,x,y,z):
    r=af/math.sqrt(3)
    pts=[V(x+r*math.cos(math.radians(30+60*j)),y+r*math.sin(math.radians(30+60*j)),z) for j in range(6)]
    return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,h))

def screw(x,y,z):
    s=Part.makeCylinder(1.25,10,V(x,y,z-10))
    h=Part.makeCylinder(2.25,1.5,V(x,y,z))
    return s.fuse(h).cut(hexprism(1.5,.9,x,y,z+.65))

def render(mode,path):
    ren=vtk.vtkRenderer(); ren.SetBackground(*BG)
    win=vtk.vtkRenderWindow(); win.SetOffScreenRendering(1)
    win.SetSize(1500,1300); win.SetMultiSamples(8); win.AddRenderer(ren)
    back=doc.BackBody.Shape.copy(); front=doc.FrontBody.Shape.copy()
    if mode=='print':
        front.Placement=doc.FrontBody.Placement.inverse().multiply(front.Placement)
        back.translate(V(-30,0,0)); front.translate(V(30,0,0))
    elif mode=='exploded':
        front.translate(V(0,0,29))
    ren.AddActor(actor(back,TEAL)); ren.AddActor(actor(front,CORAL))
    if mode!='print':
        airz=17 if mode=='exploded' else 2.4
        tag=Part.makeCylinder(15.95,8,V(0,0,airz))
        try: tag=tag.makeFillet(1.8,[e for e in tag.Edges if e.Length>80])
        except Exception: pass
        ren.AddActor(actor(tag,(.93,.94,.92)))
        disk=Part.makeCylinder(12.5,.25,V(0,0,airz+7.7))
        ren.AddActor(actor(disk,(.64,.69,.70),True))
        sz=55 if mode=='exploded' else 10.4
        for x in (-20.5,20.5):
            ren.AddActor(actor(screw(x,-5,sz),(.59,.65,.66),True))
            nz=-9 if mode=='exploded' else 1
            nut=hexprism(5,3.8,x,-5,nz).cut(Part.makeCylinder(1.25,3.8,V(x,-5,nz)))
            ren.AddActor(actor(nut,(.56,.61,.62),True))
        if mode=='hero':
            ring=Part.makeTorus(13.5,1.1,V(0,42,3.2),V(1,0,0))
            ren.AddActor(actor(ring,(.65,.7,.71),True))
    camera=ren.GetActiveCamera(); camera.ParallelProjectionOn()
    if mode=='print':
        target=(0,4,0); pos=(65,-100,165); scale=63
    elif mode=='exploded':
        target=(0,4,22); pos=(90,-130,135); scale=47
    else:
        target=(0,12,5); pos=(65,-92,155); scale=44
    camera.SetPosition(*pos); camera.SetFocalPoint(*target); camera.SetViewUp(0,1,0)
    camera.SetParallelScale(scale)
    light=vtk.vtkLight(); light.SetLightTypeToSceneLight()
    light.SetPosition(-60,20,120); light.SetFocalPoint(0,0,0); light.SetIntensity(.85)
    ren.AddLight(light)
    fill=vtk.vtkLight(); fill.SetLightTypeToSceneLight(); fill.SetPosition(80,-70,70)
    fill.SetFocalPoint(0,0,5); fill.SetIntensity(.45); ren.AddLight(fill)
    ren.ResetCameraClippingRange()
    win.Render()
    cap=vtk.vtkWindowToImageFilter(); cap.SetInput(win); cap.ReadFrontBufferOff(); cap.Update()
    out=vtk.vtkPNGWriter(); out.SetFileName(str(path)); out.SetInputConnection(cap.GetOutputPort()); out.Write()
    win.Finalize()

render('hero',ROOT/'PING_Vorschau.png')
render('exploded',ROOT/'PING_Explosionsansicht.png')
render('print',ROOT/'PING_Drucklage.png')
fontpath=os.environ.get('PING_FONT_REGULAR','C:/Windows/Fonts/segoeui.ttf')
boldpath=os.environ.get('PING_FONT_BOLD','C:/Windows/Fonts/segoeuib.ttf')
if not Path(fontpath).exists():
    fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
if not Path(boldpath).exists():
    boldpath='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(n,bold=False): return ImageFont.truetype(boldpath if bold else fontpath,n)
sheet=Image.new('RGB',(2100,1550),'#f2f0e9'); d=ImageDraw.Draw(sheet)
d.text((85,45),'PING',font=font(112,True),fill='#163c40')
d.text((400,82),'Dein Schlüsselbund hat jetzt einen Bodyguard.',font=font(38),fill='#163c40')
d.text((90,188),'FREECAD-ENTWURF  /  ZWEI DRUCKTEILE  /  PETG',font=font(22,True),fill='#a34232')
im=Image.open(ROOT/'PING_Vorschau.png'); im.thumbnail((1170,1020)); sheet.paste(im,(0,280))
im=Image.open(ROOT/'PING_Explosionsansicht.png'); im.thumbnail((850,730)); sheet.paste(im,(1200,250))
d.text((1260,1020),'Verschraubt. Wartbar. Mit einem Zwinkern.',font=font(28,True),fill='#163c40')
for i,s in enumerate(['01  Rückteil mit massiver Öse und Mutternfallen',
 '02  AirTag in umlaufend geführter Aufnahme',
 '03  Front mit Schallöffnungen im Gesicht',
 '04  Zwei versenkte M2,5 × 10 + Sicherungsmuttern']):
    d.text((1260,1080+i*52),s,font=font(23),fill='#334d4e')
d.line((90,1360,2010,1360),fill='#bcc5be',width=2)
d.text((90,1390),'50,6 × 57 × 12,8 mm',font=font(32,True),fill='#163c40')
d.text((760,1390),'PETG · 0,20 mm · 5–6 Wände',font=font(27),fill='#163c40')
d.text((90,1460),'Ansichten aus der CAD-Geometrie. Farben frei wählbar. AirTag und Hardware vereinfacht dargestellt. Probedruck erforderlich.',font=font(22),fill='#576968')
sheet.save(ROOT/'PING_Uebersicht.png')
print('Vier CAD-Vorschaubilder erstellt.')
