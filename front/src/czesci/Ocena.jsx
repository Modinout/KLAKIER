import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { zmienWerdyktAnalityka } from '../api.js'
import { BLAD_ZAPISU, NAZWY_WERDYKTOW } from '../nazwy.js'

const OCENY = ['oszustwo', 'do_sprawdzenia', 'ok']

export default function Ocena({ reklama, podmien }) {
  function ustaw(werdykt) {
    const nowy = werdykt === reklama.werdykt_analityka ? null : werdykt
    zmienWerdyktAnalityka(reklama.id, nowy)
      .then(podmien)
      .catch(() => toast.error(BLAD_ZAPISU))
  }

  return (
    <div className="flex items-center gap-1.5 py-1 pl-[18px]">
      <span className="mr-1 text-[13px] text-muted-foreground">Ocena tekstu:</span>
      {OCENY.map((werdykt) => (
        <Button
          key={werdykt}
          size="xs"
          variant={werdykt === reklama.werdykt_analityka ? 'default' : 'outline'}
          aria-pressed={werdykt === reklama.werdykt_analityka}
          onClick={() => ustaw(werdykt)}
        >
          {werdykt === 'ok' ? 'W porządku' : NAZWY_WERDYKTOW[werdykt]}
        </Button>
      ))}
    </div>
  )
}
