import { ChevronRight } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetDescription, SheetTitle } from '@/components/ui/sheet'
import { zmienStatusy } from '../api.js'
import { BLAD_ZAPISU, data, domena, dzienCzytelny, NAZWY_STATUSOW, nazwaZrodla } from '../nazwy.js'
import { POZIOMY } from '../ryzyko.js'
import { dzienReklamy } from '../sprawy.js'
import { tagi } from '../ustalenia.js'
import ListaUstalen from './ListaUstalen.jsx'
import Podobne from './Podobne.jsx'
import Rejestr from './Rejestr.jsx'
import Sekcja from './Sekcja.jsx'
import Tekst from './Tekst.jsx'

const KOMUNIKATY = {
  nowa: 'Przywrócono do nowych',
  w_toku: 'Wzięto do wyjaśnienia',
  zamknieta: 'Sprawa zamknięta',
}

function Wniosek({ reklama }) {
  const lista = tagi(reklama)
  return (
    <p className="mb-4">
      <span className={'font-semibold' + (reklama.poziom === 'wysokie' ? ' text-destructive' : '')}>
        {POZIOMY[reklama.poziom]} ryzyko
      </span>
      {lista.length > 0 && ': ' + lista.join(' · ')}
    </p>
  )
}

function InneWSprawie({ reklamy, otworz }) {
  if (reklamy.length === 0) return null
  return (
    <Sekcja tytul={'Inne reklamy w tej sprawie (' + reklamy.length + ')'}>
      <ul className="max-h-52 divide-y overflow-auto rounded-lg border">
        {reklamy.map((r) => (
          <li key={r.id}>
            <button className="grid w-full grid-cols-[auto_1fr_auto] gap-4 px-3.5 py-2 text-left hover:bg-muted/50" onClick={() => otworz(r.id)}>
              <span className="font-mono text-xs leading-5 text-muted-foreground">{r.id}</span>
              <span className="truncate">{nazwaZrodla(r.zrodlo)}</span>
              <span className="text-muted-foreground">{dzienCzytelny(dzienReklamy(r))}</span>
            </button>
          </li>
        ))}
      </ul>
    </Sekcja>
  )
}

export default function Szczegoly({ reklama, wiersze, sprawy, otworz, zamknij, podmien, odswiez }) {
  const i = sprawy.findIndex((s) => s.reklamy.some((r) => r.id === reklama.id))
  const nastepna = i === -1 ? null : sprawy[i + 1]
  const ids = i === -1 ? [reklama.id] : sprawy[i].reklamy.map((r) => r.id)
  const wSprawie = wiersze.filter((r) => ids.includes(r.id))

  function ustawStatus(status) {
    const poprzednie = wSprawie.map((r) => [r.id, r.status])
    const id = reklama.id
    zmienStatusy(wSprawie.map((r) => [r.id, status]))
      .then((nowe) => {
        nowe.forEach(podmien)
        toast(KOMUNIKATY[status], { duration: 5000, action: { label: 'Cofnij', onClick: () => cofnij(poprzednie, id) } })
        if (status === 'nowa') return
        if (nastepna) otworz(nastepna.glowna.id)
        else zamknij()
      })
      .catch(() => toast.error(BLAD_ZAPISU))
  }

  function cofnij(poprzednie, id) {
    zmienStatusy(poprzednie)
      .then((nowe) => {
        nowe.forEach(podmien)
        otworz(id)
      })
      .catch(() => toast.error(BLAD_ZAPISU))
  }

  return (
    <Sheet open onOpenChange={zamknij}>
      <SheetContent
        className="gap-0 data-[side=right]:w-[560px] data-[side=right]:sm:max-w-[560px]"
        onInteractOutside={(e) => e.target.closest?.('[data-sonner-toaster]') && e.preventDefault()}
      >
        <div className="min-h-0 flex-1 overflow-auto px-6 pt-6 pb-4">
          <SheetTitle className="pr-8 text-lg font-semibold">{reklama.reklamodawca ?? domena(reklama.url)}</SheetTitle>
          <SheetDescription className="mt-1 mb-3">
            {reklama.id} · {nazwaZrodla(reklama.zrodlo)} · {data(reklama.zebrano)} · {NAZWY_STATUSOW[reklama.status]}
          </SheetDescription>
          <Wniosek reklama={reklama} />
          {reklama.ma_obraz && (
            <img
              src={'/api/reklamy/' + reklama.id + '/obraz'}
              alt="Obraz reklamy"
              className="mb-4 max-h-80 w-full rounded-lg border object-contain"
            />
          )}
          <Rejestr reklama={reklama} />
          <Tekst key={reklama.id} reklama={reklama} />
          <ListaUstalen reklama={reklama} podmien={podmien} />
          <InneWSprawie reklamy={wSprawie.filter((r) => r.id !== reklama.id)} otworz={otworz} />
          <Podobne reklama={reklama} otworz={otworz} odswiez={odswiez} />
        </div>
        <div className="flex shrink-0 items-center gap-2 border-t px-6 py-4">
          {reklama.status === 'nowa' && <Button onClick={() => ustawStatus('w_toku')}>Biorę do wyjaśnienia</Button>}
          {reklama.status !== 'zamknieta' && (
            <Button variant="outline" onClick={() => ustawStatus('zamknieta')}>
              Zamknij sprawę
            </Button>
          )}
          {reklama.status !== 'nowa' && (
            <Button variant="outline" onClick={() => ustawStatus('nowa')}>
              Przywróć do nowych
            </Button>
          )}
          <Button variant="ghost" className="ml-auto" disabled={!nastepna} onClick={() => otworz(nastepna.glowna.id)}>
            Następna
            <ChevronRight />
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  )
}
