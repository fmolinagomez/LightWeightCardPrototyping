import json
import pathlib


class CardDeck:
    def __init__(self, name='AllCards.json'):
        self.cardDb = dict()

        self.load(name)

    def load(self, name):
        db_path = pathlib.Path(name)

        if (not db_path.is_absolute()) and (not db_path.exists()):
            db_path = pathlib.Path(__file__).parent / name

        with open(db_path, encoding='utf-8') as dbFile:
            db = json.load(dbFile)
            self.cardDb = db
    def getDb(self):
        return self.cardDb

class CardModel:
    def __init__(self, name=None, db=None):
        self.nameStr = "NAME"
        self.typeStr = "TYPE - SUBTYPE"
        self.cardText = "Some text"
        self.cardTextColour = "#000000"
        self.manaCost = "\{W\}"
        self.power = None
        self.toughness = None
        self.image = None

        if (name is not None) and (db is not None):
            # self.load(db[name][0]) For magic AllCards need this index
            self.load(db[name])

    def load(self, data: dict):
        self.nameStr = data['name']
        self.typeStr = data['type']

        if ('subtype' in data):
            self.typeStr = self.typeStr + " - " + data['subtype']

        if 'card_text' in data:
            card_text = data['card_text'] or {}
            self.cardText = card_text.get('text', '')
            self.cardTextColour = card_text.get('colour', '#000000') or '#000000'
        elif 'text' in data:
            # Backwards compatibility with older card definitions.
            self.cardText = data['text']
            self.cardTextColour = '#000000'
        else:
            self.cardText = ""
            self.cardTextColour = '#000000'
        
        if ('manaCost' in data):
            self.manaCost = data['manaCost']
        else:
            self.manaCost = ""
        
        if 'power' in data:
            self.power = int(data['power'])
            self.toughness = int(data['toughness'])
        if 'image' in data:
            self.image = data['image']

    def __str__(self):
        return f'{self.nameStr} - {self.manaCost} ({self.typeStr})'

    def get_text_color_rgb(self):
        colour = (self.cardTextColour or '#000000').strip()
        if colour.startswith('#'):
            colour = colour[1:]

        if len(colour) != 6:
            return (0.0, 0.0, 0.0)

        try:
            red = int(colour[0:2], 16) / 255.0
            green = int(colour[2:4], 16) / 255.0
            blue = int(colour[4:6], 16) / 255.0
        except ValueError:
            return (0.0, 0.0, 0.0)

        return (red, green, blue)
