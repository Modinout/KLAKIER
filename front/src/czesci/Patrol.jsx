import { useEffect, useState } from 'react'
import { Radar } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { pobierzWyszukiwanie, zlecWyszukiwanie } from '../api.js'

const BLAD = 'Nie udało się przeszukać biblioteki reklam. Spróbuj ponownie.'
const CO_ILE_MS = 2000
const NAJDLUZEJ_MS = 10 * 60 * 1000

function czekaj(ms) {
  return new Promise((koniec) => setTimeout(koniec, ms))
}

export default function Patrol({ odswiez }) {
  // Sekundy od zlecenia wyszukiwania; null, gdy nic się nie szuka.
  const [sekundy, setSekundy] = useState(null)

  useEffect(() => {
    if (sekundy === null) return
    const zegar = setTimeout(() => setSekundy((s) => (s === null ? null : s + 1)), 1000)
    return () => clearTimeout(zegar)
  }, [sekundy])

  async function szukaj() {
    setSekundy(0)
    try {
      const { id } = await zlecWyszukiwanie()
      const start = Date.now()
      while (Date.now() - start < NAJDLUZEJ_MS) {
        await czekaj(CO_ILE_MS)
        const stan = await pobierzWyszukiwanie(id)
        if (stan.stan === 'blad') return toast.error(stan.blad)
        if (stan.stan === 'gotowe') {
          toast.success(`Patrol TikToka: nowe reklamy ${stan.dodane}, już w bazie ${stan.pominiete}`)
          return odswiez()
        }
      }
      toast.error('Patrol trwa zbyt długo. Spróbuj ponownie.')
    } catch (e) {
      toast.error(e.status === 503 ? e.tresc?.detail ?? BLAD : BLAD)
    } finally {
      setSekundy(null)
    }
  }

  return (
    <Button variant="outline" className="h-[34px] px-3.5" disabled={sekundy !== null} onClick={szukaj}>
      <Radar />
      {sekundy === null ? 'Patrol' : 'Patrol… ' + sekundy + ' s'}
    </Button>
  )
}
