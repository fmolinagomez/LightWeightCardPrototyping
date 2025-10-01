#! /usr/bin/env python3
import csv
import os
import re
import numpy as np

import cairo
import argparse


import layout
from draw_card import drawCard
from card_model import CardModel
from card_model import CardDeck



def extant_file(x):
    """
    'Type' for argparse - checks that file exists but does not open.
    """
    if not os.path.exists(x):
        # Argparse uses the ArgumentTypeError to give a rejection message like:
        # error: argument input: x does not exist
        raise argparse.ArgumentTypeError("{0} does not exist".format(x))
    return x



##### CLI args #####
parser = argparse.ArgumentParser(description="Deck Generator for Game Designers")
parser.add_argument('-d', '--deck', type=extant_file, help='csv file containing the deck', metavar="FILE")
parser.add_argument('-c', '--cards', type=extant_file, help='json file containing cards description', metavar="FILE", required=True)

parser.add_argument('-i', '--images', help='Add images to cards', action='store_true')
parser.add_argument('-r', '--rgb', help='Update layout card border colour with given R,G,B, only works with default layout', nargs=3, type=int)
parser.add_argument('-l', '--layout', help='Use a different layout than default', type=extant_file, metavar="FILE")
parser.add_argument('--single-card', help='Render each card as an individual 63x85mm PNG at 300 DPI', action='store_true')


args = parser.parse_args()

handle_images = args.images
modify_layout = args.rgb
cards_file = args.cards
single_card_mode = args.single_card
deck_file = args.deck

if single_card_mode and deck_file is not None:
    parser.error('the --single-card option cannot be used together with --deck/-d')

if (not single_card_mode) and deck_file is None:
    parser.error('the --deck/-d option is required unless --single-card is specified')

cards = CardDeck(cards_file)

nameList = []
list_copy = []

if single_card_mode:
    deck_name = os.path.splitext(os.path.basename(cards_file))[0]
    cardList = []
    for entry in cards.getDb().values():
        card = CardModel()
        card.load(entry)
        cardList.append(card)
else:
    deck_name = os.path.basename(deck_file)[:-4]
    with open(deck_file, encoding='utf-8') as csvFile:
        reader = csv.reader(csvFile)
        list_copy.append(reader.__next__())
        for row in reader:
            list_copy.append(row)
            nameList = nameList + [row[1]] * int(row[0])

    cardList = [CardModel(name, cards.getDb()) for name in nameList]
    pageList = [cardList[i:i+9] for i in range(0, len(cardList), 9)]

if handle_images or (modify_layout is not None):
    from add_images import BaseImage

if handle_images:
    from add_images import addImage
    from add_images import processImage

if not os.path.exists('decks'):
    os.mkdir('decks')
if not os.path.exists(os.path.join('decks',deck_name)):
    os.mkdir(os.path.join('decks',deck_name))

if single_card_mode:
    cards_output_dir = os.path.join('decks', deck_name, 'cards')
    os.makedirs(cards_output_dir, exist_ok=True)
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
        ctx.set_matrix(layout.get_single_card_matrix(single_dpi))
        drawCard(card, ctx)

        card_filename = f"{index:03d}_{_slugify(card.nameStr)}.png"
        output_path = os.path.join(cards_output_dir, card_filename)
        surf.write_to_png(output_path)

        if handle_images:
            processImage(card, deck_name, dpi=single_dpi)
            baseImage = BaseImage(output_path)
            updated_image = addImage(card, baseImage, deck_name, dpi=single_dpi)
            baseImage.update(updated_image)
            baseImage.save(output_path)
else:
    for page_number in range(len(pageList)):
        print(f'Page {page_number}:')
        page = pageList[page_number]
        surf = layout.getSurface()
        ctx = cairo.Context(surf)

        for i in range(len(page)):
            card = page[i]
            cardPos = (i % 3, i // 3)
            print(cardPos)
            print(card)
            mat = layout.getMatrix(*cardPos, surf)
            ctx.set_matrix(mat)
            drawCard(card, ctx)

        output_path = f'decks/{deck_name}/{deck_name}_p{page_number}.png'
        surf.write_to_png(output_path)

        if (modify_layout is not None):
            from PIL import Image

            baseImage = BaseImage(output_path)
            temp = baseImage.baseImage.convert('RGBA')
            data = np.array(temp)
            red, green, blue, alpha = data.T
            for i in range(0,63):
                white_areas = (red == 190+i) & (blue == 190+i) & (green == 190+i)
                data[..., :-1][white_areas.T] = (modify_layout[0], modify_layout[1], modify_layout[2])
            baseImage.update(Image.fromarray(data))
            baseImage.save(output_path)


        #import pdb;pdb.set_trace()
        if (handle_images):
            page_dpi = layout.get_surface_dpi(surf)
            baseImage = BaseImage(output_path)
            for i in range (len(page)):
                card = page[i]
                cardPos = (i % 3, i // 3)
                card_origin_mm = layout.get_card_origin_mm(cardPos)
                image_position_mm = (
                    card_origin_mm[0] + layout.ART_OFFSET_MM[0],
                    card_origin_mm[1] + layout.ART_OFFSET_MM[1],
                )
                processImage(card,deck_name, dpi=page_dpi)
                baseImage.update(
                    addImage(
                        card,
                        baseImage,
                        deck_name,
                        position_mm=image_position_mm,
                        dpi=page_dpi,
                    )
                )
            baseImage.save(output_path)

if not single_card_mode:
    with open(f'decks/{deck_name}/{deck_name}.csv', 'w') as deck_copy:
        filewriter = csv.writer(deck_copy)
        for element in list_copy:
            filewriter.writerow(element)

