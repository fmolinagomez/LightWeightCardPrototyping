import pathlib

import card_model
import layout

from PIL import Image

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

    source_path = pathlib.Path('images') / str(card.image)
    try:
        with Image.open(source_path) as original_image:
            resized_image = original_image.resize(size_px, _RESAMPLE)
    except (FileNotFoundError, OSError):
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

    image_copy = base.copy()
    position_mm = position_mm or layout.ART_OFFSET_MM
    position_px = layout.pair_mm_to_pixels(position_mm, dpi)

    if 'A' in card_image.getbands():
        mask = card_image.split()[-1]
    else:
        mask = None
    image_copy.paste(card_image, position_px, mask)
    return image_copy
