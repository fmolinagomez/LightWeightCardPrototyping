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
        self.headerText = "HEADER"
        self.headerColour = "#000000"
        self.headerBanner = False
        self.headerBannerColour = "#FFFFFF"
        self.typeStr = "TYPE - SUBTYPE"
        self.cardText = "Some text"
        self.cardTextColour = "#000000"
        self.manaCost = "\{W\}"
        self.power = None
        self.toughness = None
        self.image = None
        self.imageFullFrame = False
        self.footerText = ""
        self.footerColour = "#000000"
        self.footerFontStyle = "normal"

        if (name is not None) and (db is not None):
            # self.load(db[name][0]) For magic AllCards need this index
            self.load(db[name])

    def load(self, data: dict):
        header = data.get('header')
        if header is not None:
            header = header or {}
            self.headerText = header.get('text', '') or ''
            self.headerColour = header.get('color', '#000000') or '#000000'
            self.headerBanner = bool(header.get('banner', False))
            self.headerBannerColour = header.get('banner_color', '#FFFFFF') or '#FFFFFF'
        else:
            name_value = data.get('name', '') or ''
            self.headerText = name_value
            self.headerColour = '#000000'
            self.headerBanner = False
            self.headerBannerColour = '#FFFFFF'

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
        else:
            self.power = None
            self.toughness = None

        image_value = data.get('image')
        image_full_frame = False

        if isinstance(image_value, dict):
            self.image = image_value.get('source')
            image_full_frame = bool(image_value.get('full_frame', False))
        else:
            self.image = image_value
            image_full_frame = bool(data.get('full_frame_image', False))

        if not self.image:
            self.image = None
            image_full_frame = False

        self.imageFullFrame = image_full_frame

        footer = data.get('footer') or {}
        self.footerText = footer.get('text', '') or ''
        self.footerColour = footer.get('color', '#000000') or '#000000'
        footer_style = footer.get('font_style')
        if footer_style is None:
            footer_style = footer.get('style')
        if footer_style is None:
            footer_style = footer.get('font')
        if footer_style is None:
            footer_style = footer.get('tipo')
        self.footerFontStyle = self._normalise_footer_style(footer_style)

    def __str__(self):
        return f'{self.headerText} - {self.manaCost} ({self.typeStr})'

    def get_text_color_rgb(self):
        return self._hex_to_rgb(self.cardTextColour, default=(0.0, 0.0, 0.0))

    def get_header_text_color_rgb(self):
        return self._hex_to_rgb(self.headerColour, default=(0.0, 0.0, 0.0))

    def get_header_banner_color_rgb(self):
        return self._hex_to_rgb(self.headerBannerColour, default=(1.0, 1.0, 1.0))

    def get_footer_text_color_rgb(self):
        return self._hex_to_rgb(self.footerColour, default=(0.0, 0.0, 0.0))

    @staticmethod
    def _hex_to_rgb(colour: str, *, default):
        value = (colour or '').strip()
        if value.startswith('#'):
            value = value[1:]

        if len(value) != 6:
            return default

        try:
            red = int(value[0:2], 16) / 255.0
            green = int(value[2:4], 16) / 255.0
            blue = int(value[4:6], 16) / 255.0
        except ValueError:
            return default

        return (red, green, blue)

    @property
    def nameStr(self):
        return self.headerText

    @nameStr.setter
    def nameStr(self, value):
        self.headerText = value or ''

    @staticmethod
    def _normalise_footer_style(value: str) -> str:
        if not value:
            return 'normal'

        normalised = value.strip().lower()
        style_map = {
            'normal': 'normal',
            'bold': 'bold',
            'negrita': 'bold',
            'italic': 'italic',
            'italica': 'italic',
            'itálica': 'italic',
            'itálica': 'italic',
        }

        return style_map.get(normalised, 'normal')
