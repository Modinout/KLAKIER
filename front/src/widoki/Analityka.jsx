import { useMemo, useState } from 'react'
import Filtry, { PUSTE_FILTRY } from '../czesci/Filtry.jsx'
import TabelaSpraw from '../czesci/TabelaSpraw.jsx'
import Trend from '../czesci/Trend.jsx'
import Widoki, { WIDOKI } from '../czesci/Widoki.jsx'
import { dzienCzytelny, ileReklam, ileSpraw, liczba } from '../nazwy.js'
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
  if (filtry.poziomy.length && !filtry.poziomy.includes(s.poziom)) return false
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
  const [filtry, setFiltry] = useState({ ...PUSTE_FILTRY, ...WIDOKI[0].zakres })
  const wszystkie = useMemo(() => wSprawy(wiersze), [wiersze])
  const ile = (zmiana) => wszystkie.filter((s) => pasujeSprawa(s, { ...filtry, ...zmiana })).length

  const sprawy = useMemo(
    () => wszystkie.filter((s) => pasujeSprawa(s, filtry)).sort(odNajgorszych),
    [wszystkie, filtry]
  )
  const powody = useMemo(() => {
    const bezPowodu = wszystkie.filter((s) => pasujeSprawa(s, { ...filtry, tagi: [] })).sort(odNajgorszych)
    return [...Map.groupBy(bezPowodu, najmocniejszyTag)].filter(([tag]) => tag).map(([tag, lista]) => [tag, lista.length])
  }, [wszystkie, filtry])
  const dlaTrendu = useMemo(
    () => wiersze.filter((r) => pasujeReklama(r, { ...PUSTE_FILTRY, zrodla: filtry.zrodla, moduly: filtry.moduly })),
    [wiersze, filtry.zrodla, filtry.moduly]
  )

  const tylkoSzukane = { ...PUSTE_FILTRY, szukaj: filtry.szukaj }

  return (
    <>
      <div className="mb-5 flex shrink-0 items-end justify-between gap-8">
        <h1 className="text-2xl font-bold tracking-tight">Sprawdzone automatycznie: {ileReklam(wiersze.length)} w {liczba(wszystkie.length)} sprawach</h1>
        <Trend reklamy={dlaTrendu} />
      </div>
      <Widoki filtry={filtry} zmien={setFiltry} ile={ile} />
      <Filtry filtry={filtry} zmien={setFiltry} wiersze={wiersze} powody={powody} />
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
    </>
  )
}
