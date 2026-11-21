from datetime import date

import pytest

import druga_domena
import lista_cert
import kolejka
import patrol
import reklamy_google
import rotacja
import zlec

HTML = '''<html><head>
<script>(function(w,d,s,l,i){})(window,document,'script','dataLayer','GTM-AB12CD3');</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-ABCDEF1234"></script>
<script>gtag('config', 'AW-123456789'); fbq('init', '1234567890123');</script>
<noscript><img src="https://www.facebook.com/tr?id=9876543210&ev=PageView"></noscript>
</head><body>GTM-x G-short</body></html>'''


def strona(tytul='Broker X', favicon='f1:100', szkielet='s1', identyfikatory=()):
    return {'tytul': tytul, 'favicon': favicon, 'szkielet': szkielet, 'identyfikatory': set(identyfikatory)}


def test_identyfikatory():
    assert druga_domena.identyfikatory(HTML) == {
        'GTM-AB12CD3', 'G-ABCDEF1234', 'AW-123456789', '1234567890123', '9876543210'}


def test_ta_sama_strona_gdy_wszystko_zgodne():
    assert druga_domena.ta_sama_strona(strona(identyfikatory=['GTM-AB12CD3']), strona(identyfikatory=['GTM-AB12CD3']))


def test_ten_sam_tytul_i_jeden_slad_to_za_malo():
    assert not druga_domena.ta_sama_strona(strona(), strona(szkielet='s2'))


def test_dwa_identyfikatory_to_jeden_rodzaj_sladu():
    assert not druga_domena.ta_sama_strona(strona(favicon='', szkielet='s1', identyfikatory=['A', 'B']),
                                           strona(favicon='', szkielet='s2', identyfikatory=['A', 'B']))


def test_inny_tytul_to_inna_strona():
    assert not druga_domena.ta_sama_strona(strona(), strona(tytul='Inny'))


def test_kandydaci():
    linki = (['https://www.siostra.io/rejestracja'] * 5 + ['https://rzadka.com/'] * 4
             + ['https://ostrzezona.com/a'] * 6 + ['https://facebook.com/x'] * 9
             + ['https://inna-z-listy.com/'] * 7 + ['https://app.siostra.io/login'] + ['mailto:a@b.pl'])
    assert druga_domena.kandydaci(linki, 'ostrzezona.com', {'ostrzezona.com': '', 'inna-z-listy.com': ''}) == ['siostra.io']


def test_oferta_inwestycyjna():
    assert druga_domena.wyglada_na_oferte('Handel na rynku Forex. Otwórz konto u brokera CFD.')


def test_kasyno_to_nie_oferta():
    assert not druga_domena.wyglada_na_oferte('Slot gacor, maxwin, kasyno online, bonus 100%, free spin')


def test_jedno_slowo_finansowe_to_za_malo():
    assert not druga_domena.wyglada_na_oferte('Kasyno online, wpłać depozyt i odbierz bonus')


def test_szczegoly_reklamy():
    tekst = ('Szczegóły reklamy Najczęstsze pytania Szczegóły reklamy Jan Kowalski Informacje o tej reklamie mogą '
             'zależeć od lokalizacji Wyświetlanie: Polska close Wyświetlona po raz pierwszy: 9 paź 2026 '
             'Temat (oznaczenie dodane przez Google): Finanse Ostatnio wyświetlona: 31 paź 2026 Format: Tekstowa')
    assert reklamy_google.szczegoly(tekst) == {
        'reklamodawca': 'Jan Kowalski', 'pierwsza': date(2026, 10, 9), 'ostatnia': date(2026, 10, 31)}


def test_data_skrot_i_pelna_nazwa_miesiaca():
    assert reklamy_google.data('6 sie 2026') == date(2026, 8, 6)
    assert reklamy_google.data('1 marca 2023') == date(2023, 3, 1)
    assert reklamy_google.data('21 października 2025') == date(2025, 10, 21)


def test_nieznana_data_to_blad():
    with pytest.raises(RuntimeError):
        reklamy_google.data('1 marzec 2023')


def test_cert_dopasowuje_domene_nadrzedna(monkeypatch):
    monkeypatch.setattr(lista_cert, 'domeny', {'zly.pl'})
    assert lista_cert.na_liscie('www.zly.pl')
    assert lista_cert.na_liscie('zly.pl')
    assert not lista_cert.na_liscie('niezly.pl')


