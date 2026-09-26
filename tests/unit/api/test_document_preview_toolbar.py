from api.routers.documents import _with_print_toolbar


def test_toolbar_goes_right_after_body_tag():
    html = '<html><head></head><body class="x"><h1>Faktura</h1></body></html>'

    result = _with_print_toolbar(html)

    assert result.startswith('<html><head></head><body class="x">')
    assert result.index("window.print()") < result.index("<h1>Faktura</h1>")


def test_toolbar_is_prepended_when_there_is_no_body():
    assert _with_print_toolbar("<p>x</p>").endswith("<p>x</p>")
    assert "window.print()" in _with_print_toolbar("<p>x</p>")
