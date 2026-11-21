import { CirclePlus, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { dzienCzytelny, NAZWY_MODULOW, NAZWY_STATUSOW, nazwaZrodla } from '../nazwy.js'
import { POZIOMY } from '../ryzyko.js'
import { ustalenia } from '../ustalenia.js'

export const PUSTE_FILTRY = { szukaj: '', od: '', do: '', zrodla: [], statusy: [], ryzyka: [], moduly: [], tagi: [] }
export const START_FILTRY = { ...PUSTE_FILTRY, statusy: ['nowa'], ryzyka: ['wysokie'] }

function Chip({ etykieta, usun }) {
  return (
    <span className="flex items-center rounded-sm bg-muted pl-1.5 font-normal">
      {etykieta}
      <button type="button" aria-label={'Usuń ' + etykieta} className="px-1 py-0.5 text-muted-foreground hover:text-foreground" onClick={usun}>
        <X className="size-3" />
      </button>
    </span>
  )
}

function PrzyciskFiltra({ nazwa, wybrane, wyczysc }) {
  return (
    <PoleFiltra wybrane={wybrane} wyczysc={wyczysc}>
      <PopoverTrigger asChild>
        <Button variant="ghost" className="h-full text-xs">
          <CirclePlus />
          {nazwa}
        </Button>
      </PopoverTrigger>
    </PoleFiltra>
  )
}

function PoleFiltra({ wybrane, wyczysc, children }) {
  return (
    <div className="flex h-8 items-center gap-1 rounded-lg border border-dashed pr-1 text-xs">
      {children}
      {wybrane.length > 0 && <span className="mr-0.5 h-4 w-px bg-border" />}
      {wybrane.length > 2 ? (
        <Chip etykieta={'Wybrane: ' + wybrane.length} usun={wyczysc} />
      ) : (
        wybrane.map((w) => <Chip key={w.etykieta} etykieta={w.etykieta} usun={w.usun} />)
      )}
    </div>
  )
}

function FiltrListy({ nazwa, opcje, wybrane, zmien }) {
  function przelacz(wartosc) {
    zmien(wybrane.includes(wartosc) ? wybrane.filter((w) => w !== wartosc) : [...wybrane, wartosc])
  }

  const chipy = opcje
    .filter((o) => wybrane.includes(o.wartosc))
    .map((o) => ({ etykieta: o.krotka ?? o.etykieta, usun: () => przelacz(o.wartosc) }))

  return (
    <Popover>
      <PrzyciskFiltra nazwa={nazwa} wybrane={chipy} wyczysc={() => zmien([])} />
      <PopoverContent align="start" className="w-auto min-w-48 gap-0 p-1">
        {opcje.map((o) => (
          <Label key={o.wartosc} className="flex cursor-pointer items-center gap-2.5 rounded-md px-2 py-1.5 font-normal hover:bg-muted">
            <Checkbox checked={wybrane.includes(o.wartosc)} onCheckedChange={() => przelacz(o.wartosc)} />
            {o.krotka && <span className="font-medium">{o.krotka}</span>}
            {o.etykieta}
          </Label>
        ))}
      </PopoverContent>
    </Popover>
  )
}

function FiltrDaty({ od, doDnia, zmien }) {
  const chipy = [
    od && { etykieta: 'od ' + dzienCzytelny(od), usun: () => zmien({ od: '' }) },
    doDnia && { etykieta: 'do ' + dzienCzytelny(doDnia), usun: () => zmien({ do: '' }) },
  ].filter(Boolean)

  return (
    <Popover>
      <PrzyciskFiltra nazwa="Data" wybrane={chipy} />
      <PopoverContent align="start" className="w-auto">
        <div className="flex items-center gap-2">
          <Label className="w-6 font-normal">Od</Label>
          <Input type="date" value={od} onChange={(e) => zmien({ od: e.target.value })} />
        </div>
        <div className="flex items-center gap-2">
          <Label className="w-6 font-normal">Do</Label>
          <Input type="date" value={doDnia} onChange={(e) => zmien({ do: e.target.value })} />
        </div>
      </PopoverContent>
    </Popover>
  )
}

function opcjeZ(nazwy) {
  return Object.entries(nazwy).map(([wartosc, etykieta]) => ({ wartosc, etykieta }))
}

export default function Filtry({ filtry, zmien, wyczysc, wiersze }) {
  function ustaw(zmiana) {
    zmien({ ...filtry, ...zmiana })
  }

  const zrodla = [...new Set(wiersze.map((r) => r.zrodlo))].sort()
  const moduly = [...new Set(wiersze.flatMap((r) => ustalenia(r).map((s) => s.modul)))].sort()
  const cosUstawione = JSON.stringify(filtry) !== JSON.stringify(PUSTE_FILTRY)

  return (
    <div className="mb-3 flex shrink-0 flex-wrap items-center gap-2">
      <Input className="w-[220px]" placeholder="Szukaj" value={filtry.szukaj} onChange={(e) => ustaw({ szukaj: e.target.value })} />
      <FiltrDaty od={filtry.od} doDnia={filtry.do} zmien={ustaw} />
      <FiltrListy
        nazwa="Źródło"
        opcje={zrodla.map((z) => ({ wartosc: z, etykieta: nazwaZrodla(z) }))}
        wybrane={filtry.zrodla}
        zmien={(zrodla) => ustaw({ zrodla })}
      />
      <FiltrListy nazwa="Status" opcje={opcjeZ(NAZWY_STATUSOW)} wybrane={filtry.statusy} zmien={(statusy) => ustaw({ statusy })} />
      <FiltrListy nazwa="Ryzyko" opcje={opcjeZ(POZIOMY)} wybrane={filtry.ryzyka} zmien={(ryzyka) => ustaw({ ryzyka })} />
      <FiltrListy
        nazwa="Moduł"
        opcje={moduly.map((m) => ({ wartosc: m, krotka: m, etykieta: NAZWY_MODULOW[m] }))}
        wybrane={filtry.moduly}
        zmien={(moduly) => ustaw({ moduly })}
      />
      {filtry.tagi.length > 0 && (
        <PoleFiltra wybrane={filtry.tagi.map((t) => ({ etykieta: t, usun: () => ustaw({ tagi: filtry.tagi.filter((x) => x !== t) }) }))}>
          <span className="px-2.5 font-medium">Powód</span>
        </PoleFiltra>
      )}
      {cosUstawione && (
        <Button variant="ghost" className="text-xs" onClick={wyczysc}>
          Wyczyść
          <X />
        </Button>
      )}
    </div>
  )
}
