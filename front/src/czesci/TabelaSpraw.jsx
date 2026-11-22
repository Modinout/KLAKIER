import { useLayoutEffect, useRef, useState } from 'react'
import { ArrowDown, ArrowRight, ArrowUp, ChevronLeft, ChevronRight, Circle, CircleCheck, CircleDashed } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ileReklam, NAZWY_STATUSOW, nazwaZrodla } from '../nazwy.js'
import { POZIOMY } from '../ryzyko.js'
import { najmocniejszyTag } from '../sprawy.js'
import { tagi } from '../ustalenia.js'

const NAGLOWEK = 44
const WIERSZ = 44
const NAJWIECEJ = 12

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
    <div className="flex max-w-[320px] items-center">
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
    <TableHead className={'h-[42px] bg-background px-3 text-muted-foreground shadow-[inset_0_-1px_0_var(--color-border)] ' + className}>
      {children}
    </TableHead>
  )
}

// As many rows as fit, so the table never scrolls inside itself.
function useWierszeWOknie() {
  const pole = useRef(null)
  const [ile, setIle] = useState(1)
  useLayoutEffect(() => {
    const obserwator = new ResizeObserver(([wpis]) =>
      setIle(Math.min(NAJWIECEJ, Math.max(1, Math.floor((wpis.contentRect.height - NAGLOWEK) / WIERSZ))))
    )
    obserwator.observe(pole.current)
    return () => obserwator.disconnect()
  }, [])
  return [pole, ile]
}

export default function TabelaSpraw({ sprawy, ile, kiedy, nowe, otwarteId, otworz, wierszy, pusto = 'Brak spraw w tym widoku' }) {
  const [pole, wOknie] = useWierszeWOknie()
  const naStrone = wierszy ?? wOknie
  const [strona, setStrona] = useState(0)
  const stron = Math.max(1, Math.ceil(sprawy.length / naStrone))
  const biezaca = Math.min(strona, stron - 1)
  const naStronie = sprawy.slice(biezaca * naStrone, (biezaca + 1) * naStrone)

  return (
    <>
      <div ref={pole} className={wierszy ? '' : 'min-h-0 flex-1 overflow-hidden'}>
        <div className="overflow-hidden rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <Naglowek className="w-full">Sprawa</Naglowek>
                <Naglowek>Powód</Naglowek>
                <Naglowek>Źródło</Naglowek>
                <Naglowek>Ryzyko</Naglowek>
                <Naglowek>Status</Naglowek>
                <Naglowek>Data</Naglowek>
              </TableRow>
            </TableHeader>
            <TableBody>
              {naStronie.length === 0 && (
                <TableRow className="hover:bg-transparent">
                  <TableCell colSpan={6} className="h-24 text-center text-muted-foreground">
                    {pusto}
                  </TableCell>
                </TableRow>
              )}
              {naStronie.map((s) => (
                <TableRow
                  key={s.klucz}
                  className="cursor-pointer"
                  data-state={s.reklamy.some((r) => r.id === otwarteId) ? 'selected' : undefined}
                  onClick={() => otworz(s)}
                >
                  <TableCell className="h-[44px] max-w-0 px-3">
                    <div className="flex items-center gap-2">
                      {nowe && <span className={'size-1.5 shrink-0 rounded-full ' + (nowe(s) ? 'bg-foreground' : 'bg-transparent')} />}
                      <span className="max-w-[340px] shrink-0 truncate font-medium">{s.tytul}</span>
                      {s.reklamy.length > 1 && (
                        <span className="shrink-0 text-xs text-muted-foreground">{ileReklam(s.reklamy.length)}</span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell className="px-3">
                    <Powod sprawa={s} />
                  </TableCell>
                  <TableCell className="px-3">{nazwaZrodla(s.glowna.zrodlo)}</TableCell>
                  <TableCell className="px-3">
                    <ZIkona ikona={IKONY_RYZYKA[s.poziom]}>{POZIOMY[s.poziom]}</ZIkona>
                  </TableCell>
                  <TableCell className="px-3">
                    <ZIkona ikona={IKONY_STATUSU[s.glowna.status]}>{NAZWY_STATUSOW[s.glowna.status]}</ZIkona>
                  </TableCell>
                  <TableCell className="px-3 text-muted-foreground">{kiedy(s)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>
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
    </>
  )
}
