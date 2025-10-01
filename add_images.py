
import io
import pathlib
from functools import lru_cache

import cairo

import card_model
import layout

from PIL import Image, ImageStat

try:
    _RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    _RESAMPLE = Image.LANCZOS



def _ensure_output_dir(deck: str) -> pathlib.Path:
    path = pathlib.Path('decks') / deck / 'images'
    path.mkdir(parents=True, exist_ok=True)
    return path

try:
    _RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    _RESAMPLE = Image.LANCZOS


def _ensure_output_dir(deck: str) -> pathlib.Path:
    path = pathlib.Path('decks') / deck / 'images'
    path.mkdir(parents=True, exist_ok=True)
    return path

class BaseImage:
    def __init__(self, image):
        self.baseImage = None

        if (image is not None):
            self.baseImage = self.load(image)
    
    def load(self, image):
        return Image.open(image)
    def copy(self):
        return self.baseImage.copy()
    def update(self, image: Image):
        self.baseImage = image
    def get(self):
        return self.baseImage
    def save(self,path):
        self.baseImage.save(path)


def _load_resized_source_image(image_name: str, size_px):
    source_path = pathlib.Path('images') / image_name
    try:
        with Image.open(source_path) as original_image:
            resized_image = original_image.resize(size_px, _RESAMPLE)
    except (FileNotFoundError, OSError):
        return None

    return resized_image.convert('RGBA')


def processImage(
    card: card_model.CardModel,
    deck: str,
    *,
    size_mm=layout.ART_SIZE_MM,
    dpi: int = layout.SINGLE_CARD_DPI,
):
    if card.image is None:
        return

    size_px = layout.pair_mm_to_pixels(size_mm, dpi)
    output_dir = _ensure_output_dir(deck)
    destination = output_dir / str(card.image)

    if destination.exists():
        try:
            with Image.open(destination) as existing_image:
                if existing_image.size == size_px:
                    return
        except (FileNotFoundError, OSError):
            pass

    resized_image = _load_resized_source_image(str(card.image), size_px)
    if resized_image is None:
        return

    resized_image.save(destination)
    


def addImage(
    card: card_model.CardModel,
    base: BaseImage,
    deck: str,
    *,
    position_mm=None,
    size_mm=layout.ART_SIZE_MM,
    dpi: int = layout.SINGLE_CARD_DPI,
):

    if card.image is None:
        return base.get()

    output_dir = _ensure_output_dir(deck)
    image_path = output_dir / str(card.image)

    try:
        card_image = Image.open(image_path)
    except (FileNotFoundError, OSError):
        return base.get()

    target_size_px = layout.pair_mm_to_pixels(size_mm, dpi)
    if card_image.size != target_size_px:
        card_image = card_image.resize(target_size_px, _RESAMPLE)

    if card_image.mode != 'RGBA':
        card_image = card_image.convert('RGBA')

    image_copy = base.copy()
    position_mm = position_mm or layout.ART_OFFSET_MM
    position_px = layout.pair_mm_to_pixels(position_mm, dpi)

    if 'A' in card_image.getbands():
        mask = card_image.split()[-1]
    else:
        mask = None
    image_copy.paste(card_image, position_px, mask)
    return image_copy



def _relative_luminance_from_mean(mean_rgb):
    def _srgb_to_linear(value):
        if value <= 0.04045:
            return value / 12.92
        return ((value + 0.055) / 1.055) ** 2.4

    red, green, blue = (channel / 255.0 for channel in mean_rgb)
    red_lin = _srgb_to_linear(red)
    green_lin = _srgb_to_linear(green)
    blue_lin = _srgb_to_linear(blue)
    return 0.2126 * red_lin + 0.7152 * green_lin + 0.0722 * blue_lin


def _best_text_color(image: Image.Image):
    mean_rgb = ImageStat.Stat(image.convert('RGB')).mean
    luminance = _relative_luminance_from_mean(mean_rgb)

    contrast_with_white = (1.05) / (luminance + 0.05)
    contrast_with_black = (luminance + 0.05) / 0.05

    if contrast_with_white >= contrast_with_black:
        return (1.0, 1.0, 1.0)
    return (0.0, 0.0, 0.0)


@lru_cache(maxsize=128)
def _load_full_frame_surface_cached(image_name: str, dpi: int):
    size_px = layout.pair_mm_to_pixels((layout.CARD_WIDTH_MM, layout.CARD_HEIGHT_MM), dpi)
    resized_image = _load_resized_source_image(image_name, size_px)
    if resized_image is None:
        return None, None

    text_color = _best_text_color(resized_image)

    buffer = io.BytesIO()
    resized_image.save(buffer, format='PNG')
    buffer.seek(0)
    surface = cairo.ImageSurface.create_from_png(buffer)
    return surface, text_color


def load_full_frame_surface(card: card_model.CardModel, dpi: int):
    if card.image is None:
        return None, None

    return _load_full_frame_surface_cached(str(card.image), dpi)

