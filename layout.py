import math
import pathlib

import cairo

# Measurement helpers
MM_PER_INCH = 25.4


# All dimensions are in mm
# Card Measurements
nameBL = (6,8.5)
nameH = 2.5
typeBL = (6,52.5)
typeH = 2
cardTextBL = (6,58)
cardTextH = 2.2
cardTextW = 51
ptBL = (50.5,82)
ptH = 3
footerBL = (6,82)
footerH = 1.8

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
CARD_CORNER_RADIUS_MM = 3.0

commandPointsShieldTL = (CARD_WIDTH_MM - 9.5, 4.0)
commandPointsShieldSize = (7.2, 8.0)
commandPointsShieldPointHeight = 2.4
commandPointsFontSize = 3.6
commandPointsBorderWidth = 0.45
commandPointsShieldGap = 1.0


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
    ctx.set_operator(cairo.OPERATOR_SOURCE)
    ctx.set_source_rgba(0, 0, 0, 0)
    ctx.paint()
    ctx.set_operator(cairo.OPERATOR_OVER)

    return surface


def get_single_card_matrix(dpi: int = SINGLE_CARD_DPI):
    """Return a scaling matrix to draw cards using millimetre coordinates."""
    scale = dpi / MM_PER_INCH
    return cairo.Matrix(xx=scale, yy=scale)


def _rounded_rectangle_path(ctx: cairo.Context, x: float, y: float, width: float, height: float, radius: float):
    """Create a rounded rectangle path on the provided context."""
    radius = min(radius, width / 2.0, height / 2.0)

    ctx.new_sub_path()
    ctx.arc(x + width - radius, y + radius, radius, -math.pi / 2.0, 0)
    ctx.arc(x + width - radius, y + height - radius, radius, 0, math.pi / 2.0)
    ctx.arc(x + radius, y + height - radius, radius, math.pi / 2.0, math.pi)
    ctx.arc(x + radius, y + radius, radius, math.pi, 3 * math.pi / 2.0)
    ctx.close_path()


def clip_card(
    ctx: cairo.Context,
    *,
    width_mm: float = CARD_WIDTH_MM,
    height_mm: float = CARD_HEIGHT_MM,
    radius_mm: float = CARD_CORNER_RADIUS_MM,
):
    """Clip the drawing context to the card bounds using rounded corners in millimetres."""

    _rounded_rectangle_path(ctx, 0, 0, width_mm, height_mm, radius_mm)
    ctx.clip()


def clip_card_absolute(
    ctx: cairo.Context,
    origin_mm,
    dpi: float,
    *,
    width_mm: float = CARD_WIDTH_MM,
    height_mm: float = CARD_HEIGHT_MM,
    radius_mm: float = CARD_CORNER_RADIUS_MM,
):
    """Clip the context to a card positioned on the page using absolute millimetre coordinates."""

    origin_px = tuple(value / MM_PER_INCH * dpi for value in origin_mm)
    width_px = width_mm / MM_PER_INCH * dpi
    height_px = height_mm / MM_PER_INCH * dpi
    radius_px = radius_mm / MM_PER_INCH * dpi

    _rounded_rectangle_path(ctx, origin_px[0], origin_px[1], width_px, height_px, radius_px)
    ctx.clip()
