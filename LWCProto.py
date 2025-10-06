#! /usr/bin/env python3
import argparse
import re
from pathlib import Path

import cairo

import layout
from draw_card import drawCard
from card_model import CardModel
from card_model import CardDeck



def extant_file(x):
    """Argparse helper that ensures a file exists without opening it."""
    path = Path(x)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"{x} does not exist")
    return str(path)



##### CLI args #####
parser = argparse.ArgumentParser(description="Card generator for game prototypes")
parser.add_argument(
    '-c',
    '--cards',
    type=extant_file,
    help='json file containing cards description',
    metavar='FILE',
    required=True,
)
parser.add_argument('-i', '--images', help='Add images to cards', action='store_true')


args = parser.parse_args()

handle_images = args.images
cards_file = args.cards

cards = CardDeck(cards_file)

cardList = []
for entry in cards.getDb().values():
    card = CardModel()
    card.load(entry)
    cardList.append(card)

output_root = Path('output') / Path(cards_file).stem
cards_output_dir = output_root / 'cards'
cards_output_dir.mkdir(parents=True, exist_ok=True)

if handle_images:
    from add_images import BaseImage
    from add_images import addImage
    from add_images import processImage
    from add_images import load_full_frame_surface

    image_output_dir = output_root / 'images'
else:
    image_output_dir = None

single_dpi = layout.SINGLE_CARD_DPI


def _slugify(value: str) -> str:
    value = value.strip()
    value = re.sub(r'\s+', '_', value)
    value = re.sub(r'[^A-Za-z0-9_-]', '', value)
    return value or 'card'


for index, card in enumerate(cardList):
    print(f'Card {index}: {card}')
    surf = layout.get_single_card_surface(single_dpi)
    ctx = cairo.Context(surf)

    card_matrix = layout.get_single_card_matrix(single_dpi)
    ctx.set_matrix(card_matrix)
    layout.clip_card(ctx)
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()

    if handle_images and card.imageFullFrame:
        full_frame_surface = load_full_frame_surface(card, single_dpi)
        if full_frame_surface is not None:
            ctx.save()
            ctx.identity_matrix()
            ctx.set_source_surface(full_frame_surface, 0, 0)
            ctx.paint()
            ctx.restore()

    ctx.reset_clip()
    ctx.set_matrix(card_matrix)
    drawCard(card, ctx)

    card_filename = f"{index:03d}_{_slugify(card.headerText)}.png"
    output_path = cards_output_dir / card_filename
    surf.write_to_png(str(output_path))

    if handle_images and not card.imageFullFrame:
        processImage(card, output_dir=image_output_dir, dpi=single_dpi)
        baseImage = BaseImage(str(output_path))
        updated_image = addImage(
            card,
            baseImage,
            output_dir=image_output_dir,
            dpi=single_dpi,
        )
        baseImage.update(updated_image)
        baseImage.save(str(output_path))
