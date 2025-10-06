import tempfile
import json
import pathlib
import unittest

from card_model import CardModel, CardDeck


class CardModelLoadTest(unittest.TestCase):
    def test_load_with_optional_fields(self):
        data = {
            "header": {
                "text": "Test Name",
                "color": "#ABCDEF",
                "banner": True,
                "banner_color": "#445566",
            },
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
            "full_frame_image": True,
        }

        card = CardModel()
        card.load(data)

        self.assertEqual(card.headerText, "Test Name")
        self.assertEqual(card.nameStr, "Test Name")
        self.assertEqual(card.headerColour, "#ABCDEF")
        self.assertTrue(card.headerBanner)
        self.assertEqual(card.headerBannerColour, "#445566")
        self.assertEqual(card.get_header_text_color_rgb(), (0xAB / 255.0, 0xCD / 255.0, 0xEF / 255.0))
        self.assertEqual(card.get_header_banner_color_rgb(), (0x44 / 255.0, 0x55 / 255.0, 0x66 / 255.0))
        self.assertEqual(card.typeStr, "Creature - Wizard")
        self.assertEqual(card.cardText, "Draw a card")
        self.assertEqual(card.cardTextColour, "#112233")
        self.assertEqual(card.get_text_color_rgb(), (0x11 / 255.0, 0x22 / 255.0, 0x33 / 255.0))
        self.assertEqual(card.manaCost, "{1}{U}")
        self.assertEqual(card.power, 2)
        self.assertEqual(card.toughness, 3)
        self.assertEqual(card.image, "wizard.png")
        self.assertTrue(card.imageFullFrame)

    def test_load_with_defaults(self):
        data = {
            "header": {
                "text": "Vanilla",
            },
            "type": "Creature",
        }

        card = CardModel()
        card.load(data)

        self.assertEqual(card.headerText, "Vanilla")
        self.assertFalse(card.headerBanner)
        self.assertEqual(card.headerColour, "#000000")
        self.assertEqual(card.headerBannerColour, "#FFFFFF")
        self.assertEqual(card.get_header_text_color_rgb(), (0.0, 0.0, 0.0))
        self.assertEqual(card.get_header_banner_color_rgb(), (1.0, 1.0, 1.0))
        self.assertEqual(card.typeStr, "Creature")
        self.assertEqual(card.cardText, "")
        self.assertEqual(card.cardTextColour, "#000000")
        self.assertEqual(card.get_text_color_rgb(), (0.0, 0.0, 0.0))
        self.assertEqual(card.manaCost, "")
        self.assertIsNone(card.power)
        self.assertIsNone(card.toughness)
        self.assertIsNone(card.image)
        self.assertFalse(card.imageFullFrame)

    def test_load_supports_image_object(self):
        data = {
            "header": {
                "text": "Object Image",
            },
            "type": "Sorcery",
            "image": {
                "source": "object.png",
                "full_frame": True,
            },
        }

        card = CardModel()
        card.load(data)

        self.assertEqual(card.image, "object.png")
        self.assertTrue(card.imageFullFrame)

    def test_load_supports_legacy_name_field(self):
        data = {
            "name": "Legacy",
            "type": "Enchantment",
        }

        card = CardModel()
        card.load(data)

        self.assertEqual(card.headerText, "Legacy")
        self.assertEqual(card.headerColour, "#000000")
        self.assertEqual(card.typeStr, "Enchantment")

    def test_load_supports_legacy_name_field(self):
        data = {
            "name": "Legacy",
            "type": "Enchantment",
        }

        card = CardModel()
        card.load(data)

        self.assertEqual(card.headerText, "Legacy")
        self.assertEqual(card.headerColour, "#000000")
        self.assertEqual(card.typeStr, "Enchantment")


class CardDeckLoadTest(unittest.TestCase):
    def test_load_uses_provided_path(self):
        cards = {
            "Example": {
                "header": {
                    "text": "Example",
                },
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
