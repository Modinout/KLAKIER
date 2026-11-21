import { useState } from 'react'
import { ArrowDown, ArrowRight, ArrowUp, ChevronLeft, ChevronRight, Circle, CircleCheck, CircleDashed } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { domena, NAZWY_STATUSOW, nazwaZrodla } from '../nazwy.js'
import { POZIOMY } from '../ryzyko.js'
import { tagi } from '../ustalenia.js'

const NA_STRONIE = 12

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

function Naglowek({ children, className = '' }) {
  return (
    <TableHead className={'sticky top-0 z-10 h-[42px] bg-background px-3 text-muted-foreground shadow-[inset_0_-1px_0_var(--color-border)] ' + className}>
      {children}
    </TableHead>
  )
}

export default function TabelaSpraw({ sprawy, ile, kiedy, nowe, otwarteId, otworz }) {
  const [strona, setStrona] = useState(0)
  const stron = Math.max(1, Math.ceil(sprawy.length / NA_STRONIE))
  const biezaca = Math.min(strona, stron - 1)
  const naStronie = sprawy.slice(biezaca * NA_STRONIE, (biezaca + 1) * NA_STRONIE)

  return (
    <>
      <div className="flex min-h-0 flex-col overflow-hidden rounded-lg border *:data-[slot=table-container]:min-h-0 *:data-[slot=table-container]:overflow-auto">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <Naglowek className="w-20">Nr</Naglowek>
              <Naglowek className="w-full">Reklama</Naglowek>
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
                  Brak spraw
                </TableCell>
              </TableRow>
            )}
            {naStronie.map((s) => (
              <TableRow
                key={s.klucz + s.glowna.id}
                className="cursor-pointer"
                data-state={s.reklamy.some((r) => r.id === otwarteId) ? 'selected' : undefined}
                onClick={() => otworz(s)}
              >
                <TableCell className="h-[50px] px-3 font-mono text-xs text-muted-foreground">
                  <div className="flex items-center gap-2">
                    {nowe && <span className={'size-1.5 rounded-full ' + (nowe(s) ? 'bg-foreground' : 'bg-transparent')} />}
                    {s.glowna.id}
                  </div>
                </TableCell>
                <TableCell className="max-w-0 px-3">
                  <div className="flex items-center gap-2">
                    <span className="max-w-[340px] shrink-0 truncate font-medium">
                      {s.glowna.reklamodawca ?? domena(s.glowna.url)}
                    </span>
                    {s.reklamy.length > 1 && (
                      <span className="shrink-0 rounded-sm bg-muted px-1.5 text-xs leading-5 text-muted-foreground">
                        ×{s.reklamy.length}
                      </span>
                    )}
                    <span className="min-w-0 truncate text-muted-foreground">{tagi(s.najgorsza).join(' · ')}</span>
                  </div>
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
