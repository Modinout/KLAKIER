import youtube
import wysylka

FEED = '''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns:media="http://search.yahoo.com/mrss/" xmlns="http://www.w3.org/2005/Atom">
 <title>Kanał</title>
 <entry>
  <id>yt:video:abc123</id>
  <yt:videoId>abc123</yt:videoId>
  <title>Pierwszy film</title>
  <author><name>Kanał Testowy</name></author>
  <published>2026-11-15T10:00:00+00:00</published>
  <media:group><media:title>Pierwszy film</media:title><media:description>Opis pierwszy</media:description></media:group>
 </entry>
 <entry>
  <id>yt:video:def456</id>
  <yt:videoId>def456</yt:videoId>
  <title>Drugi film</title>
  <author><name>Kanał Testowy</name></author>
  <published>2026-11-10T08:30:00+00:00</published>
  <media:group><media:title>Drugi film</media:title><media:description></media:description></media:group>
 </entry>
</feed>'''
ZEBRANO = '2026-11-22T10:00:00+00:00'


def test_wpisy_kanalu_zamieniaja_sie_w_rekordy():
    assert youtube.rekordy(FEED, ZEBRANO) == [
        {'zrodlo': 'youtube', 'id_zrodla': 'abc123', 'platforma': 'youtube',
         'url': 'https://www.youtube.com/watch?v=abc123', 'domena': None, 'reklamodawca': 'Kanał Testowy',
         'tekst': 'Pierwszy film\nOpis pierwszy', 'zebrano': ZEBRANO, 'opublikowano': '2026-11-15'},
        {'zrodlo': 'youtube', 'id_zrodla': 'def456', 'platforma': 'youtube',
         'url': 'https://www.youtube.com/watch?v=def456', 'domena': None, 'reklamodawca': 'Kanał Testowy',
         'tekst': 'Drugi film\n', 'zebrano': ZEBRANO, 'opublikowano': '2026-11-10'}]


def test_kazdy_rekord_idzie_do_wysylki_raz(monkeypatch):
    wyslane = []
    monkeypatch.setattr(wysylka, 'dodaj', lambda rekord: (wyslane.append(rekord) or rekord['id_zrodla'] == 'abc123', rekord))
    assert youtube.wyslij(youtube.rekordy(FEED, ZEBRANO)) == 1
    assert [rekord['id_zrodla'] for rekord in wyslane] == ['abc123', 'def456']
