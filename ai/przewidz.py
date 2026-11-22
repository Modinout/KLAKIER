# Mały klasyfikator na CPU dla usługi ai, uczony przy imporcie tego modułu.
#   from przewidz import przewidz
#   przewidz('Zainwestuj 900 zl i zarabiaj 20 000 zl miesiecznie')
#   -> {'werdykt': 'oszustwo', 'prawdopodobienstwa': {'inne': .., 'oszustwo': ..}, 'pewny': True,
#       'powody': [{'slowo': 'zarabiaj', 'waga': ..}, ..], 'rodzaj': ..}
# Werdykt zależy tylko od prawdopodobieństwa oszustwa: 'ok' poniżej PROG_DO_SPRAWDZENIA, 'oszustwo' od PROG_OSZUSTWA,
# 'do_sprawdzenia' pomiędzy nimi albo gdy nie ma tekstu. To, czy w uczciwej reklamie brokera brakuje czegoś, czego
# wymaga prawo, sprawdzają reguły modułów M1-M3, a nie ten model.
# 'pewny' False = reklamę ocenia człowiek.
# Powód to słowo, którego usunięcie, w każdej pisowni, obniża logarytm szans oszustwa o co najmniej PROG_POWODU.
# Powody kosztują jedną predykcję na słowo, więc szuka się ich dopiero od PROG_RYZYKA_POWODOW wzwyż.
import re

import numpy as np

import ucz
from tekst import normalizuj, oczysc

PROG_OSZUSTWA = 0.7
PROG_DO_SPRAWDZENIA = 0.3
PROG_RYZYKA_RODZAJU = 0.3
PROG_RYZYKA_POWODOW = 0.1
PROG_RODZAJU = 0.5
PROG_POWODU = 0.2
NAJWIECEJ_POWODOW = 5
NAJWIECEJ_SLOW = 300
# Słowa, które nic nie mówią o ofercie: słowa funkcyjne, zaimki dzierżawcze i etykiety formularzy zapisu.
NIE_POWODY = {normalizuj(s) for s in (
    'się jak dla oraz lub czy nie jest bez który która które której którego którym których the and for '
    'twój twoja twoje twoją twojego twojej twojemu twoim twoich swój swoja swoje swoją swojego swojej swojemu swoim swoich '
    'imię nazwisko numer telefon e-mail email name phone number enter').split()}
_BRZEGI = re.compile(r'^\W+|\W+$')

_modele = ucz.ucz()


def przeucz():
    global _modele
    _modele = ucz.ucz()


def znane_rodzaje():
    return sorted(set(_modele[1].classes_) - {ucz.BEZ_RODZAJU})


def przewidz(tekst):
    model_werdyktu, model_rodzaju = _modele
    tekst = oczysc(tekst)
    pr = dict(zip(model_werdyktu.classes_, map(float, model_werdyktu.predict_proba([tekst])[0])))
    werdykt = _werdykt(tekst, pr['oszustwo'])
    return {
        'werdykt': werdykt,
        'prawdopodobienstwa': pr,
        'pewny': werdykt != 'do_sprawdzenia',
        'powody': _powody(model_werdyktu, tekst, pr['oszustwo']) if pr['oszustwo'] >= PROG_RYZYKA_POWODOW else [],
        'rodzaj': _rodzaj(model_rodzaju, tekst) if pr['oszustwo'] >= PROG_RYZYKA_RODZAJU else None,
    }


def _werdykt(tekst, p_oszustwa):
    if not tekst.strip() or PROG_DO_SPRAWDZENIA <= p_oszustwa < PROG_OSZUSTWA:
        return 'do_sprawdzenia'
    return 'oszustwo' if p_oszustwa >= PROG_OSZUSTWA else 'ok'


def _logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def _powody(model, tekst, p_oszustwa):
    slowa = tekst.split()
    rdzenie = [_BRZEGI.sub('', s) for s in slowa]
    klucze = [normalizuj(r) for r in rdzenie]
    # 'ZARABIAJ', 'zarabiaj!' i 'zarabiać' to jeden kandydat: usunięcie tylko jednej pisowni zostawiłoby słowo w tekście.
    pokaz = {}
    for rdzen, klucz in zip(rdzenie, klucze):
        if _moze_byc_powodem(klucz):
            pokaz.setdefault(klucz, rdzen)
    kandydaci = list(pokaz)[:NAJWIECEJ_SLOW]
    if not kandydaci:
        return []
    # Cechy char_wb ignorują rodzaj białych znaków, więc łączenie spacjami zmienia tylko usunięte słowo.
    bez_slowa = [' '.join(s for s, k in zip(slowa, klucze) if k != kandydat) for kandydat in kandydaci]
    p_bez = model.predict_proba(bez_slowa)[:, list(model.classes_).index('oszustwo')]
    wagi = _logit(p_oszustwa) - _logit(p_bez)
    powody = sorted(((float(w), pokaz[k]) for w, k in zip(wagi, kandydaci) if w >= PROG_POWODU), reverse=True)
    return [{'slowo': s, 'waga': w} for w, s in powody[:NAJWIECEJ_POWODOW]]


def _moze_byc_powodem(klucz):
    # Link albo domena i tak są pokazane przy reklamie, a liczba lub słowo z jednej czy dwóch liter nic same nie mówią.
    return (len(klucz) > 2 and any(z.isalpha() for z in klucz) and not any(z in klucz for z in './@')
            and klucz not in NIE_POWODY)


def _rodzaj(model, tekst):
    p = model.predict_proba([tekst])[0]
    nazwa = str(model.classes_[p.argmax()])
    return nazwa if nazwa != ucz.BEZ_RODZAJU and p.max() >= PROG_RODZAJU else None
