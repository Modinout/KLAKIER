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
    mowa          TEXT,
    zebrano      TIMESTAMPTZ NOT NULL,
    opublikowano  DATE,
    dodano        TIMESTAMPTZ NOT NULL DEFAULT now(),
    werdykt       TEXT NOT NULL,
    ryzyko        REAL NOT NULL,
    pewny         BOOLEAN NOT NULL,
    rejestr       JSONB,
    sygnaly       JSONB NOT NULL DEFAULT '[]',
    -- Osobno od sygnaly, które każda ponowna ocena nadpisuje.
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

-- Obrazy leżą osobno, żeby listy reklam nie niosły ich bajtów.
CREATE TABLE obrazy_reklam (
    reklama_id    INTEGER PRIMARY KEY REFERENCES reklamy(id) ON DELETE CASCADE,
    typ           TEXT NOT NULL,
    dane          BYTEA NOT NULL
);

-- Ostrzeżenie o ryzyku na stronach docelowych tak, jak zmierzył je zbieracz; api zamienia je w ustalenia
-- przy każdym odczycie.
CREATE TABLE strony (
    domena        TEXT PRIMARY KEY,
    zmierzono     TIMESTAMPTZ NOT NULL,
    komputer      JSONB,
    tablet        JSONB,
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

-- Ustawienia zmieniane przez analityków w panelu, w jednym wierszu.
CREATE TABLE ustawienia (
    id            INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    prog          DOUBLE PRECISION NOT NULL
);
-- Własny próg oszustwa modelu tekstowego, więc poziomy pozostają werdyktami modelu, dopóki ktoś go nie zmieni.
INSERT INTO ustawienia (prog) VALUES (0.7);

-- Daty rejestracji domen docelowych według RDAP, tak jak znalazł je zbieracz; api zamienia je w ustalenia przy
-- każdym odczycie.
CREATE TABLE domeny (
    domena        TEXT PRIMARY KEY,
    zarejestrowano DATE NOT NULL,
    sprawdzono    TIMESTAMPTZ NOT NULL
);

-- Linki wklejone przez analityka w panelu; robotnik sprawdza je po kolei.
CREATE TABLE sprawdzenia (
    id            SERIAL PRIMARY KEY,
    url           TEXT NOT NULL,
    zlecono       TIMESTAMPTZ NOT NULL DEFAULT now(),
    stan          TEXT NOT NULL DEFAULT 'w_kolejce',
    reklama_id    INTEGER REFERENCES reklamy(id) ON DELETE SET NULL,
    blad          TEXT
);

-- To, co przeglądarka zobaczyła przy każdej wizycie sprawdzanego linku. Wiersze są tylko dodawane,
-- więc rekord zachowuje każdą wizytę.
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
