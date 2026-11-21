import { useEffect, useRef, useState } from 'react'
import { ChevronRight } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetDescription, SheetTitle } from '@/components/ui/sheet'
import { zmienStatusy } from '../api.js'
import { bezTekstu, BLAD_ZAPISU, data, dzienCzytelny, liniaOszustwa, NAZWY_STATUSOW, nazwaZrodla, zBiblioteki } from '../nazwy.js'
import { POZIOMY } from '../ryzyko.js'
import { dzienReklamy, odNajgorszej, tytul } from '../sprawy.js'
import ListaUstalen from './ListaUstalen.jsx'
import Obraz from './Obraz.jsx'
import Ocena from './Ocena.jsx'
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
  return (
    <p className="mb-4">
      <span className={'font-semibold' + (reklama.poziom === 'wysokie' ? ' text-destructive' : '')}>
        {POZIOMY[reklama.poziom]} ryzyko
      </span>
      {reklama.powod && ': ' + reklama.powod.replace(/^Tekst reklamy wygląda na oszustwo/, liniaOszustwa(reklama))}
    </p>
  )
}

function InneWSprawie({ reklama, reklamy, otworz }) {
  if (reklamy.length === 0) return null
  const kilkuPlatnikow = new Set([reklama, ...reklamy].map((r) => r.reklamodawca)).size > 1
  return (
    <Sekcja tytul={'Inne reklamy w tej sprawie (' + reklamy.length + ')'}>
      <ul className="max-h-52 divide-y overflow-auto rounded-lg border">
        {reklamy.map((r) => (
          <li key={r.id}>
            <button className="grid w-full grid-cols-[auto_1fr_auto] gap-4 px-3.5 py-2 text-left hover:bg-muted/50" onClick={() => otworz(r.id)}>
              <span className="font-mono text-xs leading-5 text-muted-foreground">{r.id}</span>
              <span className="truncate">
                {kilkuPlatnikow && r.reklamodawca && <span className="font-medium">{r.reklamodawca} · </span>}
                {bezTekstu(r) ? <span className="text-muted-foreground">Reklama graficzna</span> : r.tekst}
              </span>
              <span className="text-muted-foreground">{dzienCzytelny(dzienReklamy(r))}</span>
            </button>
          </li>
        ))}
      </ul>
    </Sekcja>
  )
}

export default function Szczegoly({ reklama, wiersze, sprawy, otworz, zamknij, podmien, odswiez }) {
  const tresc = useRef(null)
  const [bezObrazu, setBezObrazu] = useState(null)
  const i = sprawy.findIndex((s) => s.reklamy.some((r) => r.id === reklama.id))
  const nastepna = i === -1 ? null : sprawy[i + 1]
  const ids = i === -1 ? [reklama.id] : sprawy[i].reklamy.map((r) => r.id)
  const wSprawie = wiersze.filter((r) => ids.includes(r.id)).sort(odNajgorszej)
  const obraz = reklama.ma_obraz && bezObrazu !== reklama.id

  // The sheet body mounts after the first render, and starts at the top anyway.
  useEffect(() => {
    if (tresc.current) tresc.current.scrollTop = 0
  }, [reklama.id])

  function ustawStatus(status) {
    const poprzednie = wSprawie.map((r) => [r.id, r.status])
    const id = reklama.id
    zmienStatusy(wSprawie.map((r) => [r.id, status]))
      .then((nowe) => {
        nowe.forEach(podmien)
        toast(KOMUNIKATY[status], { duration: 5000, action: { label: 'Cofnij', onClick: () => cofnij(poprzednie, id) } })
        if (status !== 'zamknieta') return
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
        <div ref={tresc} className="min-h-0 flex-1 overflow-auto px-6 pt-6 pb-4">
          <SheetTitle className="pr-8 text-lg font-semibold">{tytul(reklama)}</SheetTitle>
          <SheetDescription className="mt-1 mb-3">
            {reklama.id} · {nazwaZrodla(reklama.zrodlo)} · {data(reklama.zebrano)} · {NAZWY_STATUSOW[reklama.status]}
            {reklama.url && zBiblioteki(reklama.url) && (
              <>
                {' · '}
                <a href={reklama.url} target="_blank" rel="noreferrer" className="underline underline-offset-4">
                  Źródło w bibliotece reklam
                </a>
              </>
            )}
          </SheetDescription>
          <Wniosek reklama={reklama} />
          {obraz && <Obraz reklama={reklama} ukryj={() => setBezObrazu(reklama.id)} />}
          <Rejestr reklama={reklama} />
          <Tekst key={'tekst' + reklama.id} reklama={reklama} obraz={obraz} />
          <ListaUstalen reklama={reklama} />
          <InneWSprawie reklama={reklama} reklamy={wSprawie.filter((r) => r.id !== reklama.id)} otworz={otworz} />
          <Podobne reklama={reklama} wSprawie={ids} otworz={otworz} odswiez={odswiez} />
          {!bezTekstu(reklama) && <Ocena key={'ocena' + reklama.id} reklama={reklama} podmien={podmien} />}
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
