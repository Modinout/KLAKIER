import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { zmienWerdyktAnalityka } from '../api.js'
import { BLAD_ZAPISU } from '../nazwy.js'

const OCENY = {
  oszustwo: 'To oszustwo',
  do_sprawdzenia: 'Wymaga sprawdzenia',
  ok: 'Tekst w porządku',
}

const WERDYKTY_MODELU = {
  oszustwo: 'oszustwo',
  do_sprawdzenia: 'wymaga sprawdzenia',
  ok: 'tekst w porządku',
}

export default function Ocena({ reklama, podmien }) {
  const [otwarta, setOtwarta] = useState(Boolean(reklama.werdykt_analityka))

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

  if (!otwarta) {
    return (
      <button className="mt-6 block text-[13px] text-muted-foreground hover:text-foreground" onClick={() => setOtwarta(true)}>
        Oceń tekst (uczy model)
      </button>
    )
  }

  return (
    <div className="mt-6">
      {reklama.werdykt && (
        <p className="mb-2 text-[13px] text-muted-foreground">Ocena modelu KAPSEL: {WERDYKTY_MODELU[reklama.werdykt]}</p>
      )}
      <div className="flex items-center gap-1.5">
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
    </div>
  )
}
