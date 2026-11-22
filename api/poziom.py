# One risk level per record, from all that is known about it: collector findings, register and text rules, the model.
# A hard fact alone makes a record high; a breach of the advertising rules by a listed firm makes it medium.
WYSOKIE = {
    'reklama_domeny_z_ostrzezenia_knf', 'druga_domena_ostrzezonej_strony', 'wielu_platnikow_domeny',
    'platnik_poza_listami', 'doradztwo_bez_zezwolenia', 'obca_domena', 'na_liscie_csirt_knf',
}
# Notes describe a finding and are not one themselves. A licensed brand paid for by another of its own
# companies is a formal mismatch an analyst would dismiss; that company paying for another brand's domain is high.
NOTATKI = {'brak_na_liscie_cert', 'na_liscie_cert', 'platnik_spoza_rejestru'}
# Payers on a KNF list or in the MiCA register: the text model alone does not make their ad high.
LICENCJE = {'w_rejestrze', 'tfi', 'bank', 'mica'}


def poziom(sygnaly, ponad_progiem, rodzaj, rejestr):
    """Returns (level, reason): the strongest finding decides and its description is the reason.

    ponad_progiem: the text model's risk is at the threshold of GET /prog or over it.
    """
    for sygnal in sygnaly:
        if sygnal['kod'] in WYSOKIE:
            return 'wysokie', sygnal['opis']
    if ponad_progiem and rejestr and rejestr['stan'] in LICENCJE:
        return 'srednie', ('Treść typowa dla fałszywych inwestycji, ale płatnik jest na liście KNF '
                           'lub w rejestrze MiCA: do sprawdzenia.')
    if ponad_progiem:
        return 'wysokie', 'Treść typowa dla fałszywych inwestycji' + (f': {rodzaj}.' if rodzaj else '.')
    for sygnal in sygnaly:
        if sygnal['kod'] not in NOTATKI:
            return 'srednie', sygnal['opis']
    # An unsure model alone names no rule and quotes nothing, so it raises no level.
    return 'niskie', None
