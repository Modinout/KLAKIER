import { useEffect, useRef, useState } from 'react'
import { ArrowDown, ArrowRight, ArrowUp, ChevronLeft, ChevronRight, Circle, CircleCheck, CircleDashed } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ileReklam, NAZWY_STATUSOW, nazwaZrodla } from '../nazwy.js'
import { POZIOMY } from '../ryzyko.js'
import { najmocniejszyTag } from '../sprawy.js'
import { tagi } from '../ustalenia.js'

const IKONY_RYZYKA = {
  wysokie: <ArrowUp className="size-4 text-destructive" />,
  srednie: <ArrowRight className="size-4 text-muted-foreground" />,
  niskie: <ArrowDown className="size-4 text-muted-foreground" />,
}

const IKONY_STATUSU = {
  nowa: <Circle className="size-4 text-muted-foreground" />,
  w_toku: <CircleDashed className="size-4 text-muted-foreground" />,
  zamknieta: <CircleCheck className="size-4 text-muted-foreground" />,
}

function ZIkona({ ikona, children }) {
  return (
    <div className="flex items-center gap-2">
      {ikona}
      {children}
    </div>
  )
}

function Powod({ sprawa }) {
  const powod = najmocniejszyTag(sprawa)
  if (!powod) return null
  const inne = tagi(sprawa.glowna).slice(1)
  return (
    <div className="flex max-w-[140px] items-center @2xl:max-w-[220px] @4xl:max-w-[300px] @6xl:max-w-[380px]">
      <span className="truncate" title={powod}>{powod}</span>
      {inne.length > 0 && (
        <span className="ml-1.5 shrink-0 text-muted-foreground" title={inne.join(' · ')}>
          +{inne.length}
        </span>
      )}
    </div>
  )
}

function Naglowek({ children, className = '' }) {
  return (
    <TableHead className={'sticky top-0 z-10 h-[42px] bg-background px-3 text-muted-foreground shadow-[inset_0_-1px_0_var(--color-border)] ' + className}>
      {children}
    </TableHead>
  )
}

