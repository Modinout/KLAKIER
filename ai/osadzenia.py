# Zamienia tekst reklamy na krótki wektor, żeby podobne reklamy i powtórki dało się znaleźć kosinusem.
#   from osadzenia import osadz
#   osadz('Zainwestuj 900 zł i zarabiaj 20 000 zł miesięcznie') -> 64 numbers of unit length
import json

from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer

from tekst import oczysc
from ucz import REKLAMY

WYMIARY = 64

# Dopasowany raz na pliku dostarczonym z usługą i już nigdy więcej: wektory zapisane wcześniej
# pozostają porównywalne z nowymi, gdy klasyfikator uczy się od analityków.
with REKLAMY.open(encoding='utf-8') as _plik:
    _teksty = [json.loads(linia)['tekst'] for linia in _plik if linia.strip()]
_model = make_pipeline(
    TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 5), sublinear_tf=True, min_df=2),
    TruncatedSVD(n_components=WYMIARY, random_state=0),
    Normalizer(),
).fit(_teksty)


def osadz(tekst):
    """Wektor jednostkowy tekstu albo None, gdy nie ma tekstu do umieszczenia."""
    tekst = oczysc(tekst)
    if not tekst.strip():
        return None
    return [round(float(x), 4) for x in _model.transform([tekst])[0]]
