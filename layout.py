import pathlib
import cairo

# Measurement helpers
MM_PER_INCH = 25.4


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

# Artwork measurements (relative to a single card origin)
ART_OFFSET_MM = (5.47, 10.933333333333332)
ART_SIZE_MM = (51.64666666666667, 38.1)

#Inter-Card Measurements
origin = (8.5,6)
deltaX = 68
deltaY = 90

# Single card defaults
CARD_WIDTH_MM = 63
CARD_HEIGHT_MM = 85
SINGLE_CARD_DPI = 300


def mm_to_pixels(value_mm: float, dpi: float) -> int:
    """Convert a millimetre measurement to whole pixels for a given DPI."""
    return int(round(value_mm / MM_PER_INCH * dpi))


def pair_mm_to_pixels(pair_mm, dpi: float):
    """Convert a pair of millimetre measurements to pixels."""
    return tuple(mm_to_pixels(v, dpi) for v in pair_mm)


def getSurface() -> cairo.ImageSurface:
    return cairo.ImageSurface.create_from_png(pathlib.Path(__file__).parent / 'layout.png')


def get_surface_dpi(surf: cairo.ImageSurface) -> float:
    """Infer the DPI of the reference layout surface."""
    return surf.get_width() / 8.5


def getMatrix(x: int, y: int, surf: cairo.ImageSurface):
    sx = surf.get_width() / 8.5 / MM_PER_INCH
    sy = surf.get_height() / 11 / MM_PER_INCH

    x0 = (origin[0] + deltaX * x) * sx
    y0 = (origin[1] + deltaY * y) * sy
    return cairo.Matrix(x0=x0, y0=y0, xx=sx, yy=sy)


def get_card_origin_mm(card_position):
    """Return the absolute origin in mm for a card positioned on the 3x3 grid."""
    return (
        origin[0] + deltaX * card_position[0],
        origin[1] + deltaY * card_position[1],
    )


def get_single_card_surface(dpi: int = SINGLE_CARD_DPI) -> cairo.ImageSurface:
    """Create a blank single-card surface at the requested DPI."""
    width_px = mm_to_pixels(CARD_WIDTH_MM, dpi)
    height_px = mm_to_pixels(CARD_HEIGHT_MM, dpi)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width_px, height_px)
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()
    return surface


def get_single_card_matrix(dpi: int = SINGLE_CARD_DPI):
    """Return a scaling matrix to draw cards using millimetre coordinates."""
    scale = dpi / MM_PER_INCH
    return cairo.Matrix(xx=scale, yy=scale)
