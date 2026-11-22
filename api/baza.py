import os

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


def polacz():
    return psycopg.connect(os.environ['BAZA_URL'], row_factory=dict_row)


def kolumny_oceny(ocena):
    return {**ocena, 'sygnaly': Jsonb(ocena['sygnaly']), 'powody': Jsonb(ocena['powody']),
            'rejestr': Jsonb(ocena['rejestr']) if ocena['rejestr'] else None}


def jest(zrodlo, id_zrodla):
    with polacz() as baza:
        return baza.execute(
            'SELECT 1 FROM reklamy WHERE zrodlo = %s AND id_zrodla = %s', [zrodlo, id_zrodla]
        ).fetchone() is not None


def dodaj(reklama, ocena, drugi_sedzia):
    """Returns the stored row, or None when this ad (zrodlo + id_zrodla) is already stored."""
    pola = {**reklama, **kolumny_oceny(ocena), 'sygnaly_zbieracza': Jsonb(reklama['sygnaly']),
            'drugi_sedzia': Jsonb(drugi_sedzia) if drugi_sedzia else None}
    with polacz() as baza:
        return baza.execute(
            """
            INSERT INTO reklamy (zrodlo, id_zrodla, platforma, url, domena, reklamodawca, tekst, zebrano, opublikowano,
                                 sygnaly_zbieracza,
                                 werdykt, ryzyko, pewny, rejestr, sygnaly, powody, rodzaj, drugi_sedzia)
            VALUES (%(zrodlo)s, %(id_zrodla)s, %(platforma)s, %(url)s, %(domena)s, %(reklamodawca)s, %(tekst)s,
                    %(zebrano)s, %(opublikowano)s, %(sygnaly_zbieracza)s,
                    %(werdykt)s, %(ryzyko)s, %(pewny)s, %(rejestr)s, %(sygnaly)s, %(powody)s, %(rodzaj)s, %(drugi_sedzia)s)
            ON CONFLICT (zrodlo, id_zrodla) DO NOTHING
            RETURNING *
            """,
            pola,
        ).fetchone()


def lista(werdykt, status, min_ryzyko, od):
    with polacz() as baza:
        return baza.execute(
            """
            SELECT * FROM reklamy
            WHERE (%(werdykt)s::text IS NULL OR werdykt = %(werdykt)s)
              AND (%(status)s::text IS NULL OR status = %(status)s)
              AND ryzyko >= %(min_ryzyko)s
              AND (%(od)s::timestamptz IS NULL OR dodano > %(od)s)
            ORDER BY ryzyko DESC
            """,
            {'werdykt': werdykt, 'status': status, 'min_ryzyko': min_ryzyko, 'od': od},
        ).fetchall()


def jedna(id):
    with polacz() as baza:
        return baza.execute('SELECT * FROM reklamy WHERE id = %s', [id]).fetchone()


def zmien(id, zmiany):
    # Column names come from the fields of ZmianaReklamy, never from the request text.
    ustaw = ', '.join(f'{pole} = %({pole})s' for pole in zmiany)
    with polacz() as baza:
        return baza.execute(f'UPDATE reklamy SET {ustaw} WHERE id = %(id)s RETURNING *', {**zmiany, 'id': id}).fetchone()


def podobne(id):
    """Raises psycopg.errors.QueryCanceled when the search runs over 5 s."""
    with polacz() as baza:
        # Trigram similarity of whole long texts (pages, video descriptions) takes tens of seconds.
        baza.execute("SET LOCAL statement_timeout = '5s'")
        return baza.execute(
            """
            SELECT inna.*, similarity(left(inna.tekst, 1000), left(ta.tekst, 1000)) AS podobienstwo
            FROM reklamy ta JOIN reklamy inna ON inna.id <> ta.id
            WHERE ta.id = %s AND similarity(left(inna.tekst, 1000), left(ta.tekst, 1000)) >= 0.5
            ORDER BY podobienstwo DESC
            LIMIT 50
            """,
            [id],
        ).fetchall()


def platnicy_domen():
    # Ordered by id so the first stored spelling of a payer's name is the one shown.
    with polacz() as baza:
        return baza.execute(
            """
            SELECT domena, reklamodawca, rejestr->>'stan' AS stan FROM reklamy
            WHERE domena IS NOT NULL AND reklamodawca IS NOT NULL
            ORDER BY id
            """
        ).fetchall()


def przyklady_analityka():
    with polacz() as baza:
        return baza.execute(
            'SELECT tekst, werdykt_analityka AS werdykt FROM reklamy WHERE werdykt_analityka IS NOT NULL'
        ).fetchall()


def do_oceny():
    with polacz() as baza:
        return baza.execute('SELECT id, tekst, reklamodawca, url, zrodlo FROM reklamy').fetchall()


