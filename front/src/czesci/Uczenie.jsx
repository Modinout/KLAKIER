import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { uczModel } from '../api.js'
import { ileReklam, liczba } from '../nazwy.js'
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
    <div className="mt-6 flex items-center justify-between gap-6 rounded-lg border p-6">
      <div>
        <h2 className="font-medium">Douczanie modelu KAPSEL</h2>
        <p className="mt-1">Oceny tekstu od analityków: {liczba(decyzje)}</p>
        <p className="text-muted-foreground">
          Analityk ocenia tekst w sprawie, linkiem „Popraw ocenę modelu”. Douczony model ocenia od nowa wszystkie reklamy.
        </p>
      </div>
      <Potwierdzenie pytanie="Nauczyć model od nowa na decyzjach analityków?" przycisk="Ucz model" potwierdz={ucz}>
        <Button variant="outline" disabled={uczy || decyzje === 0}>
          {uczy ? 'Model się uczy…' : 'Doucz model z ocen'}
        </Button>
      </Potwierdzenie>
    </div>
  )
}