def test_rekord_reklamy():
    reklama = {'kreacja': 'CR1', 'reklamodawca': 'Jan Kowalski', 'pierwsza': date(2026, 10, 9),
               'ostatnia': date(2026, 10, 31), 'obraz': b'png'}
    rekord = patrol.rekord_reklamy('quomarkets.com', 'Quomarkets', reklama, '2026-11-01T10:00:00+00:00')
    assert {k: v for k, v in rekord.items() if k != 'sygnaly'} == {
        'zrodlo': 'google_ads', 'id_zrodla': 'CR1', 'platforma': 'google', 'url': 'https://quomarkets.com/',
        'reklamodawca': 'Jan Kowalski', 'tekst': '', 'zebrano': '2026-11-01T10:00:00+00:00',
        'opublikowano': '2026-10-09'}
    sygnal, = rekord['sygnaly']
    assert sygnal['kod'] == 'reklama_domeny_z_ostrzezenia_knf'
    assert sygnal['opis'].endswith('Wyświetlana w Polsce od 09.10.2026 do 31.10.2026.')
    assert sygnal['podstawa'] == 'Lista ostrzeżeń publicznych KNF: Quomarkets'


def test_rekord_drugiej_domeny():
    druga = {'domena': 'goldflame.io', 'zgodne': ['tytuł', 'ikona strony'], 'tytul': 'Broker', 'tekst': 'Handel'}
    rekord = patrol.rekord_drugiej_domeny('goldflame.com', 'Goldflame', druga, '2026-11-01T10:00:00+00:00')
    assert rekord['zrodlo'] == 'patrol_ostrzezen'
    assert rekord['id_zrodla'] == 'goldflame.io'
    assert rekord['platforma'] == 'www'
    assert rekord['url'] == 'https://goldflame.io/'
    assert rekord['reklamodawca'] is None
    assert rekord['opublikowano'] is None
    assert rekord['tekst'] == 'Broker Handel'
    sygnal, = rekord['sygnaly']
    assert sygnal['kod'] == 'druga_domena_ostrzezonej_strony'
    assert 'zgodne tytuł, ikona strony.' in sygnal['opis']


def test_sygnal_cert(monkeypatch):
    monkeypatch.setattr(lista_cert, 'domeny', {'goldflame.io'})
    assert patrol.sygnal_cert('goldflame.io')['kod'] == 'na_liscie_cert'
    assert patrol.sygnal_cert('goldflame.com')['kod'] == 'brak_na_liscie_cert'


def obsluz_z_atrapami(monkeypatch, rekordy, w_api):
    """Runs obsluz with a stubbed check and api; w_api maps id_zrodla to (is new, has picture[, text]).

    Returns the result and the ids that got a picture.
    """
    wyslane = []

    def dodaj(rekord):
        nowy, ma_obraz, *tekst = w_api[rekord['id_zrodla']]
        return nowy, {'id': rekord['id_zrodla'], 'ma_obraz': ma_obraz, 'tekst': tekst[0] if tekst else 'Trade With X'}

    monkeypatch.setattr(patrol, 'sprawdz', lambda *_: ('6 reklam', [{}, {}], {'domena': 'siostra.io'}, rekordy))
    monkeypatch.setattr(patrol.wysylka, 'dodaj', dodaj)
    monkeypatch.setattr(patrol.wysylka, 'wyslij_obraz', lambda id, obraz: wyslane.append(id))
    return patrol.obsluz('zla.com', {'zla.com': 'Zła'}, None, False), wyslane


def test_obsluz_liczy_dodane_pominiete_i_obrazy(monkeypatch):
    rekordy = [({'id_zrodla': 'CR1'}, b'png'), ({'id_zrodla': 'CR2'}, b'png'), ({'id_zrodla': 'siostra.io'}, None)]
    wynik, wyslane = obsluz_z_atrapami(
        monkeypatch, rekordy, {'CR1': (True, False), 'CR2': (False, False), 'siostra.io': (True, False)})
    assert wynik == (2, 1, 0, 'zla.com: reklamy Google: 6 reklam, otwarte 2; druga domena: siostra.io; '
                              'dodane 2, pominięte 1; obrazy 2')
    assert wyslane == ['CR1', 'CR2']


def test_nowy_rekord_z_obrazem_dostaje_obraz(monkeypatch):
    _, wyslane = obsluz_z_atrapami(monkeypatch, [({'id_zrodla': 'CR1'}, b'png')], {'CR1': (True, False)})
    assert wyslane == ['CR1']


