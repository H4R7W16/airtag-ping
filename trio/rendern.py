"""Vorschauen direkt aus den gespeicherten CAD-Körpern rendern."""

import math
from pathlib import Path

import FreeCAD as App
import Part
import vtk
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
CAD = HERE / "CAD"
V = App.Vector
BG = (0.955, 0.951, 0.934)
COLORS = {
    "Halo": ((0.06, 0.12, 0.17), "#183242", "Die ganze Mitte wird zum Spiegel"),
    "Komet": ((0.78, 0.24, 0.12), "#9e3b23", "Metalllicht in Bewegung"),
    "Signal": ((0.10, 0.29, 0.34), "#21515b", "Drei glänzende Funkbögen"),
    "Herzaugen": ((0.98, 0.72, 0.14), "#ae3041", "Rote Herzen mit metallischem Glanz"),
    "Schock": ((0.99, 0.77, 0.28), "#397ba1", "Hände an den Wangen, Augen weit offen"),
    "Peek": ((0.98, 0.73, 0.22), "#9a6d1d", "Ein Auge lugt zwischen den Fingern hervor"),
}
MASK_COLORS = {"Rot": (0.82, 0.075, 0.16), "Orange": (0.97, 0.56, 0.25),
               "Blau": (0.46, 0.77, 0.86), "Ocker": (0.94, 0.55, 0.22)}


def actor(shape, color, metal=False):
    vertices, faces = shape.tessellate(0.055)
    points = vtk.vtkPoints()
    for vertex in vertices:
        points.InsertNextPoint(vertex.x, vertex.y, vertex.z)
    triangles = vtk.vtkCellArray()
    for face in faces:
        triangles.InsertNextCell(3)
        for index in face:
            triangles.InsertCellPoint(index)
    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetPolys(triangles)
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(poly)
    normals.SetFeatureAngle(35)
    normals.SplittingOn()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    result = vtk.vtkActor()
    result.SetMapper(mapper)
    material = result.GetProperty()
    material.SetColor(*color)
    material.SetAmbient(0.15 if metal else 0.26)
    material.SetDiffuse(0.53 if metal else 0.72)
    material.SetSpecular(0.78 if metal else 0.20)
    material.SetSpecularPower(75 if metal else 25)
    return result


def socket_head(x, y):
    underside = 8.6  # M3×8: 2,4 mm tiefe Tasche in der Front
    head = Part.makeCylinder(2.75, 3.0, V(x, y, underside))
    radius = 2.5 / math.sqrt(3)
    vertices = [V(x + radius * math.cos(math.radians(30 + 60 * n)),
                  y + radius * math.sin(math.radians(30 + 60 * n)), 10.8)
                for n in range(6)]
    socket = Part.Face(Part.makePolygon(vertices + [vertices[0]])).extrude(V(0, 0, 1.0))
    return head.cut(socket)


def render(name):
    doc = App.openDocument(str(CAD / ("PING_Trio_" + name + ".FCStd")))
    back = doc.getObject("BackBody").Shape
    front = doc.getObject("FrontBody").Shape
    color = COLORS[name][0]
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(*BG)
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(850, 850)
    window.SetMultiSamples(8)
    window.AddRenderer(renderer)
    renderer.AddActor(actor(back, (0.08, 0.19, 0.23)))
    tag = Part.makeCylinder(15.95, 8.0, V(0, 0, 1.5))
    try:
        tag = tag.makeFillet(1.3, [edge for edge in tag.Edges if edge.Length > 80])
    except Exception:
        pass
    renderer.AddActor(actor(tag, (0.90, 0.91, 0.90)))
    renderer.AddActor(actor(Part.makeCylinder(12.4, 0.20, V(0, 0, 9.5)),
                            (0.46, 0.51, 0.55), True))
    renderer.AddActor(actor(front, color))
    for mask_color, rgb in MASK_COLORS.items():
        mask = doc.getObject("ColorMask_" + mask_color)
        if mask is not None:
            renderer.AddActor(actor(mask.Shape, rgb))
    for x in (-15, 15):
        head = socket_head(x, -14)
        renderer.AddActor(actor(head, (0.52, 0.57, 0.60), True))
    camera = renderer.GetActiveCamera()
    camera.ParallelProjectionOn()
    camera.SetPosition(39, -57, 108)
    camera.SetFocalPoint(0, 4, 5)
    camera.SetViewUp(0, 1, 0)
    camera.SetParallelScale(36)
    main_light = vtk.vtkLight()
    main_light.SetLightTypeToSceneLight()
    main_light.SetPosition(-35, 45, 110)
    main_light.SetFocalPoint(0, 0, 5)
    main_light.SetIntensity(1.0)
    renderer.AddLight(main_light)
    fill = vtk.vtkLight()
    fill.SetLightTypeToSceneLight()
    fill.SetPosition(80, -50, 85)
    fill.SetFocalPoint(0, 0, 5)
    fill.SetIntensity(0.43)
    renderer.AddLight(fill)
    renderer.ResetCameraClippingRange()
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.ReadFrontBufferOff()
    capture.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(CAD / ("PING_Trio_" + name + "_Vorschau.png")))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()
    App.closeDocument(doc.Name)


def font(size, bold=False):
    path = "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"
    return ImageFont.truetype(path, size)


def montage(names, title, subtitle, output):
    sheet = Image.new("RGB", (2300, 930), "#f4f3ee")
    draw = ImageDraw.Draw(sheet)
    draw.text((60, 28), title, font=font(62, True), fill="#17343d")
    draw.text((65, 106), subtitle, font=font(27), fill="#3a555b")
    for index, name in enumerate(names):
        x = 45 + index * 760
        preview = Image.open(CAD / ("PING_Trio_" + name + "_Vorschau.png"))
        preview.thumbnail((730, 680))
        sheet.paste(preview, (x, 170))
        draw.text((x + 26, 735), name.upper(), font=font(39, True), fill=COLORS[name][1])
        draw.text((x + 26, 793), COLORS[name][2], font=font(23), fill="#365056")
    draw.text((65, 875), "CAD-Geometrie · Farbmasken optional · AirTag und Schrauben vereinfacht · Probedruck erforderlich",
              font=font(21), fill="#657477")
    sheet.save(HERE / output)


if __name__ == "__main__":
    for motif in COLORS:
        render(motif)
    montage(("Halo", "Komet", "Signal"), "PING TRIO",
            "Drei Motive. Eine schlanke M3-Konstruktion.", "PING_Trio_Uebersicht.png")
    montage(("Herzaugen", "Schock", "Peek"), "PING EMOJI",
            "Drei Gefühle. Das AirTag-Metall spielt mit.", "PING_Emoji_Uebersicht.png")
    print("Sechs CAD-Vorschauen und zwei Übersichten erzeugt.")
