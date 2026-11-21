import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'api'))

from platnicy_domeny import rdzen_marki, sygnaly_domen  # noqa: E402


def reklamy(domena, *platnicy, stan='poza_listami'):
    return [{'domena': domena, 'reklamodawca': platnik, 'stan': stan} for platnik in platnicy]


def test_rdzen_marki_to_nazwa_przed_koncowka_domeny():
    assert rdzen_marki('quomarkets.com') == 'quomarkets'
    assert rdzen_marki('my.quomarkets.com') == 'quomarkets'
    assert rdzen_marki('akcje.xtb.com') == 'xtb'
    assert rdzen_marki('www.finax.eu') == 'finax'
    assert rdzen_marki('www.hl.co.uk') == 'hl'
    assert rdzen_marki('www.pekao.com.pl') == 'pekao'


def test_trzech_niezwiazanych_platnikow_daje_sygnal():
    sygnal = sygnaly_domen(reklamy('quomarkets.com', 'TRẦN VĂN ĐĨNH', 'NGÔ QUANG NGHĨA', 'NGUYỄN VĂN NAM'))
    assert sygnal['quomarkets.com']['kod'] == 'wielu_platnikow_domeny'
    assert sygnal['quomarkets.com']['modul'] == 'M1'


def test_dwoch_niezwiazanych_platnikow_nie_daje_sygnalu():
    assert sygnaly_domen(reklamy('quomarkets.com', 'TRẦN VĂN ĐĨNH', 'NGÔ QUANG NGHĨA')) == {}


def test_platnik_z_nazwa_marki_sie_nie_liczy():
    wiersze = reklamy('www.webull.com', 'Webull Securities', 'WEBULL FINANCIAL LLC', 'Jan Kowalczyk', 'Anna Wierzbicka')
    assert sygnaly_domen(wiersze) == {}


def test_platnik_z_rejestru_sie_nie_liczy():
    wiersze = reklamy('zysk.example', 'Jan Kowalczyk', 'Anna Wierzbicka') + reklamy(
        'zysk.example', 'Dom Maklerski Alfa', stan='w_rejestrze')
    assert sygnaly_domen(wiersze) == {}


def test_ta_sama_nazwa_inaczej_zapisana_to_jeden_platnik():
    assert sygnaly_domen(reklamy('zysk.example', 'Alfa Ltd', 'ALFA LTD.', 'Beta Ltd')) == {}


def test_opis_wymienia_nazwy_po_kolei_i_najwyzej_szesc():
    trzy = sygnaly_domen(reklamy('zysk.example', 'Celina', 'Adam', 'Bogdan'))['zysk.example']
    assert trzy['opis'] == 'Reklamy domeny zysk.example opłaca 3 różnych płatników niezwiązanych z marką: Adam, Bogdan, Celina.'
    osiem = sygnaly_domen(reklamy('zysk.example', *'HGFEDCBA'))['zysk.example']
    assert osiem['opis'].endswith(': A, B, C, D, E, F i 2 innych.')
