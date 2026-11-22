import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { uczModel } from '../api.js'
import { OPISY, ileReklam, liczba } from '../nazwy.js'
import Potwierdzenie from './Potwierdzenie.jsx'

export default function Uczenie({ decyzje, odswiez }) {
  const [uczy, setUczy] = useState(false)

  function ucz() {
    setUczy(true)
    uczModel()
      .then((w) => {
        toast.success('Model nauczony. Oceniono od nowa ' + ileReklam(w.przeliczono) + '.')
        odswiez()
      })
      .catch(() => toast.error('Nie udało się nauczyć modelu. Spróbuj ponownie.'))
      .finally(() => setUczy(false))
  }

  return (
    <>
      <p className="text-muted-foreground">{OPISY.ucz}</p>
      <div className="mt-4 flex items-center justify-between gap-6">
        <div>
          <p>Oceny tekstu od analityków: {liczba(decyzje)}</p>
          {decyzje === 0 && <p className="text-muted-foreground">{OPISY.uczPusto}</p>}
        </div>
        <Potwierdzenie pytanie="Nauczyć model od nowa na decyzjach analityków?" przycisk="Ucz model" potwierdz={ucz}>
          <Button variant="outline" disabled={uczy || decyzje === 0}>
            {uczy ? 'Model się uczy…' : 'Doucz model z ocen'}
          </Button>
        </Potwierdzenie>
      </div>
    </>
  )
}
