import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { pobierzProg, pobierzProgi, zapiszProg } from '../api.js'
import { BLAD_ZAPISU, bezTresci, ileOszustw, ileReklam, ileUczciwych, liczba, procent } from '../nazwy.js'
import { ustalenia } from '../ustalenia.js'
import Uczenie from '../czesci/Uczenie.jsx'
import WykresProgow from '../czesci/WykresProgow.jsx'

function rowne(a, b) {
  return Math.abs(a - b) < 0.001
}

// Próg działa w kolejce tylko na ocenę modelu; reklamy z ustaleniami reguł zostają w „Do zrobienia”.
function zdanieKolejki(wiersze, prog, zapisany) {
  if (rowne(prog, zapisany)) return 'Próg ' + procent(prog) + ' działa teraz w kolejce.'
  if (prog < zapisany) {
    const n = wiersze.filter(
      (r) => !bezTresci(r) && r.zrodlo !== 'youtube' && r.ryzyko >= prog && r.ryzyko < zapisany && r.poziom !== 'wysokie'
    ).length
    const ile = ileReklam(n)
    if (n > 0) return 'Po zapisaniu progu ' + procent(prog) + ' do „Do zrobienia” ' + (ile.endsWith('reklamy') ? 'trafią' : 'trafi') + ' jeszcze ' + ile + '.'
  } else {
    const n = wiersze.filter(
      (r) => r.poziom === 'wysokie' && ustalenia(r).length === 0 && r.ryzyko >= zapisany && r.ryzyko < prog
    ).length
    const ile = ileReklam(n)
    if (n > 0) return 'Po zapisaniu progu ' + procent(prog) + ' z „Do zrobienia” ' + (ile.endsWith('reklamy') ? 'wypadną' : 'wypadnie') + ' ' + ile + '.'
  }
  return 'Przy progu ' + procent(prog) + ' kolejka się nie zmieni.'
}

function Kafelek({ tytul, ile, z, kolor, dopisek }) {
  return (
    <div className={'rounded-lg border border-l-4 p-5 ' + kolor.ramka}>
      <p className="font-medium">{tytul}</p>
      <p className="mt-2 flex items-baseline gap-3 tabular-nums">
        <span className={'text-4xl font-semibold ' + kolor.tekst}>
          {liczba(ile)} z {liczba(z)}
        </span>
        <span className={'text-2xl font-semibold ' + kolor.tekst}>{procent(ile / z)}</span>
      </p>
      <p className="mt-1 text-muted-foreground">{dopisek}</p>
    </div>
  )
}

const ZIELONY = { ramka: 'border-l-emerald-600', tekst: 'text-emerald-600' }
const CZERWONY = { ramka: 'border-l-destructive', tekst: 'text-destructive' }
const ZWYKLY = { ramka: '', tekst: '' }

