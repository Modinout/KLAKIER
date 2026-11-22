import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { zmienNotatke } from '../api.js'
import { BLAD_ZAPISU } from '../nazwy.js'
import Sekcja from './Sekcja.jsx'

export default function Notatka({ reklama, podmien }) {
  const [tekst, setTekst] = useState(reklama.notatka ?? '')

  function zapisz() {
    zmienNotatke(reklama.id, tekst.trim() || null)
      .then((nowa) => {
        podmien(nowa)
        setTekst(nowa.notatka ?? '')
        toast('Notatka zapisana')
      })
      .catch(() => toast.error(BLAD_ZAPISU))
  }

  return (
    <Sekcja tytul="Notatka">
      <Textarea aria-label="Notatka" value={tekst} onChange={(e) => setTekst(e.target.value)} />
      {tekst !== (reklama.notatka ?? '') && (
        <Button size="sm" className="mt-2" onClick={zapisz}>
          Zapisz notatkę
        </Button>
      )}
    </Sekcja>
  )
}
