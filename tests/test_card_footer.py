import pytest

from card_model import CardModel


def _load_card(data):
    card = CardModel()
    card.load(data)
    return card


def test_footer_defaults_to_empty_text_and_normal_style():
    card = _load_card({'type': 'Evento'})

    assert card.footerText == ''
    assert card.footerColour == '#000000'
    assert card.footerFontStyle == 'normal'


@pytest.mark.parametrize(
    'style_value, expected',
    [
        ('normal', 'normal'),
        ('negrita', 'bold'),
        ('bold', 'bold'),
        ('italica', 'italic'),
        ('itálica', 'italic'),
    ],
)
def test_footer_style_is_normalised(style_value, expected):
    card = _load_card({
        'type': 'Evento',
        'footer': {
            'text': 'Referencia',
            'color': '#123456',
            'font_style': style_value,
        },
    })

    assert card.footerText == 'Referencia'
    assert card.footerColour == '#123456'
    assert card.footerFontStyle == expected


def test_footer_accepts_alternative_style_key():
    card = _load_card({
        'type': 'Evento',
        'footer': {
            'text': 'Nota al pie',
            'color': '#654321',
            'tipo': 'negrita',
        },
    })

    assert card.footerFontStyle == 'bold'
    assert card.get_footer_text_color_rgb() == pytest.approx((0x65 / 255, 0x43 / 255, 0x21 / 255))
