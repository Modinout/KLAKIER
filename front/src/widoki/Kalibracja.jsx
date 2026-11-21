import { useEffect, useMemo, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { pobierzProgi } from '../api.js'
import { liczba } from '../nazwy.js'
import Uczenie from '../czesci/Uczenie.jsx'

function Liczba({ tytul, wartosc, zIlu }) {
  return (
    <div>
      <p className="text-muted-foreground">{tytul}</p>
      <p className="mt-1 text-2xl font-semibold tracking-tight tabular-nums">
        {liczba(wartosc)}
        {zIlu !== undefined && <span className="text-base font-normal text-muted-foreground"> z {liczba(zIlu)}</span>}
      </p>
    </div>
  )
}

function Progi({ progi, prog, ustawProg, wiersze }) {
  const wartosci = progi.progi.map((p) => p.prog)
  const krok = Math.round((wartosci[1] - wartosci[0]) * 100) / 100
  const wiersz = progi.progi.find((p) => Math.abs(p.prog - prog) < 0.001)
  const zlapane = Math.round(wiersz?.zlapane ?? 0)
  const odProgu = useMemo(() => wiersze.filter((r) => r.ryzyko >= prog).length, [wiersze, prog])

  return (
    <div className="max-w-4xl rounded-lg border">
      <div className="p-6">
        <div className="mb-4 flex items-baseline justify-between">
          <span className="font-medium">Próg modelu</span>
          <span className="font-semibold tabular-nums">{liczba(prog)}</span>
        </div>
        <Slider
          min={wartosci[0]}
          max={wartosci.at(-1)}
          step={krok}
          value={[prog]}
          onValueChange={([v]) => ustawProg(Math.round(v * 100) / 100)}
        />
        <div className="mt-2 flex justify-between text-xs text-muted-foreground tabular-nums">
          <span>{liczba(wartosci[0])}</span>
          <span>{liczba(wartosci.at(-1))}</span>
        </div>
      </div>
      <div className="border-t p-6">
        <p className="mb-3 text-xs font-medium text-muted-foreground">Na zbiorze testowym</p>
        <div className="grid grid-cols-3 gap-6">
          <Liczba tytul="Złapane oszustwa" wartosc={zlapane} zIlu={progi.oszustw} />
          <Liczba tytul="Przeoczone oszustwa" wartosc={progi.oszustw - zlapane} zIlu={progi.oszustw} />
          <Liczba tytul="Fałszywe alarmy" wartosc={Math.round(wiersz?.falszywe_alarmy ?? 0)} zIlu={progi.uczciwych} />
        </div>
      </div>
      <div className="border-t p-6">
        <Liczba tytul="Reklamy w bazie od tego progu" wartosc={odProgu} />
      </div>
    </div>
  )
}

export default function Kalibracja({ prog, ustawProg, wiersze, odswiez }) {
  const [progi, setProgi] = useState(null)
  const [blad, setBlad] = useState(false)

  function wczytaj() {
    setBlad(false)
    pobierzProgi()
      .then(setProgi)
      .catch(() => setBlad(true))
  }

  useEffect(wczytaj, [])

  return (
    <>
      <h1 className="mb-5 text-2xl font-bold tracking-tight">Kalibracja</h1>
      {blad && (
        <div className="flex max-w-4xl items-center justify-between rounded-lg border p-6">
          <p>Nie udało się wczytać progów. Spróbuj ponownie.</p>
          <Button variant="outline" onClick={wczytaj}>
            Spróbuj ponownie
          </Button>
        </div>
      )}
      {!blad && !progi && <p className="text-muted-foreground">Wczytywanie…</p>}
      {!blad && progi && <Progi progi={progi} prog={prog} ustawProg={ustawProg} wiersze={wiersze} />}
      <div className="mt-6 max-w-4xl rounded-lg border p-6">
        <h2 className="mb-3 font-medium">Uczenie modelu</h2>
        <Uczenie decyzje={wiersze.filter((r) => r.werdykt_analityka).length} odswiez={odswiez} />
      </div>
    </>
  )
}
