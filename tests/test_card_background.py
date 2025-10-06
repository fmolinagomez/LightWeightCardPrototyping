import pytest

try:
    import cairo  # type: ignore
except Exception:  # pragma: no cover - optional dependency missing
    cairo = None

from card_model import CardModel

if cairo is not None:  # pragma: no branch - conditional import for optional dependency
    import layout
    from draw_card import drawCard
else:  # pragma: no cover - only triggered when cairo is missing
    layout = None
    drawCard = None


class TrackingCard(CardModel):
    def __init__(self):
        super().__init__()
        self.background_calls = 0

    def get_background_color_rgb(self):
        self.background_calls += 1
        return super().get_background_color_rgb()


def _render_card(card: TrackingCard) -> TrackingCard:
    assert cairo is not None and layout is not None and drawCard is not None
    dpi = layout.SINGLE_CARD_DPI
    surface = layout.get_single_card_surface(dpi)
    ctx = cairo.Context(surface)
    ctx.set_matrix(layout.get_single_card_matrix(dpi))
    drawCard(card, ctx)
    return card


@pytest.mark.skipif(cairo is None, reason="pycairo is not available")
def test_draw_card_requests_background_colour_when_not_full_frame():
    card = TrackingCard()
    card.backgroundColour = '#FF00FF'
    card.imageFullFrame = False

    rendered = _render_card(card)

    assert rendered.background_calls >= 1


@pytest.mark.skipif(cairo is None, reason="pycairo is not available")
def test_draw_card_skips_background_when_full_frame():
    card = TrackingCard()
    card.backgroundColour = '#FF00FF'
    card.imageFullFrame = True

    rendered = _render_card(card)

    assert rendered.background_calls == 0
