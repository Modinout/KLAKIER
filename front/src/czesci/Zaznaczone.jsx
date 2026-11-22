import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { zmienStatusy } from '../api.js'
import { BLAD_ZAPISU, liczba } from '../nazwy.js'
import { pobierzPlik } from '../pobierz.js'
import { nazwaRaportu, raport } from '../raport.js'

export default function Zaznaczone({ sprawy, podmien, poZamknieciu }) {
  function zamknij() {
    const reklamy = sprawy.flatMap((s) => s.reklamy)
    const poprzednie = reklamy.map((r) => [r.id, r.status])
    zmienStatusy(reklamy.map((r) => [r.id, 'zamknieta']))
      .then((nowe) => {
        nowe.forEach(podmien)
        poZamknieciu()
        toast('Zamknięto sprawy: ' + liczba(sprawy.length), { duration: 5000, action: { label: 'Cofnij', onClick: () => cofnij(poprzednie) } })
      })
      .catch(() => toast.error(BLAD_ZAPISU))
  }

  function cofnij(poprzednie) {
    zmienStatusy(poprzednie)
      .then((nowe) => nowe.forEach(podmien))
      .catch(() => toast.error(BLAD_ZAPISU))
  }

  return (
    <div className="mb-2 flex shrink-0 flex-wrap items-center gap-2 rounded-lg bg-muted px-3 py-1.5">
      <span className="mr-2 font-medium">Zaznaczono: {liczba(sprawy.length)}</span>
      <Button size="sm" variant="outline" onClick={zamknij}>
        Zamknij zaznaczone
      </Button>
      <Button size="sm" variant="outline" onClick={() => pobierzPlik(raport(sprawy), 'text/csv;charset=utf-8', nazwaRaportu())}>
        Pobierz raport zaznaczonych
      </Button>
    </div>
  )
}
