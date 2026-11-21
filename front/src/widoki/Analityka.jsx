import { useMemo, useState } from 'react'
import { Button } from '@/components/ui/button'
import Filtry, { PUSTE_FILTRY, START_FILTRY } from '../czesci/Filtry.jsx'
import Srednie from '../czesci/Srednie.jsx'
import TabelaSpraw from '../czesci/TabelaSpraw.jsx'
import Trend from '../czesci/Trend.jsx'
import { dzienCzytelny, ileSpraw, liczba } from '../nazwy.js'
import { dzienReklamy, najmocniejszyTag, odNajgorszych, tytul, wSprawy } from '../sprawy.js'
import { ustalenia } from '../ustalenia.js'

function pasujeSzukane(r, szukane) {
  if (/^\d+$/.test(szukane)) return String(r.id) === szukane
  return [r.reklamodawca, r.url, tytul(r)].some((pole) => pole?.toLowerCase().includes(szukane))
}

function pasujeReklama(r, filtry) {
  const szukane = filtry.szukaj.trim().toLowerCase()
  if (szukane && !pasujeSzukane(r, szukane)) return false
  if (filtry.od && dzienReklamy(r) < filtry.od) return false
  if (filtry.do && dzienReklamy(r) > filtry.do) return false
  if (filtry.zrodla.length && !filtry.zrodla.includes(r.zrodlo)) return false
  if (filtry.statusy.length && !filtry.statusy.includes(r.status)) return false
  if (filtry.moduly.length && !ustalenia(r).some((s) => filtry.moduly.includes(s.modul))) return false
  return true
}

// Risk and reason belong to the whole case, the other filters to its single ads.
function pasujeSprawa(s, filtry) {
  if (!s.reklamy.some((r) => pasujeReklama(r, filtry))) return false
  if (filtry.ryzyka.length && !filtry.ryzyka.includes(s.poziom)) return false
  if (filtry.tagi.length && !filtry.tagi.includes(najmocniejszyTag(s))) return false
  return true
}

function takieSame(a, b) {
  return JSON.stringify(a) === JSON.stringify(b)
}

function Pusto({ poza, wyczysc }) {
  return (
    <>
      <p>Brak spraw w tym widoku</p>
      {poza > 0 && (
        <button className="mt-1 text-[13px] font-medium text-foreground underline-offset-4 hover:underline" onClick={wyczysc}>
          Poza filtrami: {liczba(poza)}
        </button>
      )}
    </>
  )
}

export default function Analityka({ wiersze, otwarteId, otworz }) {
  const [filtry, setFiltry] = useState(START_FILTRY)
  const wszystkie = useMemo(() => wSprawy(wiersze), [wiersze])
  const ile = (zmiana) => wszystkie.filter((s) => pasujeSprawa(s, { ...filtry, ...zmiana })).length

  const sprawy = useMemo(
    () => wszystkie.filter((s) => pasujeSprawa(s, filtry)).sort(odNajgorszych),
    [wszystkie, filtry]
  )
  const srednie = useMemo(
    () => wszystkie.filter((s) => pasujeSprawa(s, { ...filtry, ryzyka: ['srednie'], tagi: [] })),
    [wszystkie, filtry]
  )
  const dlaTrendu = useMemo(
    () => wiersze.filter((r) => pasujeReklama(r, { ...PUSTE_FILTRY, zrodla: filtry.zrodla, moduly: filtry.moduly })),
    [wiersze, filtry.zrodla, filtry.moduly]
  )

  const wToku = ile({ statusy: ['w_toku'], ryzyka: [], tagi: [] })
  const pokazSrednie = takieSame(filtry.ryzyka, ['wysokie']) && filtry.tagi.length === 0 && srednie.length > 0
  const tylkoSzukane = { ...PUSTE_FILTRY, szukaj: filtry.szukaj }

  return (
    <>
      <div className="mb-5 flex items-baseline gap-4">
        <h1 className="text-2xl font-bold tracking-tight">
          {takieSame(filtry, START_FILTRY) ? 'Do przejrzenia: ' + ileSpraw(sprawy.length) : 'Sprawy: ' + liczba(sprawy.length)}
        </h1>
        {wToku > 0 && (
          <Button
            variant="link"
            className="h-auto p-0 text-muted-foreground"
            onClick={() => setFiltry({ ...filtry, statusy: ['w_toku'], ryzyka: [], tagi: [] })}
          >
            W toku ({liczba(wToku)})
          </Button>
        )}
      </div>
      <Filtry filtry={filtry} zmien={setFiltry} wyczysc={() => setFiltry(PUSTE_FILTRY)} wiersze={wiersze} />
      <Trend reklamy={dlaTrendu} />
      <TabelaSpraw
        key={JSON.stringify(filtry)}
        sprawy={sprawy}
        ile={ileSpraw(sprawy.length)}
        kiedy={(s) => dzienCzytelny(s.dzien)}
        otwarteId={otwarteId}
        otworz={(s) => otworz(s.glowna.id, sprawy)}
        pusto={
          <Pusto
            poza={takieSame(filtry, tylkoSzukane) ? 0 : ile(tylkoSzukane)}
            wyczysc={() => setFiltry(tylkoSzukane)}
          />
        }
      />
      {pokazSrednie && (
        <Srednie sprawy={srednie} wybierz={(tag) => setFiltry({ ...filtry, ryzyka: ['srednie'], tagi: [tag] })} />
      )}
    </>
  )
}
