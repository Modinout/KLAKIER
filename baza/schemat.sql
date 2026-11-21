CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE reklamy (
    id            SERIAL PRIMARY KEY,
    zrodlo        TEXT NOT NULL,
    id_zrodla     TEXT NOT NULL,
    platforma     TEXT NOT NULL,
    url           TEXT,
    domena        TEXT,
    reklamodawca  TEXT,
    tekst         TEXT NOT NULL,
    zebrano       TIMESTAMPTZ NOT NULL,
    opublikowano  DATE,
    dodano        TIMESTAMPTZ NOT NULL DEFAULT now(),
    werdykt       TEXT NOT NULL,
    ryzyko        REAL NOT NULL,
    pewny         BOOLEAN NOT NULL,
    rejestr       JSONB,
    sygnaly       JSONB NOT NULL DEFAULT '[]',
    -- Kept apart from sygnaly, which every re-score overwrites.
    sygnaly_zbieracza JSONB NOT NULL DEFAULT '[]',
    powody        JSONB NOT NULL DEFAULT '[]',
    rodzaj        TEXT,
    drugi_sedzia  JSONB,
    status        TEXT NOT NULL DEFAULT 'nowa',
    werdykt_analityka TEXT,
    ma_obraz      BOOLEAN NOT NULL DEFAULT false,
    UNIQUE (zrodlo, id_zrodla)
);

-- Pictures live apart so that the ad lists do not carry their bytes.
CREATE TABLE obrazy_reklam (
    reklama_id    INTEGER PRIMARY KEY REFERENCES reklamy(id) ON DELETE CASCADE,
    typ           TEXT NOT NULL,
    dane          BYTEA NOT NULL
);
