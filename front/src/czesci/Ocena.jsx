import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { pobierzProg, zmienWerdyktAnalityka } from '../api.js'
import { BLAD_ZAPISU, bezTekstu } from '../nazwy.js'
import { zdecydowalModel } from '../ustalenia.js'

const OCENY = {
  oszustwo: 'To oszustwo',
  ok: 'Tekst w porządku',
}

const WERDYKTY_MODELU = {
  ok: 'w porządku',
  do_sprawdzenia: 'do sprawdzenia',
  oszustwo: 'tekst jak w fałszywych inwestycjach',
}

const WERDYKTY_ANALITYKA = {
  oszustwo: 'to oszustwo',
  ok: 'tekst w porządku',
}

function procent(ryzyko) {
  const p = Math.round(ryzyko * 100)
  if (p === 0) return 'poniżej 1%'
  if (p === 100) return 'powyżej 99%'
  return p + '%'
}

// Model nie ocenia opisów wideo.
function opisFilmu(reklama) {
  return reklama.zrodlo === 'youtube'
}

function linia(reklama, prog) {
  if (opisFilmu(reklama)) return 'Model KAPSEL: nie ocenia opisów filmów'
  if (bezTekstu(reklama)) return 'Model KAPSEL: brak tekstu do oceny'
  const kto = zdecydowalModel(reklama) ? 'Zdecydował model KAPSEL: ' : 'Model KAPSEL (ocenia tylko tekst): '
  const analityk = WERDYKTY_ANALITYKA[reklama.werdykt_analityka]
  return (
    kto +
    WERDYKTY_MODELU[reklama.werdykt] +
    ', ryzyko ' +
    procent(reklama.ryzyko) +
    (prog == null ? '' : ', próg ' + Math.round(prog * 100) + '%') +
    (analityk ? ', analityk: ' + analityk : '')
  )
}

function slowa(reklama) {
  if (reklama.werdykt !== 'oszustwo' && reklama.werdykt !== 'do_sprawdzenia') return []
  return [...new Set(reklama.powody.map((p) => p.slowo.toLocaleLowerCase('pl')))].slice(0, 3)
}

export default function Ocena({ reklama, podmien }) {
  const [otwarta, setOtwarta] = useState(Boolean(reklama.werdykt_analityka))
  const [prog, setProg] = useState(null)
  const zTekstem = !bezTekstu(reklama) && !opisFilmu(reklama)

  useEffect(() => {
    pobierzProg()
      .then((zapis) => setProg(zapis.prog))
      .catch(() => {})
  }, [])

  if (zTekstem && !reklama.werdykt) return null
  const najmocniejsze = zTekstem ? slowa(reklama) : []

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
      <p>{linia(reklama, prog)}</p>
      {najmocniejsze.length > 0 && <p>Słowa, które najbardziej podniosły ocenę: {najmocniejsze.join(', ')}</p>}
      {zTekstem && !otwarta && (
        <button className="block underline-offset-4 hover:text-foreground hover:underline" onClick={() => setOtwarta(true)}>
          Popraw
        </button>
      )}
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
