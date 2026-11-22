# Druga opinia dużego modelu o jednej reklamie.
import duzy_model

WERDYKTY = ('ok', 'do_sprawdzenia', 'oszustwo')
PROSBA = (
    'Oceniasz reklamę dla urzędu nadzoru finansowego. Możliwe werdykty: ok (zwykła reklama albo uczciwa oferta finansowa), '
    'do_sprawdzenia (oferta inwestycyjna bez ostrzeżenia o ryzyku, z obietnicą zysku albo od nieznanej firmy), '
    'oszustwo (podszycie pod znaną markę lub osobę, gwarantowany albo nierealny zysk, presja czasu). '
    'Odpowiedz samym obiektem JSON: {"werdykt": "...", "uzasadnienie": "jedno zdanie po polsku"}.'
    '\n\nTekst reklamy:\n'
)


def ocen(tekst):
    wynik = duzy_model.obiekt_json(duzy_model.zapytaj(PROSBA + tekst, temperature=0, max_tokens=300))
    if wynik['werdykt'] not in WERDYKTY:
        raise ValueError('Nieznany werdykt: ' + str(wynik['werdykt']))
    return {'werdykt': wynik['werdykt'], 'uzasadnienie': wynik['uzasadnienie']}
