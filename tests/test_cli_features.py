import sys
import pytest

from utils import slugify

try:
    from add_images import _ensure_output_dir
except Exception:  # pragma: no cover - optional dependency missing
    _ensure_output_dir = None


@pytest.mark.parametrize(
    "value, expected",
    [
        ("Simple Name", "Simple_Name"),
        ("  leading and trailing  ", "leading_and_trailing"),
        ("special!*@#chars", "specialchars"),
        ("", "card"),
    ],
)
def test_slugify_generates_safe_names(value, expected):
    assert slugify(value) == expected

@pytest.mark.skipif(_ensure_output_dir is None, reason="Image processing dependencies are unavailable")
def test_ensure_output_dir_uses_custom_root(tmp_path):
    output_dir = _ensure_output_dir('demo-deck', tmp_path)
    expected_path = tmp_path / 'demo-deck' / 'images'

    assert output_dir == expected_path
    assert output_dir.exists()
