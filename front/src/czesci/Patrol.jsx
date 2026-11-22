import { useEffect, useState } from 'react'
import { Radar } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { pobierzOstatnieWyszukiwanie, pobierzWyszukiwanie, zlecWyszukiwanie } from '../api.js'

const BLAD = 'Nie udało się przeszukać biblioteki. Spróbuj ponownie.'
const CO_ILE_MS = 2000
const NAJDLUZEJ_MS = 5 * 60 * 1000

function czekaj(ms) {
  return new Promise((koniec) => setTimeout(koniec, ms))
}

function opis(wynik) {
  const kiedy = new Date(wynik.kiedy).toLocaleString('pl-PL', { dateStyle: 'short', timeStyle: 'short' })
  return `„${wynik.fraza}”, ${kiedy}: nowe reklamy ${wynik.dodane}, już w bazie ${wynik.pominiete}`
}

export default function Patrol({ odswiez }) {
  const [otwarte, setOtwarte] = useState(false)
  const [fraza, setFraza] = useState('')
  // Sekundy od zlecenia wyszukiwania; null, gdy nic się nie szuka.
  const [sekundy, setSekundy] = useState(null)
  const [wynik, setWynik] = useState(null)
  const [blad, setBlad] = useState('')

  useEffect(() => {
    if (!otwarte) return
    pobierzOstatnieWyszukiwanie()
      .then((ostatnie) => setWynik((w) => w ?? ostatnie))
      .catch(() => {})
  }, [otwarte])

  useEffect(() => {
    if (sekundy === null) return
    const zegar = setTimeout(() => setSekundy((s) => (s === null ? null : s + 1)), 1000)
    return () => clearTimeout(zegar)
  }, [sekundy])

  async function szukaj(zdarzenie) {
    zdarzenie.preventDefault()
    setBlad('')
    setSekundy(0)
    try {
      const { id } = await zlecWyszukiwanie(fraza)
      const start = Date.now()
      while (Date.now() - start < NAJDLUZEJ_MS) {
        await czekaj(CO_ILE_MS)
        const stan = await pobierzWyszukiwanie(id)
        if (stan.stan === 'blad') return setBlad(stan.blad)
        if (stan.stan === 'gotowe') {
          setWynik(stan)
          return odswiez()
        }
      }
      setBlad('Wyszukiwanie trwa zbyt długo. Spróbuj ponownie.')
    } catch (e) {
      setBlad(e.status === 503 ? e.tresc?.detail ?? BLAD : BLAD)
    } finally {
      setSekundy(null)
    }
  }

  return (
    <Dialog open={otwarte} onOpenChange={setOtwarte}>
      <DialogTrigger asChild>
        <Button variant="outline" className="h-[34px] px-3.5">
          <Radar />
          Patrol
        </Button>
      </DialogTrigger>
      <DialogContent className="p-6 sm:max-w-lg" aria-describedby={undefined}>
        <DialogTitle className="text-lg font-semibold">Patrol biblioteki reklam TikToka</DialogTitle>
        <form className="flex gap-2" onSubmit={szukaj}>
          <Input aria-label="Fraza" placeholder="forex" maxLength={100} value={fraza} onChange={(e) => setFraza(e.target.value)} />
          <Button type="submit" disabled={!fraza.trim() || sekundy !== null}>
            {sekundy === null ? 'Szukaj reklam' : 'Szukam… ' + sekundy + ' s'}
          </Button>
        </form>
        {blad ? <p className="text-destructive">{blad}</p> : wynik && sekundy === null && <p className="text-muted-foreground">{opis(wynik)}</p>}
      </DialogContent>
    </Dialog>
  )
}
