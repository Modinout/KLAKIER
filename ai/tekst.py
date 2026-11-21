# Shared text cleaning for training (zbuduj.py) and prediction (przewidz.py): removes what tells the SOURCE of an ad
# rather than its message (interface buttons, the "page name / Sponsored" header, Ad Library id lines).
import re

_PRZYCISKI = {'learn more', 'see details', 'sign up', 'download', 'install now', 'install', 'like page', 'financial service', 'open',
              'shop now', 'apply now', 'dowiedz się więcej', 'więcej informacji', 'zarejestruj się', 'pobierz', 'zainstaluj', 'otwórz',
              'sprawdź', 'visit advertiser', 'skip', 'obejrzyj w youtube', 'active', 'różne wersje tej reklamy'}
_WZORY = re.compile(r'^(spon[sz]or\w*|dowiedz się\W*|więcej infor\w*\W*|identyfikator\b.*|library id\b.*|[\d,. ]+ people like this)$')


def _interfejs(s):
    return s in _PRZYCISKI or bool(_WZORY.match(s))


def oczysc(tekst):
    linie = [s.strip() for s in tekst.split('\n')]
    male = [s.lower() for s in linie]
    # Facebook layout: page name, then the "Sponsored" marker -> the message starts after the marker
    for k in range(min(3, len(male))):
        if k and re.match(r'spon[sz]or', male[k]):
            linie, male = linie[k + 1:], male[k + 1:]
            break
    return '\n'.join(s for s, m in zip(linie, male) if s and not _interfejs(m))
