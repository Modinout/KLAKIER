from datetime import date

import tiktok

REKLAMA = {
    'id': '1881897875265745', 'name': 'Finax, o.c.p., a. s.', 'audit_status': '1', 'type': '2',
    'first_shown_date': 1794700800000, 'last_shown_date': 1794787200000, 'estimated_audience': '0-1K',
    'videos': [{'video_url': 'https://library.tiktok.com/api/v1/cdn/1/video/a', 'cover_img': 'https://p16.tiktokcdn.com/okladka'}],
    'image_urls': ['https://p19.tiktokcdn.com/obraz.jpeg'], 'title': 'Inwestowanie i relaks? To możliwe! ',
    'subject': 'Financial Services',
}


def test_rekord_z_wyniku_wyszukiwania():
    assert tiktok.rekord(REKLAMA, '2026-11-21T10:00:00+00:00') == {
        'zrodlo': 'tiktok_ads', 'id_zrodla': '1881897875265745', 'platforma': 'tiktok',
        'url': 'https://library.tiktok.com/ads/detail/?ad_id=1881897875265745',
        'reklamodawca': 'Finax, o.c.p., a. s.', 'tekst': 'Inwestowanie i relaks? To możliwe!',
        'zebrano': '2026-11-21T10:00:00+00:00', 'opublikowano': '2026-11-15'}


def test_rekord_bez_podpisu_ma_pusty_tekst():
    rekord = tiktok.rekord({**REKLAMA, 'title': None}, '2026-11-21T10:00:00+00:00')
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
