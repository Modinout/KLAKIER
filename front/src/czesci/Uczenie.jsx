import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { uczModel, dodajRodzaj } from '../api.js'
import { OPISY, ileReklam, liczba } from '../nazwy.js'
import Potwierdzenie from './Potwierdzenie.jsx'

function bladRodzaju(blad) {
  if (blad.status === 409) return 'Taki rodzaj oszustwa już jest.'
  if (blad.status === 503) return 'Duży model jest teraz niedostępny. Spróbuj później.'
  return 'Nie udało się dodać rodzaju. Spróbuj ponownie.'
}

export default function Uczenie({ decyzje, odswiez }) {
  const [uczy, setUczy] = useState(false)
  const [dodaje, setDodaje] = useState(false)
  const [nazwa, setNazwa] = useState('')
  const [opis, setOpis] = useState('')

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

  function dodaj(zdarzenie) {
    zdarzenie.preventDefault()
    setDodaje(true)
    dodajRodzaj(nazwa, opis)
      .then((w) => {
        toast.success('Dodano rodzaj: ' + w.nazwa)
        setNazwa('')
        setOpis('')
        odswiez()
      })
      .catch((e) => toast.error(bladRodzaju(e)))
      .finally(() => setDodaje(false))
  }

  return (
    <>
      <div className="flex items-center gap-4">
        <Potwierdzenie pytanie="Nauczyć model od nowa na decyzjach analityków?" przycisk="Ucz model" potwierdz={ucz}>
          <Button variant="outline" disabled={uczy || decyzje === 0}>
            {uczy ? 'Model się uczy…' : 'Ucz model z decyzji'}
          </Button>
        </Potwierdzenie>
        <span className="text-muted-foreground">Decyzje analityków: {liczba(decyzje)}</span>
      </div>
      <p className="mt-2 text-muted-foreground">{OPISY.ucz}</p>
      <form className="mt-5 flex items-end gap-2" onSubmit={dodaj}>
        <div className="grid flex-1 gap-1.5">
          <Label htmlFor="nazwa-rodzaju">Nazwa rodzaju</Label>
          <Input id="nazwa-rodzaju" value={nazwa} onChange={(e) => setNazwa(e.target.value)} required />
        </div>
        <div className="grid flex-1 gap-1.5">
          <Label htmlFor="opis-rodzaju">Opis</Label>
          <Input id="opis-rodzaju" value={opis} onChange={(e) => setOpis(e.target.value)} required />
        </div>
        <Button variant="outline" disabled={dodaje}>
          {dodaje ? 'Model pisze przykłady…' : 'Dodaj'}
        </Button>
      </form>
      <p className="mt-2 text-muted-foreground">{OPISY.rodzaj}</p>
    </>
  )
}
