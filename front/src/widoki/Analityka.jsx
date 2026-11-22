import { Download } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { Button } from '@/components/ui/button'
import Filtry, { PUSTE_FILTRY } from '../czesci/Filtry.jsx'
import TabelaSpraw from '../czesci/TabelaSpraw.jsx'
import Trend from '../czesci/Trend.jsx'
import Widoki, { WIDOKI } from '../czesci/Widoki.jsx'
import Zaznaczone from '../czesci/Zaznaczone.jsx'
import useSzeroki from '../useSzeroki.js'
import { dzienCzytelny, ileReklam, liczba } from '../nazwy.js'
import { pobierzPlik } from '../pobierz.js'
import { nazwaRaportu, raport } from '../raport.js'
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

// Ryzyko i powód należą do całej sprawy, pozostałe filtry do jej pojedynczych reklam.
function pasujeSprawa(s, filtry) {
  if (!s.reklamy.some((r) => pasujeReklama(r, filtry))) return false
  if (filtry.ryzyka.length && !filtry.ryzyka.includes(s.poziom)) return false
  if (filtry.poziomy.length && !filtry.poziomy.includes(s.poziom)) return false
  if (filtry.tagi.length && !filtry.tagi.includes(najmocniejszyTag(s))) return false
  return true
}

// Szukany numer reklamy otwiera tę reklamę, a nie główną reklamę jej sprawy.
function doOtwarcia(s, szukaj) {
  const szukane = szukaj.trim()
  const znaleziona = /^\d+$/.test(szukane) && s.reklamy.find((r) => String(r.id) === szukane)
  return znaleziona ? znaleziona.id : s.glowna.id
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

export default function Analityka({ wiersze, otwarteId, otworz, podmien, szczegoly }) {
  const szeroki = useSzeroki()
  const [filtry, setFiltryBezZaznaczenia] = useState({ ...PUSTE_FILTRY, ...WIDOKI[0].zakres })
  const [zaznaczone, setZaznaczone] = useState(new Set())
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
  const zaznaczoneSprawy = sprawy.filter((s) => zaznaczone.has(s.klucz))

  // Zaznaczenie dotyczy spraw widocznych w danym widoku, więc zmiana widoku albo filtrów je czyści.
  function setFiltry(nowe) {
    setFiltryBezZaznaczenia(nowe)
    setZaznaczone(new Set())
  }

  function wybierz(s) {
    otworz(doOtwarcia(s, filtry.szukaj), sprawy)
  }

  // Szczegóły obok listy nie stoją puste: przy starcie i po zmianie widoku albo filtrów pokazują pierwszą sprawę.
  useEffect(() => {
    if (szeroki && sprawy.length > 0) wybierz(sprawy[0])
  }, [szeroki, filtry])

  // Zamknięte sprawy wypadają z widoku, więc szczegóły przechodzą do pierwszej niezaznaczonej sprawy za wybraną.
  function poZamknieciu() {
    const i = sprawy.findIndex((s) => s.reklamy.some((r) => r.id === otwarteId))
    const dalej = [...sprawy.slice(i), ...sprawy.slice(0, i)].find((s) => !zaznaczone.has(s.klucz))
    if (szeroki && i !== -1 && zaznaczone.has(sprawy[i].klucz) && dalej) wybierz(dalej)
    setZaznaczone(new Set())
  }

  return (
    <>
      <div className="mb-5 flex shrink-0 items-end justify-between gap-8">
        <h1 className="text-2xl font-bold tracking-tight">Sprawdzone automatycznie: {ileReklam(wiersze.length)} w {liczba(wszystkie.length)} sprawach</h1>
        <Trend reklamy={dlaTrendu} />
      </div>
      <Widoki filtry={filtry} zmien={setFiltry} ile={ile} />
      <Filtry filtry={filtry} zmien={setFiltry} wiersze={wiersze} powody={powody}>
        <Button variant="outline" className="ml-auto" onClick={() => pobierzPlik(raport(sprawy), 'text/csv;charset=utf-8', nazwaRaportu())}>
          <Download />
          Pobierz raport
        </Button>
      </Filtry>
      <div className="flex min-h-0 flex-1 gap-4">
        <div className="flex min-w-0 flex-1 flex-col">
          {zaznaczoneSprawy.length > 0 && <Zaznaczone sprawy={zaznaczoneSprawy} podmien={podmien} poZamknieciu={poZamknieciu} />}
          <TabelaSpraw
            key={JSON.stringify(filtry)}
            sprawy={sprawy}
            kiedy={(s) => dzienCzytelny(s.dzien)}
            otwarteId={otwarteId}
            otworz={wybierz}
            obok={szeroki}
            zaznaczone={zaznaczone}
            zaznacz={setZaznaczone}
            pusto={
              <Pusto
                poza={takieSame(filtry, tylkoSzukane) ? 0 : ile(tylkoSzukane)}
                wyczysc={() => setFiltry(tylkoSzukane)}
              />
            }
          />
        </div>
        {szeroki &&
          (szczegoly ?? (
            <aside className="flex w-[520px] shrink-0 items-center justify-center rounded-lg border text-muted-foreground">
              Wybierz sprawę z listy
            </aside>
          ))}
      </div>
    </>
  )
}
