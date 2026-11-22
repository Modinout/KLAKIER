# Reklamy Google wyświetlane w Polsce, które prowadzą do domeny, czytane z Ads Transparency Center.
import re
from datetime import date

import rotacja

ATC = 'https://adstransparency.google.com'
LICZNIK = re.compile(r'(\d[\d\s.,]*)\s*reklam\b', re.IGNORECASE)
KREACJA = re.compile(r'advertiser/(AR\d+)/creative/(CR\d+)')
REKLAMODAWCA = re.compile(r'.*Szczegóły reklamy (.*?) Informacje o tej reklamie')
PIERWSZA = re.compile(r'Wyświetlona po raz pierwszy: (\d{1,2} \S+ \d{4})')
OSTATNIA = re.compile(r'Ostatnio wyświetlona: (\d{1,2} \S+ \d{4})')
NAJWIECEJ = 8
OBRAZ = 'img[src*="tpc.googlesyndication.com/archive/simgad/"]'
RAMKA = 'iframe[src*="/adframe"], iframe[src*="tpc.googlesyndication.com/safeframe/"]'
# Google drukuje miesiąc albo skrótem, albo pełną formą dopełniacza.
MIESIACE = {
    'sty': 1, 'lut': 2, 'mar': 3, 'kwi': 4, 'maj': 5, 'cze': 6, 'lip': 7, 'sie': 8, 'wrz': 9, 'paź': 10, 'lis': 11, 'gru': 12,
    'stycznia': 1, 'lutego': 2, 'marca': 3, 'kwietnia': 4, 'maja': 5, 'czerwca': 6, 'lipca': 7, 'sierpnia': 8,
    'września': 9, 'października': 10, 'listopada': 11, 'grudnia': 12,
}


def reklamy(przegladarka, domena):
    """Zwraca tekst licznika reklam i reklamy z reklamodawcą, datami i obrazem."""
    ustawienia = rotacja.ustawienia()
    with przegladarka.new_context(locale='pl-PL', viewport={'width': 1280, 'height': 1400}, **ustawienia) as kontekst:
        karta = kontekst.new_page()
        otworz(karta, f'{ATC}/?region=PL&domain={domena}')
        licznik = LICZNIK.search(tekst_strony(karta))
        if not licznik:
            raise RuntimeError('brak licznika reklam na stronie Google')
        linki = karta.eval_on_selector_all('a[href*="/creative/CR"]', 'el => el.map(a => a.getAttribute("href"))')
        kreacje = list(dict.fromkeys(m.groups() for m in map(KREACJA.search, linki) if m))
        wynik = []
        for reklamodawca_id, kreacja in kreacje[:NAJWIECEJ]:
            karta.wait_for_timeout(3000)
            otworz(karta, f'{ATC}/advertiser/{reklamodawca_id}/creative/{kreacja}?region=PL')
            wynik.append({'kreacja': kreacja, **szczegoly(tekst_strony(karta)), 'obraz': obraz_reklamy(karta)})
    return licznik.group(0).strip(), wynik


def szczegoly(tekst):
    reklamodawca, pierwsza, ostatnia = REKLAMODAWCA.search(tekst), PIERWSZA.search(tekst), OSTATNIA.search(tekst)
    if not (reklamodawca and pierwsza and ostatnia):
        raise RuntimeError('nieznany układ strony reklamy: ' + tekst[:120])
    return {'reklamodawca': reklamodawca.group(1), 'pierwsza': data(pierwsza.group(1)), 'ostatnia': data(ostatnia.group(1))}


def data(tekst):
    """Data tak, jak Google drukuje ją po polsku, np. '9 paź 2026' albo '1 marca 2023'."""
    dzien, miesiac, rok = tekst.split()
    if miesiac not in MIESIACE:
        raise RuntimeError(f'nieznany zapis daty: {tekst}')
    return date(int(rok), MIESIACE[miesiac], int(dzien))


def otworz(karta, adres):
    karta.goto(adres, wait_until='domcontentloaded', timeout=45000)
    karta.wait_for_timeout(7000)


def tekst_strony(karta):
    return ' '.join(karta.evaluate('document.body.innerText').split())


def obraz_reklamy(karta):
    """PNG samej reklamy albo None, gdy strona nie pokazuje obrazu reklamy.

    Niektóre reklamy obrazkowe i wideo nie mają pliku obrazu i są rysowane w ramce, więc brana jest ramka.
    """
    for wybor in (OBRAZ, RAMKA):
        element = karta.locator(wybor).filter(visible=True)
        if element.count():
            return element.first.screenshot()
    return None
