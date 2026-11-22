# The risk warning on the landing page of an ad, as the collector measured it on a computer and on a phone.
# The CFD warning must be prominent and in a font at least as large as the prevailing one (ESMA 2018/796, Annex III).
KONTRAST = 4.5
# WCAG asks less of large text: from 24 px, or from 18.66 px in bold.
KONTRAST_DUZEGO_TEKSTU = 3
MIEJSCA = {'komputer': 'na komputerze', 'telefon': 'na telefonie'}
PODSTAWA = ('Pomiar strony głównej domeny w przeglądarce {data} (komputer 1366 px, telefon 390 px). Ostrzeżenie o ryzyku '
            'CFD ma być wyeksponowane i nie mniejsze niż przeważająca czcionka: decyzja ESMA (UE) 2018/796, załącznik III, '
            'zastąpiona krajową interwencją produktową KNF; kontrast co najmniej 4,5:1 według WCAG 2.1')


def liczba(wartosc):
    return f'{wartosc:g}'.replace('.', ',')


def widac(widok):
    return bool(widok['ostrzezenie'] and widok['ostrzezenie']['widoczne'])


def uwagi(widok):
    """What makes the warning hard to read in one view, as Polish phrases; empty when it reads well."""
    if not widac(widok):
        return ['niewidoczne']
    ostrzezenie = widok['ostrzezenie']
    wynik = []
    if ostrzezenie['px'] < widok['przewazajacy_px']:
        wynik.append(f'mniejsze niż reszta tekstu ({liczba(ostrzezenie["px"])} px przy '
                     f'{liczba(widok["przewazajacy_px"])} px)')
    duze = ostrzezenie['px'] >= 24 or (ostrzezenie['px'] >= 18.66 and ostrzezenie['pogrubienie'] >= 700)
    prog = KONTRAST_DUZEGO_TEKSTU if duze else KONTRAST
    if ostrzezenie['kontrast'] is not None and ostrzezenie['kontrast'] < prog:
        wynik.append(f'słabo odcina się od tła (kontrast {liczba(ostrzezenie["kontrast"])}:1)')
    return wynik


def sygnal(kod, opis, strona):
    return {'modul': 'M2', 'kod': kod, 'opis': opis,
            'podstawa': PODSTAWA.format(data=f'{strona["zmierzono"]:%d.%m.%Y}')}


def sygnaly(domena, strona):
    """Findings for an ad that leads to domena; strona is the row of the strony table for it, or None."""
    if not strona:
        return []
    widoki = {nazwa: strona[nazwa] for nazwa in MIEJSCA if strona[nazwa]}
    if not any(widac(widok) for widok in widoki.values()):
        if any(widok['cfd'] for widok in widoki.values()):
            return [sygnal('brak_ostrzezenia_strony', f'Na stronie {domena} jest mowa o kontraktach CFD, ale nie widać '
                                                      'na niej standardowego ostrzeżenia o ryzyku.', strona)]
        return []
    czesci = [f'{MIEJSCA[nazwa]} {", ".join(uwagi(widok))}' for nazwa, widok in widoki.items() if uwagi(widok)]
    if not czesci:
        return []
    return [sygnal('ostrzezenie_nieczytelne', f'Ostrzeżenie o ryzyku na stronie {domena}: {"; ".join(czesci)}.', strona)]
