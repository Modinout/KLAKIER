import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { pobierzProgi } from '../api.js'
import { OPISY, ileAlarmow, ilePrzeoczonych, liczba } from '../nazwy.js'
import BliskoProgu from '../czesci/BliskoProgu.jsx'
import Uczenie from '../czesci/Uczenie.jsx'
import WykresProgow from '../czesci/WykresProgow.jsx'

function Progi({ progi, prog, ustawProg, wiersze }) {
  const wartosci = progi.progi.map((p) => p.prog)
  const krok = Math.round((wartosci[1] - wartosci[0]) * 100) / 100
  const punkty = progi.progi.map((p) => ({
    prog: p.prog,
    przeoczone: Math.round(progi.oszustw - p.zlapane),
    alarmy: Math.round(p.falszywe_alarmy),
  }))
  const punkt = punkty.find((p) => Math.abs(p.prog - prog) < 0.001)

  return (
    <div className="max-w-4xl rounded-lg border">
      <div className="p-6">
        <div className="mb-4 flex items-baseline justify-between">
          <span className="font-medium">Symulacja progu</span>
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
        <h2 className="mb-2 font-medium">Test na {liczba(progi.oszustw + progi.uczciwych)} reklamach z etykietą</h2>
        <WykresProgow punkty={punkty} prog={prog} oszustw={progi.oszustw} uczciwych={progi.uczciwych} />
        <p className="mt-3">
          Przy progu {liczba(prog)}: {ilePrzeoczonych(punkt.przeoczone)}, {ileAlarmow(punkt.alarmy)}.
        </p>
      </div>
      <div className="border-t p-6">
        <BliskoProgu wiersze={wiersze} prog={prog} />
      </div>
      <div className="border-t p-6">
        <p className="text-muted-foreground">{OPISY.suwak}</p>
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
      <h1 className="mb-1 text-2xl font-bold tracking-tight">Kalibracja</h1>
      <p className="mb-5 text-muted-foreground">{OPISY.kalibracja}</p>
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
        <h2 className="mb-1 font-medium">Douczanie modelu KAPSEL</h2>
        <Uczenie decyzje={wiersze.filter((r) => r.werdykt_analityka).length} odswiez={odswiez} />
      </div>
    </>
  )
}
