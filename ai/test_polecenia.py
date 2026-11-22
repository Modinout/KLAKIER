# Sprawdzenie reguły M1 o linkach polecających w opisach filmów. Uruchom: docker compose run --rm ai python test_polecenia.py
import sys
sys.stdout.reconfigure(encoding='utf-8')
from fastapi.testclient import TestClient

import polecenia
from main import app

OBCY = {'stan': 'poza_listami', 'podmiot': None, 'panstwo': None, 'lista': None}
FIRMA = {'stan': 'w_rejestrze', 'podmiot': 'X-TRADE BROKERS DOM MAKLERSKI S.A.', 'panstwo': 'Polska', 'lista': 'domy_maklerskie'}
KOD = ['polecenie_bez_oznaczenia']

LINK_212 = 'Jak kupić pierwsze akcje?\nZałóż konto w Trading 212 i odbierz darmową akcję: https://www.trading212.com/invite/ABC123'
LINK_REF = 'Najlepsza giełda krypto 2026\nBybit 👉 https://www.bybit.com/invite?ref=AEZDAAA'
LINK_SIEC = 'Broker do ETF bez prowizji:\nhttps://brokerx.prf.hn/click/camref:1100l3'
KOD_PL = 'Rejestrując się w XTB z kodem "BUNKIER" otrzymasz darmowy kurs inwestowania.'
KOD_EN = 'Get a free fractional share worth up to £100 with Trading 212, use promo code ISMAIL when you sign up.'

# tekst, wynik rejestru, oczekiwane kody
PROBY = [
    (LINK_212, OBCY, KOD),
    (LINK_REF, OBCY, KOD),
    (LINK_SIEC, OBCY, KOD),
    (KOD_PL, OBCY, KOD),
    (KOD_EN, OBCY, KOD),
    (LINK_212, None, KOD),
    ('Tu zakładam konto inwestycyjne 👉 https://link-pso.xtb.com/pso/u0V2g', OBCY, KOD),
    ('Revolut: https://revolut.com/referral/jan3s3f', OBCY, KOD),
    (LINK_212 + '\n#reklama', OBCY, []),
    (LINK_212 + '\n[Reklama] Promocja podlega regulaminowi.', OBCY, []),
    (KOD_PL + '\nFilm powstał we współpracy reklamowej z XTB.', OBCY, []),
    (KOD_PL + '\nPłatna współpraca z marką XTB.', OBCY, []),
    (LINK_REF + '\nTo jest link afiliacyjny.', OBCY, []),
    (KOD_EN + '\nThis video is sponsored by Trading 212.', OBCY, []),
    (KOD_EN + '\nIncludes paid partnership.', OBCY, []),
    (LINK_212 + '\nPartner odcinka: Trading 212.', OBCY, []),
    (LINK_212 + '\nKorzystając z linku polecającego wspierasz kanał.', OBCY, []),
    (KOD_EN + '\nI may earn a commission if you sign up.', OBCY, []),
    ('Konto maklerskie bez prowizji: https://www.xtb.com/pl', OBCY, []),
    ('Kupuję akcje i ETF, prowizja za transakcję to 0 zł. https://www.trading212.com/invite/ABC123', OBCY, KOD),
    ('Obejrzyj też: https://www.youtube.com/watch?v=abc i https://www.instagram.com/inwestor.pl/', OBCY, []),
    ('Mój kurs inwestowania w akcje: https://sklep.inwestor.pl/kurs', OBCY, []),
    ('CRM, którego używam do obsługi klientów: https://www.pipedrive.com/?ref=inwestor', OBCY, []),
    ('Kanał o giełdzie na Discordzie: https://discord.com/invite/wWvxfj6eCY', OBCY, []),
    ('Z kodem "ZERO" 10% rabatu na odżywki:\nhttps://sklep.sfd.pl/r/a/65', OBCY, []),
    ('Konferencja inwestycyjna Invest Cuffs. Z kodem "Comparic" 10% zniżki na bilety.', OBCY, []),
    ('Czym jest kod ISIN oraz ticker ETF-a?', OBCY, []),
    ('Kod promocyjny XTB - czy warto użyć? #xtb #giełda', OBCY, []),
    (LINK_212, FIRMA, []),
    (KOD_PL, FIRMA, []),
    ('', OBCY, []),
]
zle = 0
for tekst, rejestr, kody in PROBY:
    sygnaly = polecenia.sygnaly(tekst, rejestr, 'youtube')
    mam = [s['kod'] for s in sygnaly]
    dobrze = mam == kody and all(s['modul'] == 'M1' and s['opis'] and s['podstawa'] for s in sygnaly)
    zle += not dobrze
    print('OK  ' if dobrze else 'FAIL', ' '.join(tekst.split())[:60].ljust(60), '| expected', kody, '| got', mam)

mam = [s['kod'] for s in polecenia.sygnaly(LINK_212, OBCY, 'google_ads')]
zle += mam != []
print('OK  ' if mam == [] else 'FAIL', 'a referral in an ad from an ad library'.ljust(60), '| expected [] | got', mam)

opis = polecenia.sygnaly(LINK_212, OBCY, 'youtube')[0]['opis']
dobrze = 'trading212.com („trading212.com/invite/ABC123”)' in opis
zle += not dobrze
print('OK  ' if dobrze else 'FAIL', 'the finding names the host and quotes the link |', opis)

firmy = [
    (polecenia.sygnaly('Konto maklerskie: https://link-pso.xtb.com/pso/abc', OBCY, 'youtube'), {'nazwa': 'XTB', 'stan_rejestru': 'w_rejestrze'}),
    (polecenia.sygnaly('Najlepszy broker: https://brokerchampion.com/go/etoro', OBCY, 'youtube'), None),
]
for sygnaly, oczekiwana in firmy:
    mam = sygnaly[0].get('firma')
    dobrze = (mam is None) if oczekiwana is None else (mam is not None and all(mam[k] == v for k, v in oczekiwana.items()))
    zle += not dobrze
    print('OK  ' if dobrze else 'FAIL', 'promoted firm from the link domain | expected', oczekiwana, '| got', mam)

klient = TestClient(app)
film = klient.post('/ocen', json={'tekst': LINK_212, 'reklamodawca': 'Kanał o inwestowaniu', 'zrodlo': 'youtube'}).json()
reklama = klient.post('/ocen', json={'tekst': LINK_212, 'reklamodawca': 'Kanał o inwestowaniu', 'zrodlo': 'google_ads'}).json()
w_filmie = [s['kod'] for s in film['sygnaly']]
w_reklamie = [s['kod'] for s in reklama['sygnaly']]
dobrze = 'polecenie_bez_oznaczenia' in w_filmie and 'polecenie_bez_oznaczenia' not in w_reklamie
zle += not dobrze
print('OK  ' if dobrze else 'FAIL', '/ocen flags the video and not the ad |', w_filmie, w_reklamie)

print(f'{len(PROBY) + 5 - zle} of {len(PROBY) + 5} checks passed')
sys.exit(1 if zle else 0)
