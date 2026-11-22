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
    notatka       TEXT,
    ma_obraz      BOOLEAN NOT NULL DEFAULT false,
    UNIQUE (zrodlo, id_zrodla)
);

-- Pictures live apart so that the ad lists do not carry their bytes.
CREATE TABLE obrazy_reklam (
    reklama_id    INTEGER PRIMARY KEY REFERENCES reklamy(id) ON DELETE CASCADE,
    typ           TEXT NOT NULL,
    dane          BYTEA NOT NULL
);

-- The risk warning on landing pages as the collector measured it; the api turns it into findings on each read.
CREATE TABLE strony (
    domena        TEXT PRIMARY KEY,
    zmierzono     TIMESTAMPTZ NOT NULL,
    komputer      JSONB,
    telefon       JSONB
);

CREATE TABLE historia (
    id            SERIAL PRIMARY KEY,
    reklama_id    INTEGER NOT NULL REFERENCES reklamy(id) ON DELETE CASCADE,
    kiedy         TIMESTAMPTZ NOT NULL DEFAULT now(),
    kto           TEXT NOT NULL,
    co            TEXT NOT NULL
);
CREATE INDEX historia_reklama_id ON historia (reklama_id);

-- Settings the analysts change in the panel, in a single row.
CREATE TABLE ustawienia (
    id            INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    prog          DOUBLE PRECISION NOT NULL
);
-- The text model's own scam threshold, so the levels stay as the model's verdicts until someone changes it.
INSERT INTO ustawienia (prog) VALUES (0.7);

-- Registration dates of landing domains by RDAP, as the collector found them; the api turns them into findings on
-- each read.
CREATE TABLE domeny (
    domena        TEXT PRIMARY KEY,
    zarejestrowano DATE NOT NULL,
    sprawdzono    TIMESTAMPTZ NOT NULL
);

-- Links an analyst pasted in the panel; the robotnik checks them one by one.
CREATE TABLE sprawdzenia (
    id            SERIAL PRIMARY KEY,
    url           TEXT NOT NULL,
    zlecono       TIMESTAMPTZ NOT NULL DEFAULT now(),
    stan          TEXT NOT NULL DEFAULT 'w_kolejce',
    reklama_id    INTEGER REFERENCES reklamy(id) ON DELETE SET NULL,
    blad          TEXT
);

-- What the browser saw on each visit of a checked link. Rows are only added, so a record keeps every visit.
CREATE TABLE dowody (
    id            SERIAL PRIMARY KEY,
    reklama_id    INTEGER NOT NULL REFERENCES reklamy(id) ON DELETE CASCADE,
    kiedy         TIMESTAMPTZ NOT NULL,
    rodzaj        TEXT NOT NULL,
    adres         TEXT NOT NULL,
    lancuch       JSONB NOT NULL,
    obraz         BYTEA NOT NULL,
    html          BYTEA NOT NULL,
    sha256_obrazu TEXT NOT NULL,
    sha256_html   TEXT NOT NULL
);
