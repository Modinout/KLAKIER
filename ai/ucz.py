# Trains the verdict model on every ad, and the scam type model on the ads with a named type plus the ads
# that are not scams. Those teach it when to name no type; a scam without a type teaches it nothing.
import json
import pathlib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

import dopisane

REKLAMY = pathlib.Path(__file__).parent / 'dane' / 'reklamy.jsonl'
BEZ_RODZAJU = ''


def wiersze():
    with REKLAMY.open(encoding='utf-8') as plik:
        return [json.loads(linia) for linia in plik] + dopisane.czytaj()


def _nowy_model():
    return make_pipeline(TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 5), sublinear_tf=True, min_df=2),
                         LogisticRegression(C=20.0, max_iter=3000, class_weight='balanced'))


def ucz():
    dane = wiersze()
    do_rodzaju = [w for w in dane if w['rodzaj'] or w['werdykt'] != 'oszustwo']
    model_werdyktu = _nowy_model().fit([w['tekst'] for w in dane], [w['werdykt'] for w in dane])
    model_rodzaju = _nowy_model().fit([w['tekst'] for w in do_rodzaju], [w['rodzaj'] or BEZ_RODZAJU for w in do_rodzaju])
    return model_werdyktu, model_rodzaju