function Progi({ progi, prog, ustawProg, zapisany, zapisz, wiersze }) {
  const wartosci = progi.progi.map((p) => p.prog)
  const krok = Math.round((wartosci[1] - wartosci[0]) * 100) / 100
  const punkty = progi.progi.map((p) => ({
    prog: p.prog,
    lapane: Math.round(p.zlapane),
    falszywe: Math.round(p.falszywe_alarmy),
  }))
  const procenty = punkty.map((p) => ({
    prog: p.prog,
    zlapane: (p.lapane / progi.oszustw) * 100,
    alarmy: (p.falszywe / progi.uczciwych) * 100,
  }))
  // Próg zapisany przez api może wypaść między przetestowanymi punktami.
  const punkt = punkty.find((p) => rowne(p.prog, prog))
  const zapisanyTeraz = rowne(prog, zapisany)

  return (
    <>
      <div className="rounded-lg border">
        <div className="p-6">
          <div className="flex items-start gap-8">
            <div className="flex-1">
              <div className="flex items-baseline gap-3">
                <span className="font-medium">Próg alarmu</span>
                <span className="text-3xl font-semibold tabular-nums">{procent(prog)}</span>
                {!zapisanyTeraz && <span className="text-xs text-muted-foreground">zapisany: {procent(zapisany)}</span>}
              </div>
              <Slider
                className="mt-4"
                aria-label="Próg alarmu"
                min={wartosci[0]}
                max={wartosci.at(-1)}
                step={krok}
                value={[prog]}
                onValueChange={([v]) => ustawProg(Math.round(v * 100) / 100)}
              />
              <div className="mt-2 flex justify-between text-xs text-muted-foreground">
                <span>{procent(wartosci[0])} · łapie więcej oszustw</span>
                <span>{procent(wartosci.at(-1))} · mniej fałszywych alarmów</span>
              </div>
            </div>
            <Button className="mt-1 w-48" variant={zapisanyTeraz ? 'outline' : 'default'} disabled={zapisanyTeraz} onClick={zapisz}>
              {zapisanyTeraz ? 'Zapisany próg: ' + procent(zapisany) : 'Zapisz próg (' + procent(prog) + ')'}
            </Button>
          </div>
          <p className="mt-4">{zdanieKolejki(wiersze, prog, zapisany)}</p>
        </div>
        {punkt && (
          <div className="border-t p-6">
            <h2 className="mb-3 text-muted-foreground">
              Wynik na {liczba(progi.oszustw + progi.uczciwych)} sprawdzonych reklamach ({ileOszustw(progi.oszustw)}, {ileUczciwych(progi.uczciwych)})
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <Kafelek
                tytul="Wyłapane oszustwa"
                ile={punkt.lapane}
                z={progi.oszustw}
                kolor={ZIELONY}
                dopisek={'przeoczone: ' + liczba(progi.oszustw - punkt.lapane)}
              />
              <Kafelek
                tytul="Fałszywe alarmy"
                ile={punkt.falszywe}
                z={progi.uczciwych}
                kolor={punkt.falszywe > 0 ? CZERWONY : ZWYKLY}
                dopisek="uczciwe reklamy oznaczone jako oszustwo"
              />
            </div>
          </div>
        )}
        <div className="border-t p-6">
          <h2 className="mb-2 font-medium">Jak próg zmienia wynik</h2>
          <WykresProgow punkty={procenty} prog={prog} />
        </div>
      </div>
      <p className="mt-3 text-xs text-muted-foreground">
        Twarde reguły, np. strona z listy ostrzeżeń KNF, kierują reklamę do „Do zrobienia” niezależnie od progu.
      </p>
    </>
  )
}

export default function Kalibracja({ prog, ustawProg, wiersze, odswiez }) {
  const [progi, setProgi] = useState(null)
  const [zapisany, setZapisany] = useState(null)
  const [blad, setBlad] = useState(false)

  function wczytaj() {
    setBlad(false)
    Promise.all([pobierzProgi(), pobierzProg()])
      .then(([wyniki, zapis]) => {
        setProgi(wyniki)
        setZapisany(zapis.prog)
        ustawProg(zapis.prog)
      })
      .catch(() => setBlad(true))
  }

  useEffect(wczytaj, [])

  function zapisz() {
    zapiszProg(prog)
      .then(() => {
        setZapisany(prog)
        toast('Próg zapisany')
        odswiez()
      })
      .catch(() => toast.error(BLAD_ZAPISU))
  }

  return (
    <div className="max-w-4xl">
      <h1 className="mb-1 text-2xl font-bold tracking-tight">Kalibracja progu alarmu</h1>
      <p className="mb-5 text-muted-foreground">
        Ustaw, od jakiej oceny modelu KAPSEL reklama trafia do spraw „Do zrobienia”. Niższy próg łapie więcej oszustw, ale daje więcej
        fałszywych alarmów.
      </p>
      {blad && (
        <div className="flex items-center justify-between rounded-lg border p-6">
          <p>Nie udało się wczytać progów. Spróbuj ponownie.</p>
          <Button variant="outline" onClick={wczytaj}>
            Spróbuj ponownie
          </Button>
        </div>
      )}
      {!blad && !progi && <p className="text-muted-foreground">Wczytywanie…</p>}
      {!blad && progi && (
        <>
          <Progi progi={progi} prog={prog} ustawProg={ustawProg} zapisany={zapisany} zapisz={zapisz} wiersze={wiersze} />
          <Uczenie decyzje={wiersze.filter((r) => r.werdykt_analityka).length} odswiez={odswiez} />
        </>
      )}
    </div>
  )
}
