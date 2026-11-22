import { useEffect, useRef, useState } from 'react'
import { ChevronRight, Download, Undo2 } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetDescription, SheetTitle } from '@/components/ui/sheet'
import { zmienStatusy } from '../api.js'
import { bezTekstu, BLAD_ZAPISU, data, dzienCzytelny, ileReklam, NAZWY_STATUSOW, nazwaZrodla, zBiblioteki } from '../nazwy.js'
import { pobierzPlik } from '../pobierz.js'
import { POZIOMY } from '../ryzyko.js'
import { dzienReklamy, odNajgorszej, tytul } from '../sprawy.js'
import { czystaSprawa, modelZalecaSprawdzenie, tagi, ustalenia, zdecydowalModel, zdaniePowodu } from '../ustalenia.js'
import { nazwaPliku, zgloszenie } from '../zgloszenie.js'
import Dowody from './Dowody.jsx'
import Historia from './Historia.jsx'
import ListaUstalen from './ListaUstalen.jsx'
import Notatka from './Notatka.jsx'
import Obraz from './Obraz.jsx'
import Ocena from './Ocena.jsx'
import Podobne from './Podobne.jsx'
import Powiazane from './Powiazane.jsx'
import Rejestr from './Rejestr.jsx'
import Sekcja from './Sekcja.jsx'
import Tekst from './Tekst.jsx'

const KOMUNIKATY = {
  nowa: 'Przywrócono do nowych',
  w_toku: 'Wzięto do wyjaśnienia',
  zamknieta: 'Sprawa zamknięta',
}

function dopisek(reklama) {
  if (czystaSprawa(reklama)) return ': nie znaleziono naruszeń.'
  if (reklama.poziom === 'niskie' && ustalenia(reklama).length === 0 && modelZalecaSprawdzenie(reklama)) {
    return ': brak twardych ustaleń, ale model KAPSEL zaleca sprawdzenie tekstu.'
  }
  return reklama.powod && ': ' + zdaniePowodu(reklama)
}

// Skróty takie jak „CFD” zostają wielkimi literami.
function malaLitera(tekst) {
  return /^\p{Lu}\p{Lu}/u.test(tekst) ? tekst : tekst.charAt(0).toLocaleLowerCase('pl') + tekst.slice(1)
}

