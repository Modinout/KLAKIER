import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { zmienWerdyktAnalityka } from '../api.js'
import { BLAD_ZAPISU, bezTekstu } from '../nazwy.js'

const OCENY = {
  oszustwo: 'To oszustwo',
  ok: 'Tekst w porządku',
}

const WERDYKTY_MODELU = {
  ok: 'tekst w porządku',
  do_sprawdzenia: 'tekst wymaga sprawdzenia',
  oszustwo: 'tekst wygląda na oszustwo',
}

const WERDYKTY_ANALITYKA = {
  oszustwo: 'to oszustwo',
  ok: 'tekst w porządku',
}

function procent(ryzyko) {
  const p = Math.round(ryzyko * 100)
  return p === 0 ? 'poniżej 1%' : p + '%'
}

// The model does not score video descriptions.
function opisFilmu(reklama) {
  return reklama.zrodlo === 'youtube'
}

function linia(reklama) {
  if (opisFilmu(reklama)) return 'Model KAPSEL: nie ocenia opisów filmów'
  if (bezTekstu(reklama)) return 'Model KAPSEL: brak tekstu do oceny'
  const analityk = WERDYKTY_ANALITYKA[reklama.werdykt_analityka]
  return (
    'Model KAPSEL: ' + WERDYKTY_MODELU[reklama.werdykt] + ' · ryzyko ' + procent(reklama.ryzyko) + (analityk ? ' · analityk: ' + analityk : '')
  )
}

export default function Ocena({ reklama, podmien }) {
  const [otwarta, setOtwarta] = useState(Boolean(reklama.werdykt_analityka))
  const zTekstem = !bezTekstu(reklama) && !opisFilmu(reklama)

  if (zTekstem && !reklama.werdykt) return null

  function zapisz(werdykt) {
    return zmienWerdyktAnalityka(reklama.id, werdykt).then(podmien)
  }

  function ustaw(werdykt) {
    const poprzedni = reklama.werdykt_analityka
    const nowy = werdykt === poprzedni ? null : werdykt
    zapisz(nowy)
      .then(() =>
        toast(nowy ? 'Ocena tekstu: ' + OCENY[nowy] : 'Usunięto ocenę tekstu', {
          duration: 5000,
          action: { label: 'Cofnij', onClick: () => zapisz(poprzedni).catch(() => toast.error(BLAD_ZAPISU)) },
        })
      )
      .catch(() => toast.error(BLAD_ZAPISU))
  }

  return (
    <div className="mt-1 text-[13px] text-muted-foreground">
      <div className="flex items-baseline gap-3">
        <p>{linia(reklama)}</p>
        {zTekstem && !otwarta && (
          <button className="ml-auto shrink-0 underline-offset-4 hover:text-foreground hover:underline" onClick={() => setOtwarta(true)}>
            Popraw
          </button>
        )}
      </div>
      {zTekstem && otwarta && (
        <div className="mt-2 flex items-center gap-1.5">
          {Object.entries(OCENY).map(([werdykt, nazwa]) => (
            <Button
              key={werdykt}
              size="xs"
              variant={werdykt === reklama.werdykt_analityka ? 'default' : 'outline'}
              aria-pressed={werdykt === reklama.werdykt_analityka}
              onClick={() => ustaw(werdykt)}
            >
              {nazwa}
            </Button>
          ))}
        </div>
      )}
    </div>
  )
}