// Bez `wierszy` tabela pokazuje wszystkie sprawy i przewija się sama w sobie, a liczbę spraw podaje już zakładka widoku.
// Z `zaznaczone` ma kolumnę pól wyboru, a spacja zaznacza wiersz zamiast go otwierać.
// Z `obok` strzałki od razu otwierają sąsiednią sprawę, bo szczegóły stoją obok listy.
export default function TabelaSpraw({ sprawy, ile, kiedy, nowe, otwarteId, otworz, obok, wierszy, zaznaczone, zaznacz, pusto = 'Brak spraw w tym widoku' }) {
  const cialo = useRef(null)
  const [strona, setStrona] = useState(0)
  const stron = wierszy ? Math.max(1, Math.ceil(sprawy.length / wierszy)) : 1
  const biezaca = Math.min(strona, stron - 1)
  const naStronie = wierszy ? sprawy.slice(biezaca * wierszy, (biezaca + 1) * wierszy) : sprawy
  const wszystkieZaznaczone = sprawy.length > 0 && sprawy.every((s) => zaznaczone?.has(s.klucz))
  const czescZaznaczona = sprawy.some((s) => zaznaczone?.has(s.klucz))

  // Wybrana sprawa ma być widoczna; gdy już ją widać, lista stoi w miejscu.
  useEffect(() => {
    cialo.current?.querySelector('[data-state=selected]')?.scrollIntoView({ block: 'nearest' })
  }, [otwarteId])

  function przelacz(s) {
    const zbior = new Set(zaznaczone)
    if (zbior.has(s.klucz)) zbior.delete(s.klucz)
    else zbior.add(s.klucz)
    zaznacz(zbior)
  }

  function klawisz(e, i) {
    const wiersz = e.currentTarget
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      const krok = e.key === 'ArrowDown' ? 1 : -1
      const sasiad = krok === 1 ? wiersz.nextElementSibling : wiersz.previousElementSibling
      if (!sasiad) return
      e.preventDefault()
      sasiad.focus()
      if (obok) otworz(naStronie[i + krok])
      return
    }
    if (e.target !== wiersz || (e.key !== 'Enter' && e.key !== ' ')) return
    e.preventDefault()
    if (e.key === ' ' && zaznaczone) przelacz(naStronie[i])
    else otworz(naStronie[i])
  }

  return (
    <>
      <div
        className={'@container rounded-lg border ' + (wierszy ? 'overflow-hidden' : 'min-h-0 flex-1 overflow-auto *:overflow-visible')}
        onKeyDown={(e) => e.key === 'Escape' && zaznaczone?.size > 0 && zaznacz(new Set())}
      >
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              {zaznaczone && (
                <Naglowek className="w-px">
                  <Checkbox
                    aria-label="Zaznacz wszystkie w widoku"
                    title="Zaznacz wszystkie w widoku"
                    disabled={sprawy.length === 0}
                    checked={wszystkieZaznaczone || (czescZaznaczona && 'indeterminate')}
                    onCheckedChange={() => zaznacz(new Set(wszystkieZaznaczone ? [] : sprawy.map((s) => s.klucz)))}
                  />
                </Naglowek>
              )}
              <Naglowek className="w-full">Sprawa</Naglowek>
              <Naglowek>Powód</Naglowek>
              <Naglowek className="hidden @5xl:table-cell">Źródło</Naglowek>
              <Naglowek>Ryzyko</Naglowek>
              <Naglowek>Status</Naglowek>
              <Naglowek className="hidden @4xl:table-cell">Data</Naglowek>
            </TableRow>
          </TableHeader>
          <TableBody ref={cialo}>
            {naStronie.length === 0 && (
              <TableRow className="hover:bg-transparent">
                <TableCell colSpan={7} className="h-24 text-center text-muted-foreground">
                  {pusto}
                </TableCell>
              </TableRow>
            )}
            {naStronie.map((s, i) => (
              <TableRow
                key={s.klucz}
                className="scroll-mt-[42px] cursor-pointer focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-ring"
                data-state={s.reklamy.some((r) => r.id === otwarteId) ? 'selected' : undefined}
                tabIndex={0}
                onClick={() => otworz(s)}
                onKeyDown={(e) => klawisz(e, i)}
              >
                {zaznaczone && (
                  // Kliknięcie pola tylko zaznacza; fokus wraca na wiersz, żeby strzałki dalej działały.
                  <TableCell
                    className="px-3"
                    onClick={(e) => {
                      e.stopPropagation()
                      przelacz(s)
                      e.currentTarget.parentElement.focus()
                    }}
                  >
                    <Checkbox tabIndex={-1} aria-label={'Zaznacz ' + s.tytul} checked={zaznaczone.has(s.klucz)} />
                  </TableCell>
                )}
                <TableCell className="h-[44px] max-w-0 px-3">
                  <div className="flex items-center gap-2">
                    {nowe && <span className={'size-1.5 shrink-0 rounded-full ' + (nowe(s) ? 'bg-foreground' : 'bg-transparent')} />}
                    <span className="max-w-[440px] truncate font-medium">{s.tytul}</span>
                    {s.reklamy.length > 1 && (
                      <span className="shrink-0 text-xs text-muted-foreground">{ileReklam(s.reklamy.length)}</span>
                    )}
                  </div>
                </TableCell>
                <TableCell className="px-3">
                  <Powod sprawa={s} />
                </TableCell>
                <TableCell className="hidden px-3 @5xl:table-cell">{nazwaZrodla(s.glowna.zrodlo)}</TableCell>
                <TableCell className="px-3">
                  <ZIkona ikona={IKONY_RYZYKA[s.poziom]}>{POZIOMY[s.poziom]}</ZIkona>
                </TableCell>
                <TableCell className="px-3">
                  <ZIkona ikona={IKONY_STATUSU[s.glowna.status]}>{NAZWY_STATUSOW[s.glowna.status]}</ZIkona>
                </TableCell>
                <TableCell className="hidden px-3 text-muted-foreground @4xl:table-cell">{kiedy(s)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      {wierszy && (
        <div className="mt-3 flex shrink-0 items-center gap-6">
          <span className="mr-auto text-muted-foreground">{ile}</span>
          <span className="font-medium">
            Strona {biezaca + 1} z {stron}
          </span>
          <div className="flex gap-2">
            <Button variant="outline" size="icon" aria-label="Poprzednia strona" disabled={biezaca === 0} onClick={() => setStrona(biezaca - 1)}>
              <ChevronLeft />
            </Button>
            <Button variant="outline" size="icon" aria-label="Następna strona" disabled={biezaca >= stron - 1} onClick={() => setStrona(biezaca + 1)}>
              <ChevronRight />
            </Button>
          </div>
        </div>
      )}
    </>
  )
}
