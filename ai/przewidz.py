# Small CPU classifier for the ai service. Needs scikit-learn + joblib in the versions named in KARTA_MODELU.md.
#   from przewidz import przewidz
#   przewidz('Zainwestuj 900 zl i zarabiaj 20 000 zl miesiecznie')
#   -> {'werdykt': 'oszustwo', 'prawdopodobienstwa': {'ok': .., 'do_sprawdzenia': .., 'oszustwo': ..}, 'pewny': True}
# 'pewny' False = a person rates the ad.
import pathlib
import joblib
from tekst import oczysc

KLASY = ['ok', 'do_sprawdzenia', 'oszustwo']
PROG_PEWNOSCI = 0.7
_model = joblib.load(pathlib.Path(__file__).with_name('klasyfikator.joblib'))


def przewidz(tekst):
    tekst = oczysc(tekst)
    p = _model.predict_proba([tekst])[0]
    pr = {KLASY[k]: float(v) for k, v in zip(_model.classes_, p)}
    werdykt = max(pr, key=pr.get)
    return {'werdykt': werdykt, 'prawdopodobienstwa': pr, 'pewny': bool(tekst.strip()) and pr[werdykt] >= PROG_PEWNOSCI}
