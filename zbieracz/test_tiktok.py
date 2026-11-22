from datetime import date

import tiktok

REKLAMA = {
    'id': '1881897875265745', 'name': 'Finax, o.c.p., a. s.', 'audit_status': '1', 'type': '2',
    'first_shown_date': 1794700800000, 'last_shown_date': 1794787200000, 'estimated_audience': '0-1K',
    'videos': [{'video_url': 'https://library.tiktok.com/api/v1/cdn/1/video/a', 'cover_img': 'https://p16.tiktokcdn.com/okladka'}],
    'image_urls': ['https://p19.tiktokcdn.com/obraz.jpeg'], 'title': 'Inwestowanie i relaks? To możliwe! ',
    'subject': 'Financial Services',
}
SZCZEGOLY = {
    'ad': {'id': '1881897875265745', 'external_url': 'https://WWW.Finax.eu/pl?utm_source=tiktok&utm_medium=video',
           'call_to_action': 'Dowiedz się więcej', 'subject': 'Financial Services'},
    'advertiser': {'name': 'Finax, o.c.p., a. s.', 'registry_location': 'Słowacja', 'tt_user': None,
                   'sponsor': 'HTTPOOL, d.o.o.'},
}
ZEBRANO = '2026-11-21T10:00:00+00:00'


def test_rekord_z_reklamodawca_i_domena():
    assert tiktok.rekord(REKLAMA, SZCZEGOLY, ZEBRANO) == {
        'zrodlo': 'tiktok_ads', 'id_zrodla': '1881897875265745', 'platforma': 'tiktok',
        'url': 'https://library.tiktok.com/ads/detail/?ad_id=1881897875265745', 'domena': 'www.finax.eu',
        'reklamodawca': 'Finax, o.c.p., a. s.', 'tekst': 'Inwestowanie i relaks? To możliwe!',
        'zebrano': ZEBRANO, 'opublikowano': '2026-11-15'}


def test_bez_adresu_strony_domena_pusta():
    szczegoly = {**SZCZEGOLY, 'ad': {**SZCZEGOLY['ad'], 'external_url': ''}}
    assert tiktok.rekord(REKLAMA, szczegoly, ZEBRANO)['domena'] is None


def test_temat_spoza_finansow_odpada():
    assert not tiktok.w_temacie({**REKLAMA, 'subject': 'Business Services'})
    assert not tiktok.w_temacie({**REKLAMA, 'subject': 'Home Improvement'})


def test_slowo_o_nieruchomosciach_w_podpisie_lub_nazwie_odpada():
    assert not tiktok.w_temacie({**REKLAMA, 'subject': None, 'title': 'Mieszkania nad morzem, rata od 2000 zł'})
    assert not tiktok.w_temacie({**REKLAMA, 'subject': None, 'name': 'NataliaNieruchomości'})
    assert not tiktok.w_temacie({**REKLAMA, 'title': 'Inwestycja w APARTAMENT w Tajlandii'})


def test_reklama_finansowa_bez_tematu_przechodzi():
    assert tiktok.w_temacie({**REKLAMA, 'subject': None})
    assert tiktok.w_temacie({**REKLAMA, 'subject': 'Apps', 'title': '24/7 Mobile Forex App'})


def test_wybierz_liczy_poza_tematem_i_bierze_najwyzej_dziesiec():
    lista = [{**REKLAMA, 'id': str(i)} for i in range(11)] + [{**REKLAMA, 'subject': 'Home Improvement'}]
    wybrane, poza_tematem = tiktok.wybierz(lista)
    assert [reklama['id'] for reklama in wybrane] == [str(i) for i in range(10)]
    assert poza_tematem == 1


def test_rekord_bez_podpisu_ma_pusty_tekst():
    rekord = tiktok.rekord({**REKLAMA, 'title': None}, SZCZEGOLY, ZEBRANO)
    assert rekord['tekst'] == ''


def test_data_z_milisekund():
    assert tiktok.data(1794700800000) == date(2026, 11, 15)
    assert tiktok.data(1795298419000) == date(2026, 11, 21)


def test_okladka_obraz_przed_filmem():
    assert tiktok.okladka(REKLAMA) == 'https://p19.tiktokcdn.com/obraz.jpeg'
    assert tiktok.okladka({**REKLAMA, 'image_urls': []}) == 'https://p16.tiktokcdn.com/okladka'
    assert tiktok.okladka({**REKLAMA, 'image_urls': [], 'videos': []}) is None


class Odpowiedz:
    def __init__(self, tresc=b'', status=200, dane=None):
        self.tresc, self.status, self.ok, self.dane = tresc, status, 200 <= status < 300, dane

    def body(self):
        return self.tresc

    def json(self):
        return self.dane


class Karta:
    """Strona biblioteki: odpowiedź na wyszukiwanie albo na szczegóły, zależnie od ostatniego adresu."""

    def __init__(self, wynik):
        self.wynik = wynik
        self.value = None

    def goto(self, adres, **_):
        self.value = Odpowiedz(dane={'data': SZCZEGOLY} if '/ads/detail/' in adres else self.wynik)

    def wait_for_timeout(self, _):
        pass

    def expect_response(self, *_, **__):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass


class Kontekst:
    def __init__(self, wynik, okladki):
        self.karta = Karta(wynik)
        self.request = type('Zadania', (), {'get': lambda _, adres: okladki[adres]})()

    def new_page(self):
        return self.karta

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass


def test_okladka_inna_niz_png_i_jpeg_nie_idzie_do_api(monkeypatch):
    lista = [{**REKLAMA, 'id': str(i), 'image_urls': [f'https://p19.tiktokcdn.com/{i}']} for i in range(4)]
    okladki = {
        'https://p19.tiktokcdn.com/0': Odpowiedz(b'RIFF\x00\x00\x00\x00WEBPVP8 '),
        'https://p19.tiktokcdn.com/1': Odpowiedz(b'\xff\xd8\xff<html>Access Denied</html>', status=403),
        'https://p19.tiktokcdn.com/2': Odpowiedz(b'\x89PNG\r\n\x1a\nobraz'),
        'https://p19.tiktokcdn.com/3': Odpowiedz(b'\xff\xd8\xffobraz'),
    }
    przegladarka = type('Przegladarka', (), {
        'new_context': lambda _, **__: Kontekst({'data': lista, 'total': 4}, okladki)})()
    dodane, obrazy = [], []
    monkeypatch.setattr(tiktok.rotacja, 'ustawienia', lambda: {})
    monkeypatch.setattr(tiktok.wysylka, 'dodaj', lambda rekord: (
        dodane.append(rekord['id_zrodla']) or True, {'id': rekord['id_zrodla'], 'ma_obraz': False, 'tekst': ''}))
    monkeypatch.setattr(tiktok.wysylka, 'wyslij_obraz', lambda id, obraz: obrazy.append(id))
    wynik = tiktok.obsluz('inwestowanie', przegladarka)
    assert wynik[:3] == (4, 0, 0)
    assert dodane == ['0', '1', '2', '3']
    assert obrazy == ['2', '3']


def test_adres_wyszukiwania():
    adres = tiktok.adres_wyszukiwania('giełda', 1795298400000)
    assert adres.startswith('https://library.tiktok.com/ads?region=PL&start_time=1792706400000&end_time=1795298400000')
    assert '&adv_name=gie%C5%82da&' in adres
    assert '&query_type=1&' in adres
