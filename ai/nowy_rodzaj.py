# Nowy rodzaj oszustwa z opisu w jednym zdaniu: duży model pisze przykładowe reklamy, małe modele się ich uczą.
import dopisane
import duzy_model
from przewidz import przeucz
from tekst import oczysc

NAJMNIEJ_REKLAM = 5
STYLE = (
    'Krótkie teksty, od jednego do trzech zdań.',
    'Dłuższe teksty, od czterech do ośmiu zdań, część z wyliczeniami albo emoji.',
)
PROSBA = (
    'Budujemy dla urzędu nadzoru finansowego klasyfikator, który wykrywa oszukańcze reklamy inwestycyjne, '
    'i potrzebujemy przykładów treningowych. Napisz 10 różnych tekstów reklam po polsku w formie posta sponsorowanego na Facebooku.\n'
    'Rodzaj: oszukańcza reklama: {opis}.\n'
    '{styl} Każdy tekst inny: inne otwarcie, inna długość, inne kwoty i nazwy. Zamiast nazwisk wstawiaj znacznik [znana osoba].\n'
    'Odpowiedz samym obiektem JSON: {{"reklamy": ["...", "..."]}}'
)


def napisz(opis):
    teksty = []
    for styl in STYLE:
        odpowiedz = duzy_model.obiekt_json(duzy_model.zapytaj(PROSBA.format(opis=opis, styl=styl), temperature=1.0, max_tokens=6000))
        # Model czasem przekręca nazwę klucza, więc bierzemy pierwszą listę, jakkolwiek się nazywa.
        reklamy = next((v for v in odpowiedz.values() if isinstance(v, list)), [])
        teksty += [oczysc(r) for r in reklamy if isinstance(r, str)]
    teksty = [t for t in teksty if t.strip()]
    if len(teksty) < NAJMNIEJ_REKLAM:
        raise ValueError(f'Duży model napisał tylko {len(teksty)} reklam.')
    return teksty


def dodaj(nazwa, teksty):
    dopisane.zapisz(dopisane.czytaj() + [{'tekst': t, 'werdykt': 'oszustwo', 'rodzaj': nazwa, 'pochodzenie': 'generator'} for t in teksty])
    przeucz()
