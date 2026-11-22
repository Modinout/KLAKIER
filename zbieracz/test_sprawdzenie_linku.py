import httpx

import kolejka
import lista_cert
import sprawdzenie_linku

OSTRZEZENIA = {'zla.com': 'Zła sp. z o.o.'}
LINK = 'https://t.ly/x'


def wizyta(**zmiany):
    return {'kiedy': '2026-11-21T12:00:00+00:00', 'rodzaj': 'komputer', 'status': 200,
            'adres': 'https://www.dobra.pl/oferta', 'lancuch': [LINK, 'https://www.dobra.pl/oferta'],
            'tytul': 'Oferta', 'tekst': 'Zarabiaj codziennie', 'html': '<html></html>', 'zrzut': b'png',
            'pomiar': {'przewazajacy_px': 16, 'cfd': False, 'ostrzezenie': None}, **zmiany}


def test_kod_bledu_przegladarki_trafia_do_powodu():
    assert sprawdzenie_linku.powod_bledu('net::ERR_NAME_NOT_RESOLVED at https://zla.example/') == (
        'Strona nie otworzyła się (net::ERR_NAME_NOT_RESOLVED).')
    assert sprawdzenie_linku.powod_bledu('Timeout 30000ms exceeded.') == 'Strona nie otworzyła się w ciągu 30 sekund.'
    assert sprawdzenie_linku.powod_bledu('Target page, context or browser has been closed') == 'Strona nie otworzyła się.'


def test_odpowiedz_z_bledem_albo_sprawdzenie_czlowieka_to_odmowa():
    assert sprawdzenie_linku.powod_odmowy(wizyta(status=404)) == 'Strona odpowiedziała kodem błędu 404.'
    assert sprawdzenie_linku.powod_odmowy(wizyta(status=503)) == 'Strona odpowiedziała kodem błędu 503.'
    assert sprawdzenie_linku.powod_odmowy(wizyta(tytul='Just a moment...')) == (
        'Strona zamiast treści pokazała sprawdzenie, czy odwiedza ją człowiek.')
    assert sprawdzenie_linku.powod_odmowy({'blad': 'Strona nie otworzyła się.'}) == 'Strona nie otworzyła się.'
    assert sprawdzenie_linku.powod_odmowy(wizyta()) is None


def test_rekord_linku():
    rekord = sprawdzenie_linku.rekord(LINK, wizyta(tekst='z' * 5000), [])
    assert {pole: wartosc for pole, wartosc in rekord.items() if pole != 'tekst'} == {
        'zrodlo': 'panel', 'id_zrodla': LINK, 'platforma': 'www', 'url': LINK, 'domena': 'www.dobra.pl',
        'reklamodawca': None, 'zebrano': '2026-11-21T12:00:00+00:00', 'opublikowano': None, 'sygnaly': []}
    assert rekord['tekst'].startswith('Oferta zzz')
    assert len(rekord['tekst']) == len('Oferta ') + sprawdzenie_linku.NAJWIECEJ_ZNAKOW


def test_domena_z_ostrzezenia_knf_w_lancuchu_i_lista_cert(monkeypatch):
    monkeypatch.setattr(lista_cert, 'domeny', set())
    lancuch = [LINK, 'https://promo.zla.com/a', 'https://promo.zla.com/b', 'https://www.dobra.pl/oferta']
    sygnaly = sprawdzenie_linku.sygnaly(wizyta(lancuch=lancuch), OSTRZEZENIA, True)
    assert [sygnal['kod'] for sygnal in sygnaly] == ['reklama_domeny_z_ostrzezenia_knf', 'brak_na_liscie_cert']
    assert 'promo.zla.com' in sygnaly[0]['opis']
    assert sygnaly[0]['podstawa'] == 'Lista ostrzeżeń publicznych KNF: Zła sp. z o.o.'
    assert 'www.dobra.pl' in sygnaly[1]['opis']


def test_bez_listy_cert_i_bez_ostrzezenia_nie_ma_sygnalow():
    assert sprawdzenie_linku.sygnaly(wizyta(), OSTRZEZENIA, False) == []


