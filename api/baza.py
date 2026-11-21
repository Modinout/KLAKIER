import os

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


def polacz():
    return psycopg.connect(os.environ['BAZA_URL'], row_factory=dict_row)


def dodaj(reklama, ocena):
    """Returns the stored row, or None when this ad (zrodlo + id_zrodla) is already stored."""
    pola = {**reklama, **ocena, 'sygnaly': Jsonb(ocena['sygnaly'])}
    with polacz() as baza:
        return baza.execute(
            """
            INSERT INTO reklamy (zrodlo, id_zrodla, platforma, url, reklamodawca, tekst, zebrano,
                                 werdykt, ryzyko, pewny, sygnaly)
            VALUES (%(zrodlo)s, %(id_zrodla)s, %(platforma)s, %(url)s, %(reklamodawca)s, %(tekst)s, %(zebrano)s,
                    %(werdykt)s, %(ryzyko)s, %(pewny)s, %(sygnaly)s)
            ON CONFLICT (zrodlo, id_zrodla) DO NOTHING
            RETURNING *
            """,
            pola,
        ).fetchone()


def lista(werdykt, status, min_ryzyko):
    with polacz() as baza:
        return baza.execute(
            """
            SELECT * FROM reklamy
            WHERE (%(werdykt)s::text IS NULL OR werdykt = %(werdykt)s)
              AND (%(status)s::text IS NULL OR status = %(status)s)
              AND ryzyko >= %(min_ryzyko)s
            ORDER BY ryzyko DESC
            """,
            {'werdykt': werdykt, 'status': status, 'min_ryzyko': min_ryzyko},
        ).fetchall()


def jedna(id):
    with polacz() as baza:
        return baza.execute('SELECT * FROM reklamy WHERE id = %s', [id]).fetchone()


def zmien_status(id, status):
    with polacz() as baza:
        return baza.execute('UPDATE reklamy SET status = %s WHERE id = %s RETURNING *', [status, id]).fetchone()
