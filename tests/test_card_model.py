import tempfile
import json
import pathlib
import unittest

from card_model import CardModel, CardDeck


class CardModelLoadTest(unittest.TestCase):
    def test_load_with_optional_fields(self):
        data = {
            "name": "Test Name",
            "type": "Creature",
            "subtype": "Wizard",
            "card_text": {
                "text": "Draw a card",
                "colour": "#112233",
            },
            "manaCost": "{1}{U}",
            "power": 2,
            "toughness": 3,
            "image": "wizard.png",
        }

        card = CardModel()
        card.load(data)

        self.assertEqual(card.nameStr, "Test Name")
        self.assertEqual(card.typeStr, "Creature - Wizard")
        self.assertEqual(card.cardText, "Draw a card")
        self.assertEqual(card.cardTextColour, "#112233")
        self.assertEqual(card.get_text_color_rgb(), (0x11 / 255.0, 0x22 / 255.0, 0x33 / 255.0))
        self.assertEqual(card.manaCost, "{1}{U}")
        self.assertEqual(card.power, 2)
        self.assertEqual(card.toughness, 3)
        self.assertEqual(card.image, "wizard.png")

    def test_load_without_optional_fields(self):
        data = {
            "name": "Vanilla",
            "type": "Creature",
        }

        card = CardModel()
        card.load(data)

        self.assertEqual(card.nameStr, "Vanilla")
        self.assertEqual(card.typeStr, "Creature")
        self.assertEqual(card.cardText, "")
        self.assertEqual(card.cardTextColour, "#000000")
        self.assertEqual(card.get_text_color_rgb(), (0.0, 0.0, 0.0))
        self.assertEqual(card.manaCost, "")
        self.assertIsNone(card.power)
        self.assertIsNone(card.toughness)
        self.assertIsNone(card.image)


class CardDeckLoadTest(unittest.TestCase):
    def test_load_uses_provided_path(self):
        cards = {
            "Example": {
                "name": "Example",
                "type": "Artifact",
            }
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            deck_path = pathlib.Path(tmp_dir) / "cards.json"
            deck_path.write_text(json.dumps(cards), encoding="utf-8")

            deck = CardDeck(str(deck_path))

        self.assertIn("Example", deck.getDb())


if __name__ == "__main__":
    unittest.main()
