import pytest

from jinja2 import Environment, DictLoader, FileSystemLoader, select_autoescape


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("page.html", True),
        ("page.htm", True),
        ("page.xml", True),
        ("page.xhtml", True),
        ("page.svg", True),
        ("PAGE.SVG", True),
        ("page.txt", False),
        (None, True),
    ],
)
def test_select_autoescape_defaults(name, expected):
    assert select_autoescape()(name) is expected


def test_explicit_extensions_override_defaults():
    select = select_autoescape(enabled_extensions=("txt",))
    assert select("page.txt") is True
    assert select("page.html") is False


def test_svg_and_xhtml_render_escaped():
    env = Environment(
        loader=DictLoader(
            {
                "icon.svg": "<svg><text>{{ v }}</text></svg>",
                "page.xhtml": "<p>{{ v }}</p>",
            }
        ),
        autoescape=select_autoescape(),
    )
    payload = "<script>alert(1)</script>"
    assert "&lt;script&gt;" in env.get_template("icon.svg").render(v=payload)
    assert "&lt;script&gt;" in env.get_template("page.xhtml").render(v=payload)


def test_filesystem_loader_svg_is_escaped(tmp_path):
    (tmp_path / "icon.svg").write_text("<svg><text>{{ v }}</text></svg>", encoding="utf-8")
    env = Environment(
        loader=FileSystemLoader(tmp_path), autoescape=select_autoescape()
    )
    assert "&lt;script&gt;" in env.get_template("icon.svg").render(v="<script>x</script>")
