import { CirclePlus, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { dzienCzytelny, liczba, NAZWY_MODULOW, nazwaZrodla } from '../nazwy.js'
import { POZIOMY } from '../ryzyko.js'
import { ustalenia } from '../ustalenia.js'

export const PUSTE_FILTRY = { szukaj: '', od: '', do: '', zrodla: [], statusy: [], ryzyka: [], poziomy: [], moduly: [], tagi: [] }

// Status and the risk range belong to the view, so clearing the filters keeps them.
const POLA = ['szukaj', 'od', 'do', 'zrodla', 'poziomy', 'moduly', 'tagi']

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
      <PopoverContent align="start" className="w-auto max-w-md min-w-48 gap-0 p-1">
        {opcje.map((o) => (
          <Label key={o.wartosc} className="flex cursor-pointer items-center gap-2.5 rounded-md px-2 py-1.5 font-normal hover:bg-muted">
            <Checkbox checked={wybrane.includes(o.wartosc)} onCheckedChange={() => przelacz(o.wartosc)} />
            {o.krotka && <span className="font-medium">{o.krotka}</span>}
            <span className="truncate leading-normal" title={o.etykieta}>
              {o.etykieta}
            </span>
            {o.ile !== undefined && <span className="ml-auto pl-4 tabular-nums text-muted-foreground">{liczba(o.ile)}</span>}
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

export default function Filtry({ filtry, zmien, wiersze, powody }) {
  function ustaw(zmiana) {
    zmien({ ...filtry, ...zmiana })
  }

  const zrodla = [...new Set(wiersze.map((r) => r.zrodlo))].sort()
  const moduly = [...new Set(wiersze.flatMap((r) => ustalenia(r).map((s) => s.modul)))].sort()
  const zmienione = POLA.some((pole) => filtry[pole].length > 0)

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
      <FiltrListy
        nazwa="Ryzyko"
        opcje={Object.entries(POZIOMY).map(([poziom, nazwa]) => ({ wartosc: poziom, etykieta: nazwa }))}
        wybrane={filtry.poziomy}
        zmien={(poziomy) => ustaw({ poziomy })}
      />
      <FiltrListy
        nazwa="Moduł"
        opcje={moduly.map((m) => ({ wartosc: m, krotka: m, etykieta: NAZWY_MODULOW[m] }))}
        wybrane={filtry.moduly}
        zmien={(moduly) => ustaw({ moduly })}
      />
      {powody.length > 0 && (
        <FiltrListy
          nazwa="Powód"
          opcje={powody.map(([tag, ile]) => ({ wartosc: tag, etykieta: tag, ile }))}
          wybrane={filtry.tagi}
          zmien={(tagi) => ustaw({ tagi })}
        />
      )}
      {zmienione && (
        <Button variant="ghost" className="text-xs" onClick={() => zmien({ ...PUSTE_FILTRY, statusy: filtry.statusy, ryzyka: filtry.ryzyka })}>
          Wyczyść filtry
        </Button>
      )}
    </div>
  )
}
