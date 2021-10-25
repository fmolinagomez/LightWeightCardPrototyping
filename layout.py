import pathlib
import cairo

# All dimensions are in mm
# Card Measurements
nameBL = (6,8.5)
nameH = 2.5
manaRight = 57
mana0TL = (54,5.5)
manaOS = 3.5
typeBL = (6,52.5)
typeH = 2
cardTextBL = (6,58)
cardTextH = 2.2
cardTextW = 51
ptBL = (50.5,82)
ptH = 3

#Inter-Card Measurements
origin = (8.5,6)
deltaX = 68
deltaY = 90

def getSurface() -> cairo.ImageSurface:
    return cairo.ImageSurface.create_from_png(pathlib.Path(__file__).parent / 'layout.png')

def getMatrix(x: int, y: int, surf: cairo.ImageSurface):
    sx = surf.get_width() / 8.5 / 25.4
    sy = surf.get_height() / 11 / 25.4

    x0 = (origin[0] + deltaX * x) * sx
    y0 = (origin[1] + deltaY * y) * sy
    return cairo.Matrix(x0=x0, y0=y0, xx=sx, yy=sy)