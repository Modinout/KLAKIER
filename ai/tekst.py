# Wspólne czyszczenie tekstu do uczenia (ucz.py) i predykcji (przewidz.py): usuwa to, co zdradza ŹRÓDŁO reklamy,
# a nie jej treść (przyciski interfejsu, nagłówek "nazwa strony / Sponsored", linie z id z Ad Library).
import re
import unicodedata

_PRZYCISKI = {'learn more', 'see details', 'sign up', 'download', 'install now', 'install', 'like page', 'financial service', 'open',
              'shop now', 'apply now', 'dowiedz się więcej', 'więcej informacji', 'zarejestruj się', 'pobierz', 'zainstaluj', 'otwórz',
              'sprawdź', 'visit advertiser', 'skip', 'obejrzyj w youtube', 'active', 'różne wersje tej reklamy'}
_WZORY = re.compile(r'^(spon[sz]or\w*|dowiedz się\W*|więcej infor\w*\W*|identyfikator\b.*|library id\b.*|[\d,. ]+ people like this)$')
_NIEWIDOCZNE = re.compile('[­᠎​-‏‪-‮⁠-⁤﻿]')
# Litery cyrylicy i greckie podobne do łacińskich, po zamianie na małe.
_PODOBNE = str.maketrans('аеіјорсухѕԁһӏвкмнтαεορτυνκχ', 'aeijopcyxsdhlbkmhtaeoptuvkx')
_BEZ_ROZKLADU = str.maketrans('łđø', 'ldo')


def _interfejs(s):
    return s in _PRZYCISKI or bool(_WZORY.match(s))


def oczysc(tekst):
    linie = [s.strip() for s in tekst.split('\n')]
    male = [s.lower() for s in linie]
    # Układ Facebooka: nazwa strony, potem znacznik "Sponsored" -> treść zaczyna się po znaczniku
    for k in range(min(3, len(male))):
        if k and re.match(r'spon[sz]or', male[k]):
            linie, male = linie[k + 1:], male[k + 1:]
            break
    return '\n'.join(s for s, m in zip(linie, male) if s and not _interfejs(m))


def normalizuj(tekst):
    # Reklamy oszustów omijają filtry słów kluczowych stylizowanymi literami Unicode, literami łudząco podobnymi
    # i niewidocznymi znakami, a często gubią polskie znaki. Model widzi każdą taką pisownię jako zwykłą.
    t = unicodedata.normalize('NFKC', tekst).lower()
    t = _NIEWIDOCZNE.sub('', t).translate(_PODOBNE)
    t = ''.join(z for z in unicodedata.normalize('NFD', t) if not unicodedata.combining(z))
    return t.translate(_BEZ_ROZKLADU)
