import json
import os

import pytest

import scrape_quini6

HTML_TEMPLATE = """
<html><body>
  <h2>Nro. Sorteo: 3330 - Fecha: 14/12/2025</h2>
  <div><strong>TRADICIONAL</strong><p>05 - 10 - 15 - 20 - 25 - 30</p></div>
  <div><strong>LA SEGUNDA</strong><p>01 - 02 - 03 - 04 - 05 - 06</p></div>
  <div><strong>REVANCHA</strong><p>11 - 12 - 13 - 14 - 15 - 16</p></div>
  <div><strong>SIEMPRE SALE</strong><p>21 - 22 - 23 - 24 - 25 - 26</p></div>
</body></html>
"""


class FakeResponse:
    def __init__(self, content="", status_code=200):
        self.content = content.encode("utf-8")
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeScraper:
    def __init__(self, response):
        self._response = response
        self.calls = []

    def get(self, url, headers=None):
        self.calls.append((url, headers))
        return self._response


@pytest.fixture
def run_in_tmpdir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def fake_site(monkeypatch):
    def _install(html="", status_code=200):
        scraper = FakeScraper(FakeResponse(html, status_code))
        monkeypatch.setattr(
            scrape_quini6.cloudscraper, "create_scraper", lambda **kwargs: scraper
        )
        return scraper

    return _install


@pytest.mark.parametrize(
    "text,expected",
    [("05", 5), (" 45 ", 45), ("Sorteo 3330", 3330), ("n°7", 7)],
)
def test_limpiar_numero(text, expected):
    assert scrape_quini6.limpiar_numero(text) == expected


def test_limpiar_numero_without_digits():
    with pytest.raises(ValueError):
        scrape_quini6.limpiar_numero("abc")


def test_run_scraper_writes_expected_json(run_in_tmpdir, fake_site):
    fake_site(HTML_TEMPLATE)

    scrape_quini6.run_scraper()

    output = run_in_tmpdir / "quinimind-frontend" / "public" / "data.json"
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["id"] == 3330
    assert data["date"] == "14/12/2025"
    assert data["modes"]["tradicional"] == [5, 10, 15, 20, 25, 30]
    assert data["modes"]["laSegunda"] == [1, 2, 3, 4, 5, 6]
    assert data["modes"]["revancha"] == [11, 12, 13, 14, 15, 16]
    assert data["modes"]["siempreSale"] == [21, 22, 23, 24, 25, 26]


def test_run_scraper_requests_target_url_with_headers(run_in_tmpdir, fake_site):
    scraper = fake_site(HTML_TEMPLATE)

    scrape_quini6.run_scraper()

    url, headers = scraper.calls[0]
    assert url == scrape_quini6.URL
    assert "User-Agent" in headers


def test_run_scraper_accepts_alternate_draw_id_format(run_in_tmpdir, fake_site):
    fake_site("<html><body>Sorteo N° 3401 del 01/01/2026</body></html>")

    scrape_quini6.run_scraper()

    data = json.loads(
        (run_in_tmpdir / "quinimind-frontend" / "public" / "data.json").read_text()
    )
    assert data["id"] == 3401
    assert data["date"] == "01/01/2026"


def test_run_scraper_defaults_when_no_metadata(run_in_tmpdir, fake_site):
    fake_site("<html><body>sin datos</body></html>")

    scrape_quini6.run_scraper()

    data = json.loads(
        (run_in_tmpdir / "quinimind-frontend" / "public" / "data.json").read_text()
    )
    assert data["id"] == 0
    assert data["date"]  # falls back to today's date
    assert data["modes"] == {
        "tradicional": [],
        "laSegunda": [],
        "revancha": [],
        "siempreSale": [],
    }


def test_run_scraper_ignores_out_of_range_and_duplicate_numbers(
    run_in_tmpdir, fake_site
):
    fake_site(
        """
        <html><body>
          <h2>Nro. Sorteo: 3331 - 15/12/2025</h2>
          <div><strong>TRADICIONAL</strong>
            <p>99 - 07 - 07 - 46 - 08 - 09 - 10 - 11 - 12</p>
          </div>
        </body></html>
        """
    )

    scrape_quini6.run_scraper()

    data = json.loads(
        (run_in_tmpdir / "quinimind-frontend" / "public" / "data.json").read_text()
    )
    assert data["modes"]["tradicional"] == [7, 8, 9, 10, 11, 12]


def test_run_scraper_reads_numbers_from_separate_elements(run_in_tmpdir, fake_site):
    cells = "".join(f"<span>{n:02d}</span>" for n in [3, 3, 46, 6, 9, 12, 15, 18])
    fake_site(
        f"""
        <html><body>
          <h2>Nro. Sorteo: 3332 - 16/12/2025</h2>
          <div><strong>TRADICIONAL</strong><div>{cells}</div></div>
        </body></html>
        """
    )

    scrape_quini6.run_scraper()

    data = json.loads(
        (run_in_tmpdir / "quinimind-frontend" / "public" / "data.json").read_text()
    )
    assert data["modes"]["tradicional"] == [3, 6, 9, 12, 15, 18]


def test_run_scraper_stops_after_max_steps(run_in_tmpdir, fake_site):
    filler = "".join(f"<span>x{i}</span>" for i in range(60))
    fake_site(
        f"""
        <html><body>
          <h2>Nro. Sorteo: 3333 - 17/12/2025</h2>
          <div><strong>TRADICIONAL</strong>{filler}
            <p>01 - 02 - 03 - 04 - 05 - 06</p>
          </div>
        </body></html>
        """
    )

    scrape_quini6.run_scraper()

    data = json.loads(
        (run_in_tmpdir / "quinimind-frontend" / "public" / "data.json").read_text()
    )
    assert data["modes"]["tradicional"] == []


def test_run_scraper_creates_output_directory(run_in_tmpdir, fake_site):
    fake_site(HTML_TEMPLATE)
    assert not os.path.exists(run_in_tmpdir / "quinimind-frontend")

    scrape_quini6.run_scraper()

    assert (run_in_tmpdir / "quinimind-frontend" / "public").is_dir()


def test_run_scraper_raises_on_403(run_in_tmpdir, fake_site, capsys):
    fake_site(HTML_TEMPLATE, status_code=403)

    with pytest.raises(Exception, match="403"):
        scrape_quini6.run_scraper()
    assert "403" in capsys.readouterr().out


def test_run_scraper_raises_on_http_error(run_in_tmpdir, fake_site):
    fake_site(HTML_TEMPLATE, status_code=500)

    with pytest.raises(RuntimeError, match="HTTP 500"):
        scrape_quini6.run_scraper()