def obsluz_z_atrapami(monkeypatch, komputer, telefon, zapisana=None, blad_api=None):
    """Runs obsluz with stubbed visits and api; returns the printed line and the calls to the api in order."""
    wywolania = []
    wizyty = {'komputer': komputer, 'telefon': telefon}

    def dodaj(rekord):
        if blad_api:
            raise blad_api
        wywolania.append(('reklama', rekord['url'], rekord['domena']))
        return zapisana is None, zapisana or {'id': 7, 'ma_obraz': False}

    monkeypatch.setattr(sprawdzenie_linku, 'odwiedz', lambda przegladarka, url, widok: wizyty[widok])
    monkeypatch.setattr(sprawdzenie_linku, 'zapisz_stan', lambda id, stan: wywolania.append(('stan', id, stan)))
    monkeypatch.setattr(sprawdzenie_linku, 'zapisz_pomiar', lambda domena, pomiar: wywolania.append(('strona', domena, pomiar)))
    monkeypatch.setattr(sprawdzenie_linku, 'wyslij_dowod', lambda id, wizyta: wywolania.append(('dowod', id, wizyta['rodzaj'])))
    monkeypatch.setattr(sprawdzenie_linku.wysylka, 'dodaj', dodaj)
    monkeypatch.setattr(sprawdzenie_linku.wysylka, 'wyslij_obraz', lambda id, obraz: wywolania.append(('obraz', id, obraz)))
    linia = sprawdzenie_linku.obsluz('{"id": 3, "url": "%s"}' % LINK, OSTRZEZENIA, None, False)
    return linia, wywolania


def test_link_staje_sie_reklama_z_dowodami(monkeypatch):
    linia, wywolania = obsluz_z_atrapami(monkeypatch, wizyta(), wizyta(rodzaj='telefon', zrzut=b'png telefonu'))
    pomiar = {'adres': 'https://www.dobra.pl/oferta', 'przewazajacy_px': 16, 'cfd': False, 'ostrzezenie': None}
    assert wywolania == [
        ('stan', 3, {'stan': 'w_toku'}),
        ('strona', 'www.dobra.pl', {'komputer': pomiar, 'telefon': pomiar}),
        ('reklama', LINK, 'www.dobra.pl'),
        ('dowod', 7, 'komputer'),
        ('dowod', 7, 'telefon'),
        ('obraz', 7, b'png'),
        ('stan', 3, {'stan': 'gotowe', 'reklama_id': 7}),
    ]
    assert linia == f'{LINK}: reklama 7'


def test_powtorne_sprawdzenie_dodaje_dowody_i_zostawia_obraz(monkeypatch):
    _, wywolania = obsluz_z_atrapami(monkeypatch, wizyta(), wizyta(rodzaj='telefon'), zapisana={'id': 5, 'ma_obraz': True})
    assert ('dowod', 5, 'komputer') in wywolania and ('dowod', 5, 'telefon') in wywolania
    assert [wywolanie for wywolanie in wywolania if wywolanie[0] == 'obraz'] == []


def test_telefon_bez_strony_nie_ma_pomiaru_ani_dowodu(monkeypatch):
    _, wywolania = obsluz_z_atrapami(monkeypatch, wizyta(), {'blad': 'Strona nie otworzyła się.'})
    assert wywolania[1][2]['telefon'] is None
    assert [wywolanie for wywolanie in wywolania if wywolanie[0] == 'dowod'] == [('dowod', 7, 'komputer')]


def test_strona_z_bledem_nie_daje_reklamy(monkeypatch):
    linia, wywolania = obsluz_z_atrapami(monkeypatch, wizyta(status=404), wizyta(rodzaj='telefon'))
    assert wywolania == [
        ('stan', 3, {'stan': 'w_toku'}),
        ('stan', 3, {'stan': 'blad', 'blad': 'Strona odpowiedziała kodem błędu 404.'}),
    ]
    assert linia == f'{LINK}: błąd: Strona odpowiedziała kodem błędu 404.'


def test_blad_api_konczy_sprawdzenie_bledem(monkeypatch):
    _, wywolania = obsluz_z_atrapami(monkeypatch, wizyta(), wizyta(rodzaj='telefon'),
                                     blad_api=httpx.ConnectError('connection refused'))
    assert wywolania[-1] == ('stan', 3, {'stan': 'blad', 'blad': 'Nie udało się sprawdzić linku: connection refused'})


def test_robotnik_bierze_link_przed_domena(monkeypatch):
    class Redis:
        def blpop(self, listy):
            self.listy = listy
            return 'patrol:linki', '{"id": 1}'

    redis = Redis()
    monkeypatch.setattr(kolejka, 'polaczenie', lambda: redis)
    assert kolejka.pobierz() == ('patrol:linki', '{"id": 1}')
    assert redis.listy == [kolejka.LINKI, kolejka.LISTA]
