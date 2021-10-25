#! /usr/bin/env python3
import csv
import json
import os
import pathlib
import sys
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
parser.add_argument('-d', '--deck', type=extant_file, help='csv file containing the deck', metavar="FILE", required=True)
parser.add_argument('-c', '--cards', type=extant_file, help='json file containing cards description', metavar="FILE", required=True)

parser.add_argument('-i', '--images', help='Add images to cards', action='store_true')
parser.add_argument('-r', '--rgb', help='Update layout card border colour with given R,G,B, only works with default layout', nargs=3, type=int)
parser.add_argument('-l', '--layout', help='Use a different layout than default', type=extant_file, metavar="FILE")


args = parser.parse_args()

handle_images = args.images
modify_layout = args.rgb
deck_file = args.deck
cards_file = args.cards
#deck_file = './example_deck.csv'
deck_name = os.path.basename(deck_file)[:-4]
nameList = []
list_copy = []

with open(deck_file, encoding='utf-8') as csvFile:
    reader = csv.reader(csvFile)
    list_copy.append(reader.__next__())
    for row in reader:
        list_copy.append(row)
        nameList = nameList + [row[1]] * int(row[0])

cards = CardDeck(cards_file)

cardList = [CardModel(name,cards.getDb()) for name in nameList]
pageList = [cardList[i:i+9] for i in range(0, len(cardList), 9)]

if not os.path.exists('decks'):
    os.mkdir('decks')
if not os.path.exists(os.path.join('decks',deck_name)):
    os.mkdir(os.path.join('decks',deck_name))

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

    surf.write_to_png(f'decks/{deck_name}/{deck_name}_p{page_number}.png')

    from add_images import BaseImage
    from add_images import addImage
    from add_images import processImage
    from PIL import Image

    if (modify_layout is not None):
        baseImage = BaseImage(f'decks/{deck_name}/{deck_name}_p{page_number}.png')
        temp = baseImage.baseImage.convert('RGBA')
        data = np.array(temp)
        red, green, blue, alpha = data.T 
        for i in range(0,63):
            white_areas = (red == 190+i) & (blue == 190+i) & (green == 190+i)
            data[..., :-1][white_areas.T] = (modify_layout[0], modify_layout[1], modify_layout[2])
        baseImage.update(Image.fromarray(data))
        baseImage.save(f'decks/{deck_name}/{deck_name}_p{page_number}.png')


    #import pdb;pdb.set_trace()
    if (handle_images):

        if not os.path.exists(os.path.join('decks',deck_name,'images')):
            os.mkdir(os.path.join('decks',deck_name,'images'))
        #open the previous png to add the images
        baseImage = BaseImage(f'decks/{deck_name}/{deck_name}_p{page_number}.png')
        for i in range (len(page)):
            card = page[i]
            cardPos = (i % 3, i // 3)
            processImage(card,deck_name)
            baseImage.update(addImage(card,baseImage,deck_name, cardPos))
        baseImage.save(f'decks/{deck_name}/{deck_name}_p{page_number}.png')


with open(f'decks/{deck_name}/{deck_name}.csv', 'w') as deck_copy:
    filewriter = csv.writer(deck_copy)
    for element in list_copy:
        filewriter.writerow(element)
