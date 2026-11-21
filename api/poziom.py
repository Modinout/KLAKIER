# One risk level per record, from all that is known about it: collector findings, register and text rules, the model.
# A hard fact alone makes a record high. A breach of the advertising rules by a listed firm makes it medium,
# and so does a licensed brand paid for by another of its own companies: a formal mismatch, not a missing licence.
WYSOKIE = {
    'reklama_domeny_z_ostrzezenia_knf', 'druga_domena_ostrzezonej_strony', 'wielu_platnikow_domeny',
    'platnik_poza_listami', 'doradztwo_bez_zezwolenia',
}
# Notes describe a finding and are not one themselves.
NOTATKI = {'brak_na_liscie_cert', 'na_liscie_cert'}


def poziom(sygnaly, werdykt, rodzaj):
    """Returns (level, reason): the strongest finding decides and its description is the reason."""
    for sygnal in sygnaly:
        if sygnal['kod'] in WYSOKIE:
            return 'wysokie', sygnal['opis']
    if werdykt == 'oszustwo':
        return 'wysokie', 'Treść typowa dla fałszywych inwestycji' + (f': {rodzaj}.' if rodzaj else '.')
    for sygnal in sygnaly:
        if sygnal['kod'] not in NOTATKI:
            return 'srednie', sygnal['opis']
    # An unsure model alone names no rule and quotes nothing, so it raises no level.
    return 'niskie', None
