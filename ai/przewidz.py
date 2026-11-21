# Small CPU classifier for the ai service, trained when this module is imported.
#   from przewidz import przewidz
#   przewidz('Zainwestuj 900 zl i zarabiaj 20 000 zl miesiecznie')
#   -> {'werdykt': 'oszustwo', 'prawdopodobienstwa': {'ok': .., 'do_sprawdzenia': .., 'oszustwo': ..}, 'pewny': True,
#       'powody': [{'slowo': 'zarabiaj', 'waga': ..}, ..], 'rodzaj': ..}
# The verdict follows the scam probability alone: 'ok' below PROG_DO_SPRAWDZENIA, 'oszustwo' from PROG_OSZUSTWA,
# 'do_sprawdzenia' between them or when there is no text. The middle class the model learns is not shown:
# from text alone it only repeats how broker ads look, and those are checked by the rules of modules M1-M3.
# 'pewny' False = a person rates the ad.
# A reason is a word whose removal lowers the scam log-odds by at least PROG_POWODU.
# Reasons cost one prediction per word, so they are looked for only from PROG_RYZYKA_POWODOW up.
import numpy as np

import ucz
from tekst import oczysc

PROG_OSZUSTWA = 0.7
PROG_DO_SPRAWDZENIA = 0.3
PROG_RYZYKA_RODZAJU = 0.3
PROG_RYZYKA_POWODOW = 0.1
PROG_RODZAJU = 0.5
PROG_POWODU = 0.2
NAJWIECEJ_POWODOW = 5
NAJWIECEJ_SLOW = 300

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
    kandydaci = list(dict.fromkeys(slowa))[:NAJWIECEJ_SLOW]
    if not kandydaci:
        return []
    # The char_wb features ignore the kind of whitespace, so rejoining with spaces changes nothing but the removed word.
    bez_slowa = [' '.join(s for s in slowa if s != kandydat) for kandydat in kandydaci]
    p_bez = model.predict_proba(bez_slowa)[:, list(model.classes_).index('oszustwo')]
    wagi = _logit(p_oszustwa) - _logit(p_bez)
    powody = sorted(((float(w), s) for w, s in zip(wagi, kandydaci) if w >= PROG_POWODU), reverse=True)
    return [{'slowo': s, 'waga': w} for w, s in powody[:NAJWIECEJ_POWODOW]]


def _rodzaj(model, tekst):
    p = model.predict_proba([tekst])[0]
    nazwa = str(model.classes_[p.argmax()])
    return nazwa if nazwa != ucz.BEZ_RODZAJU and p.max() >= PROG_RODZAJU else None