function Wniosek({ reklama }) {
  const [pierwszy] = tagi(reklama)
  const samPoziom = reklama.poziom !== 'niskie' && Boolean(pierwszy)
  return (
    <>
      <p>
        <span className={'font-semibold' + (reklama.poziom === 'wysokie' ? ' text-destructive' : '')}>
          {POZIOMY[reklama.poziom]} ryzyko
        </span>
        {!samPoziom && dopisek(reklama)}
      </p>
      {samPoziom && !zdecydowalModel(reklama) && (
        <p className="mt-1 text-[13px] text-muted-foreground">Zdecydowała reguła: {malaLitera(pierwszy)}</p>
      )}
    </>
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
  // Arkusz otwiera się ze stanu, bez wyzwalacza Radix, więc po zamknięciu fokus wraca tu ręcznie.
  const otwierajacy = useRef(document.activeElement)
  const [bezObrazu, setBezObrazu] = useState(null)
  const i = sprawy.findIndex((s) => s.reklamy.some((r) => r.id === reklama.id))
  const nastepna = i === -1 ? null : sprawy[i + 1]
  const ids = i === -1 ? [reklama.id] : sprawy[i].reklamy.map((r) => r.id)
  const wSprawie = wiersze.filter((r) => ids.includes(r.id)).sort(odNajgorszej)
  const obraz = reklama.ma_obraz && bezObrazu !== reklama.id

  // Treść szczegółów montuje się po pierwszym renderze i tak zaczyna od góry.
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

  // Otwarta reklama idzie w raporcie jako pierwsza.
  const doZgloszenia = [reklama, ...wSprawie.filter((r) => r.id !== reklama.id)]

  function kopiujZgloszenie() {
    navigator.clipboard
      .writeText(zgloszenie(doZgloszenia))
      .then(() => toast('Skopiowano zgłoszenie'))
      .catch(() => toast.error('Nie udało się skopiować'))
  }

  function pobierzZgloszenie() {
    pobierzPlik(zgloszenie(doZgloszenia), 'text/plain;charset=utf-8', nazwaPliku(doZgloszenia))
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
        className="gap-0 data-[side=right]:w-full data-[side=right]:sm:w-[560px] data-[side=right]:sm:max-w-[560px]"
        onInteractOutside={(e) => e.target.closest?.('[data-sonner-toaster]') && e.preventDefault()}
        onCloseAutoFocus={(e) => {
          e.preventDefault()
          otwierajacy.current?.focus()
        }}
      >
        <div ref={tresc} className="min-h-0 flex-1 overflow-auto px-6 pb-4">
          <div className="sticky top-0 -mx-6 bg-popover px-6 pt-6 pb-1">
            <SheetTitle className="pr-8 text-lg font-semibold">
              {tytul(reklama)}
              {wSprawie.length > 1 && <span className="font-normal text-muted-foreground"> · {ileReklam(wSprawie.length)}</span>}
            </SheetTitle>
          </div>
          <SheetDescription className="mb-3">
            Reklama nr {reklama.id} · {nazwaZrodla(reklama.zrodlo)} · {data(reklama.zebrano)} · {NAZWY_STATUSOW[reklama.status]}
            {reklama.url && zBiblioteki(reklama.url) && (
              <>
                {' · '}
                <a href={reklama.url} target="_blank" rel="noreferrer" className="underline underline-offset-4">
                  Źródło w bibliotece reklam
                </a>
              </>
            )}
          </SheetDescription>
          <div className="mb-4">
            <Wniosek reklama={reklama} />
            <Ocena key={'ocena' + reklama.id} reklama={reklama} podmien={podmien} />
          </div>
          <Rejestr reklama={reklama} />
          <ListaUstalen reklama={reklama} />
          <Notatka key={'notatka' + reklama.id} reklama={reklama} podmien={podmien} />
          {(obraz || !bezTekstu(reklama)) && (
            <Sekcja tytul="Reklama">
              {obraz && <Obraz reklama={reklama} ukryj={() => setBezObrazu(reklama.id)} />}
              <Tekst key={'tekst' + reklama.id} reklama={reklama} obraz={obraz} />
            </Sekcja>
          )}
          <InneWSprawie reklama={reklama} reklamy={wSprawie.filter((r) => r.id !== reklama.id)} otworz={otworz} />
          <Powiazane key={'powiazane' + reklama.id} reklama={reklama} wSprawie={ids} otworz={otworz} />
          <Podobne key={'podobne' + reklama.id} reklama={reklama} wSprawie={ids} otworz={otworz} odswiez={odswiez} />
          <Dowody reklama={reklama} />
          <Historia key={'historia' + reklama.id} reklama={reklama} />
        </div>
        <div className="flex shrink-0 items-center gap-2 border-t px-6 py-4">
          {reklama.status === 'nowa' && <Button onClick={() => ustawStatus('w_toku')}>Biorę do wyjaśnienia</Button>}
          {reklama.status === 'w_toku' && (
            <div className="flex">
              <Button className="rounded-r-none" onClick={kopiujZgloszenie}>
                Kopiuj zgłoszenie
              </Button>
              <Button
                size="icon"
                className="rounded-l-none border-l-primary-foreground/25"
                aria-label="Pobierz zgłoszenie"
                title="Pobierz zgłoszenie"
                onClick={pobierzZgloszenie}
              >
                <Download />
              </Button>
            </div>
          )}
          {reklama.status !== 'zamknieta' && (
            <Button variant="outline" onClick={() => ustawStatus('zamknieta')}>
              Zamknij sprawę
            </Button>
          )}
          {reklama.status === 'w_toku' && (
            <Button variant="ghost" size="icon" aria-label="Przywróć do nowych" title="Przywróć do nowych" onClick={() => ustawStatus('nowa')}>
              <Undo2 />
            </Button>
          )}
          {reklama.status === 'zamknieta' && (
            <Button variant="outline" onClick={() => ustawStatus('nowa')}>
              Przywróć do nowych
            </Button>
          )}
          <Button variant="ghost" className="ml-auto" disabled={!nastepna} onClick={() => otworz(nastepna.glowna.id)}>
            Następna sprawa
            <ChevronRight />
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  )
}