def zapisz_oceny(oceny):
    """oceny: one dict per ad with its id and a fresh answer of ai /ocen."""
    with polacz() as baza:
        baza.cursor().executemany(
            """
            UPDATE reklamy
            SET werdykt = %(werdykt)s, ryzyko = %(ryzyko)s, pewny = %(pewny)s, rejestr = %(rejestr)s,
                sygnaly = %(sygnaly)s, powody = %(powody)s, rodzaj = %(rodzaj)s
            WHERE id = %(id)s
            """,
            [kolumny_oceny(ocena) for ocena in oceny],
        )


def zapisz_tekst(id, tekst):
    with polacz() as baza:
        baza.execute('UPDATE reklamy SET tekst = %s WHERE id = %s', [tekst, id])


def zapisz_obraz(id, typ, dane):
    """Replaces an earlier picture of the ad and returns the ad."""
    with polacz() as baza:
        baza.execute(
            """
            INSERT INTO obrazy_reklam (reklama_id, typ, dane) VALUES (%s, %s, %s)
            ON CONFLICT (reklama_id) DO UPDATE SET typ = EXCLUDED.typ, dane = EXCLUDED.dane
            """,
            [id, typ, dane],
        )
        return baza.execute('UPDATE reklamy SET ma_obraz = true WHERE id = %s RETURNING *', [id]).fetchone()


def obraz(id):
    with polacz() as baza:
        return baza.execute('SELECT typ, dane FROM obrazy_reklam WHERE reklama_id = %s', [id]).fetchone()


def zapisz_strone(domena, pomiar):
    """Replaces an earlier measurement of the domain and returns the stored row."""
    widoki = {nazwa: Jsonb(widok) if widok else None for nazwa, widok in pomiar.items()}
    with polacz() as baza:
        return baza.execute(
            """
            INSERT INTO strony (domena, zmierzono, komputer, telefon)
            VALUES (%(domena)s, now(), %(komputer)s, %(telefon)s)
            ON CONFLICT (domena) DO UPDATE
            SET zmierzono = EXCLUDED.zmierzono, komputer = EXCLUDED.komputer, telefon = EXCLUDED.telefon
            RETURNING *
            """,
            {'domena': domena, **widoki},
        ).fetchone()


def strony():
    """Measured landing pages by domain."""
    with polacz() as baza:
        return {strona['domena']: strona for strona in baza.execute('SELECT * FROM strony').fetchall()}


def dodaj_sprawdzenie(url):
    with polacz() as baza:
        return baza.execute('INSERT INTO sprawdzenia (url) VALUES (%s) RETURNING id', [url]).fetchone()['id']


def usun_sprawdzenie(id):
    with polacz() as baza:
        baza.execute('DELETE FROM sprawdzenia WHERE id = %s', [id])


def sprawdzenie(id):
    with polacz() as baza:
        return baza.execute('SELECT stan, reklama_id, blad FROM sprawdzenia WHERE id = %s', [id]).fetchone()


def zapisz_sprawdzenie(id, stan):
    with polacz() as baza:
        return baza.execute(
            """
            UPDATE sprawdzenia SET stan = %(stan)s, reklama_id = %(reklama_id)s, blad = %(blad)s WHERE id = %(id)s
            RETURNING stan, reklama_id, blad
            """,
            {**stan, 'id': id},
        ).fetchone()


# A visit without its files, with the hashes of both files in one object.
POLA_DOWODU = "id, kiedy, rodzaj, adres, lancuch, json_build_object('obraz', sha256_obrazu, 'html', sha256_html) AS sha256"


def dodaj_dowod(reklama_id, dowod):
    with polacz() as baza:
        return baza.execute(
            f"""
            INSERT INTO dowody (reklama_id, kiedy, rodzaj, adres, lancuch, obraz, html, sha256_obrazu, sha256_html)
            VALUES (%(reklama_id)s, %(kiedy)s, %(rodzaj)s, %(adres)s, %(lancuch)s, %(obraz)s, %(html)s,
                    %(sha256_obrazu)s, %(sha256_html)s)
            RETURNING {POLA_DOWODU}
            """,
            {**dowod, 'reklama_id': reklama_id, 'lancuch': Jsonb(dowod['lancuch'])},
        ).fetchone()


def dowody(reklama_id):
    with polacz() as baza:
        return baza.execute(f'SELECT {POLA_DOWODU} FROM dowody WHERE reklama_id = %s ORDER BY id', [reklama_id]).fetchall()


def dowod(id):
    """One visit with its files."""
    with polacz() as baza:
        return baza.execute('SELECT * FROM dowody WHERE id = %s', [id]).fetchone()


def dowody_z_plikami(reklama_id):
    with polacz() as baza:
        return baza.execute('SELECT * FROM dowody WHERE reklama_id = %s ORDER BY id', [reklama_id]).fetchall()
