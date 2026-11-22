# Short Polish sentences for the history of an ad: what an analyst or a re-score changed.
STATUSY = {'nowa': 'nowa', 'w_toku': 'w toku', 'zamknieta': 'zamknięta'}
WERDYKTY = {'ok': 'ok', 'do_sprawdzenia': 'do sprawdzenia', 'oszustwo': 'oszustwo'}
POZIOMY = {'wysokie': 'wysokie', 'srednie': 'średnie', 'niskie': 'niskie'}


def zmiany_analityka(przed, zmiany):
    """(id, sentence) for each field of zmiany whose value differs from przed, the ad before the change."""
    return [(przed['id'], zdanie(pole, przed[pole], nowa)) for pole, nowa in zmiany.items() if przed[pole] != nowa]


def zdanie(pole, stara, nowa):
    """pole is a field of ZmianaReklamy."""
    if pole == 'status':
        return f'Status: {STATUSY[stara]} → {STATUSY[nowa]}'
    if pole == 'werdykt_analityka':
        return f'Ocena analityka: {WERDYKTY[nowa]}' if nowa else 'Ocena analityka usunięta'
    if pole == 'domena':
        return f'Domena: {nowa}' if nowa else 'Domena usunięta'
    return 'Notatka zmieniona' if nowa else 'Notatka usunięta'


def zmiany_modelu(przed, po):
    """(id, sentence) for each ad whose model verdict or risk level differs after a re-score.

    przed and po map ids to {'werdykt', 'poziom'}; an ad added during the re-score has nothing to compare with.
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
