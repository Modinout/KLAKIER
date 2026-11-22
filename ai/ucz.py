# Uczy model werdyktu na każdej reklamie (oszustwo lub nie), a model rodzaju oszustwa na reklamach z nazwanym rodzajem oraz
# na reklamach, które nie są oszustwami. Te uczą go, kiedy nie nazywać rodzaju; oszustwo bez rodzaju niczego go nie uczy.
import json
import pathlib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline, make_union

import dopisane
from tekst import normalizuj

REKLAMY = pathlib.Path(__file__).parent / 'dane' / 'reklamy.jsonl'
BEZ_RODZAJU = ''


def wiersze():
    with REKLAMY.open(encoding='utf-8') as plik:
        return [json.loads(linia) for linia in plik] + dopisane.czytaj()


def _model_werdyktu():
    # Fragmenty znaków przeżywają sztuczki z pisownią i błędy OCR, a słowa i pary słów niosą frazy.
    znaki = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 5), sublinear_tf=True, min_df=2, preprocessor=normalizuj)
    slowa = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), sublinear_tf=True, min_df=2, preprocessor=normalizuj,
                            token_pattern=r'(?u)\b\w+\b')
    return make_pipeline(make_union(znaki, slowa), LogisticRegression(C=20.0, max_iter=5000, class_weight='balanced'))


def _model_rodzaju():
    return make_pipeline(TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 5), sublinear_tf=True, min_df=2),
                         LogisticRegression(C=20.0, max_iter=3000, class_weight='balanced'))


def ucz():
    dane = wiersze()
    do_rodzaju = [w for w in dane if w['rodzaj'] or w['werdykt'] != 'oszustwo']
    model_werdyktu = _model_werdyktu().fit([w['tekst'] for w in dane],
                                           ['oszustwo' if w['werdykt'] == 'oszustwo' else 'inne' for w in dane])
    model_rodzaju = _model_rodzaju().fit([w['tekst'] for w in do_rodzaju], [w['rodzaj'] or BEZ_RODZAJU for w in do_rodzaju])
    return model_werdyktu, model_rodzaju
