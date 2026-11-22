import json

import meta

SLEDZACA = {
    'ad_archive_id': '1814959106526730', 'page_name': 'OANDA TMS Brokers',
    'publisher_platform': ['FACEBOOK', 'INSTAGRAM'], 'start_date': 1788850800,
    'snapshot': {'body': {'text': 'Myślisz o inwestowaniu?\nPostaw na kontrakty na srebro bez prowizji.'},
                 'caption': 'tms.pl', 'cards': [],
                 'link_url': 'https://ad.doubleclick.net/ddm/trackclk/N299601.2201507FACEBOOK_ROS/B36638986.455833189'},
}
SZABLON = {
    'ad_archive_id': '1269830924657531', 'page_name': 'Saxo Bank',
    'publisher_platform': ['FACEBOOK', 'INSTAGRAM', 'MESSENGER', 'THREADS'], 'start_date': 1775804400,
    'snapshot': {'body': {'text': '{{product.brand}}'}, 'caption': 'home.saxo',
                 'link_url': 'https://www.home.saxo/pl-pl/campaigns/invest-for-less',
                 'cards': [{'body': 'Dlaczego pozwalać swojemu bankowi uszczuplać Twoje zyski?'}, {'body': 'Druga karta'}]},
}
DO_META = {
    'ad_archive_id': '1788634302300937', 'page_name': 'OANDA TMS Brokers',
    'publisher_platform': ['FACEBOOK'], 'start_date': 1790319600,
    'snapshot': {'body': {'text': 'Chcesz wiedzieć, jak skutecznie optymalizować koszty swojego tradingu?'},
                 'caption': 'facebook.com', 'link_url': 'https://www.facebook.com/246970801967', 'cards': []},
}


def strona(*dane):
    """A saved library page: its data sits in JSON scripts, nested as the library nests search results."""
    skrypty = ''.join(f'<script type="application/json" data-sjs>{json.dumps(wartosc)}</script>' for wartosc in dane)
    return f'<html><head><script>var x = 1;</script>{skrypty}<script type="application/json">nie json</script></head></html>'


def zagniezdz(*reklamy):
    return {'require': [['ScheduledServerJS', 'handle', None, [{'__bbox': {'result': {'data': {'ad_library_main': {
        'search_results_connection': {'edges': [{'node': {'collated_results': list(reklamy)}}]}}}}}}]]]}


def test_reklamy_ze_strony_w_kazdej_glebi_bez_powtorzen():
    html = strona(zagniezdz(SLEDZACA, SZABLON), {'inne': {'ad_archive_id': '1', 'bez': 'migawki'}}, zagniezdz(SZABLON, DO_META))
    assert sorted(meta.reklamy_ze_strony(html)) == ['1269830924657531', '1788634302300937', '1814959106526730']


def test_strona_bez_danych_reklam():
    assert meta.reklamy_ze_strony(strona({'a': [1, 2]})) == {}


def test_rekord_ze_sledzacym_linkiem_bierze_domene_z_podpisu():
    assert meta.rekord(SLEDZACA, '2026-11-21T20:00:00+00:00') == {
        'zrodlo': 'meta_ads',
        'id_zrodla': '1814959106526730',
        'platforma': 'facebook',
        'url': 'https://www.facebook.com/ads/library/?id=1814959106526730',
        'domena': 'tms.pl',
        'reklamodawca': 'OANDA TMS Brokers',
        'tekst': 'Myślisz o inwestowaniu?\nPostaw na kontrakty na srebro bez prowizji.',
        'zebrano': '2026-11-21T20:00:00+00:00',
        'opublikowano': '2026-09-08',
    }


def test_szablon_bierze_tekst_pierwszej_karty_a_domena_z_linku():
    zapis = meta.rekord(SZABLON, 'z')
    assert zapis['tekst'] == 'Dlaczego pozwalać swojemu bankowi uszczuplać Twoje zyski?'
    assert zapis['domena'] == 'www.home.saxo'


def test_link_do_aplikacji_mety_nie_daje_domeny():
    assert meta.rekord(DO_META, 'z')['domena'] is None


def test_platforma_z_pierwszej_na_liscie():
    tylko_instagram = dict(SLEDZACA, publisher_platform=['INSTAGRAM'])
    assert meta.rekord(tylko_instagram, 'z')['platforma'] == 'instagram'
