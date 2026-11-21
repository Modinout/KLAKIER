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


def test_adres_wyszukiwania():
    adres = tiktok.adres_wyszukiwania('giełda', 1795298400000)
    assert adres.startswith('https://library.tiktok.com/ads?region=PL&start_time=1792706400000&end_time=1795298400000')
    assert '&adv_name=gie%C5%82da&' in adres
    assert '&query_type=1&' in adres
