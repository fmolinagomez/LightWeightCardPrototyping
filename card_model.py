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

        if ('text' in data):
            self.cardText = data['text']
        else:
            self.cardText = ""
        
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