def test_istniejacy_rekord_bez_obrazu_dostaje_obraz(monkeypatch):
    _, wyslane = obsluz_z_atrapami(monkeypatch, [({'id_zrodla': 'CR1'}, b'png')], {'CR1': (False, False)})
    assert wyslane == ['CR1']


def test_istniejacy_rekord_z_obrazem_nie_dostaje_drugiego(monkeypatch):
    _, wyslane = obsluz_z_atrapami(monkeypatch, [({'id_zrodla': 'CR1'}, b'png')], {'CR1': (False, True)})
    assert wyslane == []


def test_istniejacy_rekord_z_obrazem_ale_bez_tekstu_dostaje_obraz_jeszcze_raz(monkeypatch):
    _, wyslane = obsluz_z_atrapami(monkeypatch, [({'id_zrodla': 'CR1'}, b'png')], {'CR1': (False, True, '')})
    assert wyslane == ['CR1']


def test_bez_obrazu_nic_nie_wysyla(monkeypatch):
    _, wyslane = obsluz_z_atrapami(monkeypatch, [({'id_zrodla': 'CR1'}, None)], {'CR1': (True, False)})
    assert wyslane == []


def test_powtorka_pobiera_zapisane_z_api_raz(monkeypatch):
    monkeypatch.setattr(patrol.wysylka, 'zapisane', {})
    monkeypatch.setenv('API_URL', 'http://api')
    pobrania = []

    class Odpowiedz:
        def __init__(self, status_code, dane=None):
            self.status_code, self.dane = status_code, dane

        def raise_for_status(self):
            pass

        def json(self):
            return self.dane

    def get(adres, timeout):
        pobrania.append(adres)
        return Odpowiedz(200, [{'zrodlo': 'google_ads', 'id_zrodla': 'CR1', 'id': 7, 'ma_obraz': False},
                               {'zrodlo': 'google_ads', 'id_zrodla': 'CR2', 'id': 8, 'ma_obraz': True}])

    monkeypatch.setattr(patrol.wysylka.httpx, 'post', lambda *_, **__: Odpowiedz(409))
    monkeypatch.setattr(patrol.wysylka.httpx, 'get', get)
    assert patrol.wysylka.dodaj({'zrodlo': 'google_ads', 'id_zrodla': 'CR1'})[1]['id'] == 7
    assert patrol.wysylka.dodaj({'zrodlo': 'google_ads', 'id_zrodla': 'CR2'})[1]['ma_obraz'] is True
    assert pobrania == ['http://api/reklamy']


def test_obsluz_zwraca_blad(monkeypatch):
    def sprawdz(*_):
        raise RuntimeError('brak licznika reklam')

    monkeypatch.setattr(patrol, 'sprawdz', sprawdz)
    assert patrol.obsluz('zla.com', {'zla.com': 'Zła'}, None, False) == (
        0, 0, 1, 'zla.com: błąd: RuntimeError brak licznika reklam')


def test_zlec_bez_argumentow_bierze_cala_liste(monkeypatch):
    zlecone = []
    monkeypatch.setattr(kolejka, 'dodaj', zlecone.append)
    zlec.zlec([])
    assert zlecone == list(patrol.wczytaj_ostrzezenia())
    assert 'quomarkets.com' in zlecone


def test_rotacja_bierze_kolejne_wartosci_po_kolei(monkeypatch):
    monkeypatch.setattr(rotacja, 'uzyte', {})
    monkeypatch.setenv('ZBIERACZ_USER_AGENTS', 'agent-a/1, agent-b/1')
    monkeypatch.setenv('ZBIERACZ_PROXY', 'http://p1:8080,http://p2:8080')
    pierwsze, drugie, trzecie = rotacja.ustawienia(), rotacja.ustawienia(), rotacja.ustawienia()
    assert pierwsze == {'user_agent': 'agent-a/1', 'proxy': {'server': 'http://p1:8080'}}
    assert drugie == {'user_agent': 'agent-b/1', 'proxy': {'server': 'http://p2:8080'}}
    assert trzecie == pierwsze


def test_rotacja_bez_ustawien_zostawia_przegladarke(monkeypatch):
    monkeypatch.setattr(rotacja, 'uzyte', {})
    monkeypatch.setenv('ZBIERACZ_USER_AGENTS', '')
    monkeypatch.delenv('ZBIERACZ_PROXY', raising=False)
    assert rotacja.ustawienia() == {'user_agent': None, 'proxy': None}
