# Jeden poziom ryzyka na rekord, z wszystkiego, co o nim wiadomo: ustaleń zbieracza, rejestru, reguł tekstowych i modelu.
# Sam twardy fakt daje rekordowi poziom wysoki; naruszenie zasad reklamy przez firmę z rejestru daje średni.
WYSOKIE = {
    'reklama_domeny_z_ostrzezenia_knf', 'druga_domena_ostrzezonej_strony', 'wielu_platnikow_domeny',
    'platnik_poza_listami', 'doradztwo_bez_zezwolenia', 'obca_domena', 'na_liscie_csirt_knf',
}
# Notatki opisują ustalenie, same nim nie są. Licencjonowana marka opłacana przez inną firmę z własnej grupy
# to formalna niezgodność, którą analityk by odrzucił; ta firma płacąca za domenę innej marki to poziom wysoki.
NOTATKI = {'brak_na_liscie_cert', 'na_liscie_cert', 'platnik_spoza_rejestru'}
# Płatnicy z rejestru KNF lub MiCA: sam model tekstowy nie czyni ich reklamy wysoką.
LICENCJE = {'w_rejestrze', 'tfi', 'bank', 'mica'}


def poziom(sygnaly, ponad_progiem, rodzaj, rejestr):
    """Zwraca (poziom, powód): decyduje najsilniejsze ustalenie, a jego opis jest powodem.

    ponad_progiem: ryzyko modelu tekstowego jest równe progowi z GET /prog lub go przekracza.
    """
    for sygnal in sygnaly:
        if sygnal['kod'] in WYSOKIE:
            return 'wysokie', sygnal['opis']
    if ponad_progiem and rejestr and rejestr['stan'] in LICENCJE:
        return 'srednie', ('Treść typowa dla fałszywych inwestycji, ale płatnik jest w rejestrze KNF '
                           'lub MiCA: do sprawdzenia.')
    if ponad_progiem:
        return 'wysokie', 'Treść typowa dla fałszywych inwestycji' + (f': {rodzaj}.' if rodzaj else '.')
    for sygnal in sygnaly:
        if sygnal['kod'] not in NOTATKI:
            return 'srednie', sygnal['opis']
    # Niepewny model sam nie wskazuje żadnej reguły ani niczego nie cytuje, więc nie podnosi poziomu.
    return 'niskie', None
