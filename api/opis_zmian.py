# Krótkie polskie zdania do historii reklamy: co zmienił analityk albo ponowna ocena.
STATUSY = {'nowa': 'nowa', 'w_toku': 'w toku', 'zamknieta': 'zamknięta'}
WERDYKTY = {'ok': 'ok', 'do_sprawdzenia': 'do sprawdzenia', 'oszustwo': 'oszustwo'}
POZIOMY = {'wysokie': 'wysokie', 'srednie': 'średnie', 'niskie': 'niskie'}


def zmiany_analityka(przed, zmiany):
    """(id, zdanie) dla każdego pola zmiany, którego wartość różni się od przed, czyli reklamy sprzed zmiany."""
    return [(przed['id'], zdanie(pole, przed[pole], nowa)) for pole, nowa in zmiany.items() if przed[pole] != nowa]


def zdanie(pole, stara, nowa):
    """pole to pole ZmianaReklamy."""
    if pole == 'status':
        return f'Status: {STATUSY[stara]} → {STATUSY[nowa]}'
    if pole == 'werdykt_analityka':
        return f'Ocena analityka: {WERDYKTY[nowa]}' if nowa else 'Ocena analityka usunięta'
    if pole == 'domena':
        return f'Domena: {nowa}' if nowa else 'Domena usunięta'
    return 'Notatka zmieniona' if nowa else 'Notatka usunięta'


def zmiany_modelu(przed, po):
    """(id, zdanie) dla każdej reklamy, której werdykt modelu lub poziom ryzyka różni się po ponownej ocenie.

    przed i po mapują id na {'werdykt', 'poziom'}; reklama dodana w trakcie ponownej oceny nie ma z czym być porównana.
    """
    return [(id, zdanie_modelu(przed[id], ocena)) for id, ocena in po.items() if id in przed and przed[id] != ocena]


def zdanie_modelu(przed, po):
    czesci = []
    if przed['werdykt'] != po['werdykt']:
        czesci.append(f"ocena modelu: {WERDYKTY[przed['werdykt']]} → {WERDYKTY[po['werdykt']]}")
    if przed['poziom'] != po['poziom']:
        czesci.append(f"poziom ryzyka: {POZIOMY[przed['poziom']]} → {POZIOMY[po['poziom']]}")
    tekst = ', '.join(czesci)
    return tekst[0].upper() + tekst[1:]
