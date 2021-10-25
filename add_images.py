import json
import os
import pathlib
import card_model

from PIL import Image

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


def processImage(card: card_model.CardModel, deck):
    if card.image is None:
        return
    if not os.path.exists(os.path.join('decks',deck,'images',str(card.image))):
        originalImage = Image.open('./images/' + card.image)
        resizedImage = originalImage.resize((610,450))
        resizedImage.save('./decks/'+ deck +'/images/' +card.image)
    


def addImage (card: card_model.CardModel , base: BaseImage, deck,cardPos):

    if card.image is None:
        return base.get()

    cardImage = Image.open('./decks/'+ deck +'/images/' +str(card.image))
    image_copy = base.copy()
    position = ((cardPos[0]*805+165), (cardPos[1]*1060+200))
    image_copy.paste(cardImage, position)
    return image_copy