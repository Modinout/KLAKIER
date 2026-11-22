# Runs the page measurement in a real browser on pages built for the test. Needs the patrol image:
# docker compose --profile patrol run --rm --no-deps patrol python -m pytest test_pomiar_ostrzezenia.py
import pytest

sync_api = pytest.importorskip('playwright.sync_api')

import strony_docelowe  # noqa: E402

TRESC = '<p>' + 'Handluj akcjami i walutami na naszej platformie. ' * 20 + '</p>'
OSTRZEZENIE = ('Kontrakty CFD są złożonymi instrumentami i wiążą się z dużym ryzykiem szybkiej utraty środków '
               'pieniężnych z powodu dźwigni finansowej. 76% rachunków inwestorów detalicznych odnotowuje straty.')


def strona(przed_trescia='', po_tresci='', styl=''):
    return ('<html><head><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<style>body {{ font-size: 16px; margin: 0 }} {styl}</style></head>'
            f'<body>{przed_trescia}{TRESC}{po_tresci}</body></html>')


@pytest.fixture(scope='module')
def przegladarka():
    with sync_api.sync_playwright() as playwright:
        przegladarka = playwright.chromium.launch()
        yield przegladarka
        przegladarka.close()


def zmierz(przegladarka, html, widok='komputer'):
    kontekst = przegladarka.new_context(**strony_docelowe.WIDOKI[widok])
    karta = kontekst.new_page()
    karta.set_content(html)
    pomiar = karta.evaluate(strony_docelowe.POMIAR)
    kontekst.close()
    return pomiar


def test_zgodne_ostrzezenie(przegladarka):
    pomiar = zmierz(przegladarka, strona(f'<p>{OSTRZEZENIE}</p>'))
    assert pomiar['przewazajacy_px'] == 16
    assert pomiar['cfd'] is True
    ostrzezenie = pomiar['ostrzezenie']
    assert ostrzezenie['tekst'] == OSTRZEZENIE
    assert (ostrzezenie['px'], ostrzezenie['pogrubienie'], ostrzezenie['kontrast']) == (16, 400, 21)
    assert ostrzezenie['widoczne'] is True and ostrzezenie['bez_przewijania'] is True


def test_mniejsza_czcionka(przegladarka):
    pomiar = zmierz(przegladarka, strona(f'<p style="font-size: 11px">{OSTRZEZENIE}</p>'))
    assert (pomiar['ostrzezenie']['px'], pomiar['przewazajacy_px']) == (11, 16)


def test_przewaza_rozmiar_z_najwieksza_iloscia_tekstu(przegladarka):
    pomiar = zmierz(przegladarka, strona('<h1 style="font-size: 40px">Inwestuj</h1><p style="font-size: 12px">Menu</p>'))
    assert pomiar['przewazajacy_px'] == 16


def test_baner_cookie_nie_ustala_przewazajacej_czcionki(przegladarka):
    baner = ('<div style="position: fixed; bottom: 0; font-size: 12px">'
             + 'Ta strona używa plików cookie. ' * 50 + '</div>')
    assert zmierz(przegladarka, strona(baner))['przewazajacy_px'] == 16


def test_blady_tekst_ma_slaby_kontrast(przegladarka):
    pomiar = zmierz(przegladarka, strona(f'<p style="color: #aaa">{OSTRZEZENIE}</p>'))
    assert pomiar['ostrzezenie']['kontrast'] == pytest.approx(2.32, abs=0.01)


def test_kontrast_liczy_sie_z_tlem_przodka(przegladarka):
    html = strona(f'<div style="background: #000"><p><span style="color: #767676">{OSTRZEZENIE}</span></p></div>')
    assert zmierz(przegladarka, html)['ostrzezenie']['kontrast'] == pytest.approx(4.62, abs=0.01)


def test_kolor_oklch(przegladarka):
    pomiar = zmierz(przegladarka, strona(f'<p style="color: oklch(0 0 0)">{OSTRZEZENIE}</p>'))
    assert pomiar['ostrzezenie']['kontrast'] == 21


def test_gradient_za_tekstem_to_nieznany_kontrast(przegladarka):
    html = strona(f'<div style="background: linear-gradient(#000, #333); color: #fff"><p>{OSTRZEZENIE}</p></div>')
    assert zmierz(przegladarka, html)['ostrzezenie']['kontrast'] is None


def test_ukryte_na_telefonie(przegladarka):
    html = strona(f'<p class="ryzyko">{OSTRZEZENIE}</p>', styl='@media (max-width: 600px) { .ryzyko { display: none } }')
    assert zmierz(przegladarka, html)['ostrzezenie']['widoczne'] is True
    na_telefonie = zmierz(przegladarka, html, 'telefon')['ostrzezenie']
    assert na_telefonie['widoczne'] is False and na_telefonie['bez_przewijania'] is False


def test_ostrzezenie_dopiero_po_przewinieciu(przegladarka):
    pomiar = zmierz(przegladarka, strona(po_tresci=f'<div style="height: 2000px"></div><p>{OSTRZEZENIE}</p>'))
    assert pomiar['ostrzezenie']['widoczne'] is True and pomiar['ostrzezenie']['bez_przewijania'] is False


def test_liczy_sie_najbardziej_widoczna_kopia(przegladarka):
    html = strona(f'<p style="font-size: 10px">{OSTRZEZENIE}</p>', f'<p style="font-size: 18px">{OSTRZEZENIE}</p>')
    assert zmierz(przegladarka, html)['ostrzezenie']['px'] == 18


def test_tekst_dla_czytnika_ekranu_jest_niewidoczny(przegladarka):
    ukryty = ('<span style="position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0)">'
              f'{OSTRZEZENIE}</span>')
    assert zmierz(przegladarka, strona(ukryty))['ostrzezenie']['widoczne'] is False


def test_strona_z_podmienionymi_metodami_tablic(przegladarka):
    podmiana = '<script>Array.prototype.reduce = function () { return this; }; Array.prototype.sort = function () { return this; };</script>'
    pomiar = zmierz(przegladarka, strona(podmiana, f'<p style="font-size: 10px">{OSTRZEZENIE}</p><p>{OSTRZEZENIE}</p>'))
    assert (pomiar['przewazajacy_px'], pomiar['ostrzezenie']['px']) == (16, 16)


def test_brak_ostrzezenia_przy_cfd(przegladarka):
    pomiar = zmierz(przegladarka, strona('<p>Handluj kontraktami CFD na indeksy.</p>'))
    assert pomiar['ostrzezenie'] is None and pomiar['cfd'] is True


def test_strona_bez_cfd(przegladarka):
    pomiar = zmierz(przegladarka, strona())
    assert pomiar['ostrzezenie'] is None and pomiar['cfd'] is False


def test_tekst_w_skrypcie_sie_nie_liczy(przegladarka):
    skrypt = '<script type="application/json">{"ryzyko": "76% rachunków inwestorów detalicznych"}</script>'
    assert zmierz(przegladarka, strona(skrypt))['ostrzezenie'] is None
