CREATE TABLE reklamy (
    id            SERIAL PRIMARY KEY,
    zrodlo        TEXT NOT NULL,
    id_zrodla     TEXT NOT NULL,
    platforma     TEXT NOT NULL,
    url           TEXT,
    reklamodawca  TEXT,
    tekst         TEXT NOT NULL,
    zebrano       TIMESTAMPTZ NOT NULL,
    dodano        TIMESTAMPTZ NOT NULL DEFAULT now(),
    werdykt       TEXT NOT NULL,
    ryzyko        REAL NOT NULL,
    pewny         BOOLEAN NOT NULL,
    sygnaly       JSONB NOT NULL DEFAULT '[]',
    status        TEXT NOT NULL DEFAULT 'nowa',
    UNIQUE (zrodlo, id_zrodla)
);
