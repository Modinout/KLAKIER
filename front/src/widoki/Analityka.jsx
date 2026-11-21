import { useMemo, useState } from 'react'
import Filtry, { PUSTE_FILTRY, START_FILTRY } from '../czesci/Filtry.jsx'
import TabelaSpraw from '../czesci/TabelaSpraw.jsx'
import Trend from '../czesci/Trend.jsx'
import { dzienCzytelny, ileSpraw } from '../nazwy.js'
import { dzienReklamy, odNajgorszych, wSprawy } from '../sprawy.js'
import { ustalenia } from '../ustalenia.js'

function pasujeSzukane(r, szukane) {
  if (/^\d+$/.test(szukane)) return String(r.id) === szukane
  return [r.reklamodawca, r.url].some((pole) => pole?.toLowerCase().includes(szukane))
}

function pasuje(r, filtry) {
  const szukane = filtry.szukaj.trim().toLowerCase()
  if (szukane && !pasujeSzukane(r, szukane)) return false
  if (filtry.od && dzienReklamy(r) < filtry.od) return false
  if (filtry.do && dzienReklamy(r) > filtry.do) return false
  if (filtry.zrodla.length && !filtry.zrodla.includes(r.zrodlo)) return false
  if (filtry.statusy.length && !filtry.statusy.includes(r.status)) return false
  if (filtry.ryzyka.length && !filtry.ryzyka.includes(r.poziom)) return false
  if (filtry.moduly.length && !ustalenia(r).some((s) => filtry.moduly.includes(s.modul))) return false
  return true
}

export default function Analityka({ wiersze, otwarteId, otworz }) {
  const [filtry, setFiltry] = useState(START_FILTRY)

  const sprawy = useMemo(
    () => wSprawy(wiersze.filter((r) => pasuje(r, filtry))).sort(odNajgorszych),
    [wiersze, filtry]
  )
  const dlaTrendu = useMemo(
    () => wiersze.filter((r) => pasuje(r, { ...PUSTE_FILTRY, zrodla: filtry.zrodla, moduly: filtry.moduly })),
    [wiersze, filtry.zrodla, filtry.moduly]
  )

  return (
    <>
      <h1 className="mb-5 text-2xl font-bold tracking-tight">Do przejrzenia: {ileSpraw(sprawy.length)}</h1>
      <Filtry filtry={filtry} zmien={setFiltry} wyczysc={() => setFiltry(PUSTE_FILTRY)} wiersze={wiersze} />
      <Trend reklamy={dlaTrendu} />
      <TabelaSpraw
        key={JSON.stringify(filtry)}
        sprawy={sprawy}
        ile={ileSpraw(sprawy.length)}
        kiedy={(s) => dzienCzytelny(s.dzien)}
        otwarteId={otwarteId}
        otworz={(s) => otworz(s.glowna.id, sprawy)}
      />
    </>
  )
}
