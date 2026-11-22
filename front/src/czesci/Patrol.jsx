import { useEffect, useState } from 'react'
import { Loader2, Radar } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { ostatnieWyszukiwanie, pobierzWyszukiwanie, zlecWyszukiwanie } from '../api.js'
import { data, liczba } from '../nazwy.js'

const BLAD = 'Nie udało się przeszukać biblioteki reklam. Spróbuj ponownie.'
const CO_ILE_MS = 2000
const NAJDLUZEJ_MS = 10 * 60 * 1000

function czekaj(ms) {
  return new Promise((koniec) => setTimeout(koniec, ms))
}

function Wiersz({ fraza, szukana }) {
  if (fraza.dodane === null) {
    return (
      <>
        <span className={szukana ? '' : 'text-muted-foreground'}>{fraza.fraza}</span>
        <span className="col-span-3 flex justify-end text-muted-foreground">
          {fraza.blad ? 'brak odpowiedzi' : szukana && <Loader2 className="size-4 animate-spin" />}
        </span>
      </>
    )
  }
  return (
    <>
      <span>{fraza.fraza}</span>
      <span className="text-right">{liczba(fraza.w_bibliotece)}</span>
      <span className="text-right">{liczba(fraza.dodane + fraza.pominiete)}</span>
      <span className="text-right font-medium">{liczba(fraza.dodane)}</span>
    </>
  )
}

export default function Patrol({ odswiez }) {
  // Wyszukiwanie trwające albo ostatnie zakończone; null, gdy żadnego nie było.
  const [stan, setStan] = useState(null)
  const [otwarte, setOtwarte] = useState(false)

  useEffect(() => {
    ostatnieWyszukiwanie().then(setStan, () => {})
  }, [])

  const trwa = stan?.stan === 'w_kolejce' || stan?.stan === 'w_toku'
  const frazy = stan?.frazy ?? []
  const szukana = trwa ? frazy.findIndex((fraza) => fraza.dodane === null && !fraza.blad) : -1

  function nieudane(tekst) {
    toast.error(tekst)
    setStan({ stan: 'blad', blad: tekst, frazy: [] })
  }

  async function szukaj() {
    setStan({ stan: 'w_kolejce', frazy: [] })
    try {
      const { id } = await zlecWyszukiwanie()
      const start = Date.now()
      while (Date.now() - start < NAJDLUZEJ_MS) {
        await czekaj(CO_ILE_MS)
        const teraz = await pobierzWyszukiwanie(id)
        setStan(teraz)
        if (teraz.stan === 'blad') return toast.error(teraz.blad)
        if (teraz.stan === 'gotowe') {
          toast.success(`Patrol TikToka: nowe reklamy ${teraz.dodane}, już w bazie ${teraz.pominiete}`)
          return odswiez()
        }
      }
      nieudane('Patrol trwa zbyt długo. Spróbuj ponownie.')
    } catch (e) {
      nieudane(e.status === 503 ? e.tresc?.detail ?? BLAD : BLAD)
    }
  }

  function otworz(otwarte) {
    setOtwarte(otwarte)
    if (otwarte && !stan) szukaj()
  }

  return (
    <Popover open={otwarte} onOpenChange={otworz}>
      <PopoverTrigger asChild>
        <Button variant="outline" className="h-[34px] px-3.5">
          {trwa ? <Loader2 className="animate-spin" /> : <Radar />}
          {szukana < 0 ? 'Patrol' : `Patrol ${szukana + 1} z ${frazy.length}`}
        </Button>
      </PopoverTrigger>
      {stan && (
        <PopoverContent align="end" className="w-92 gap-3 p-3.5">
          <div className="flex items-baseline justify-between">
            <span className="font-medium">Biblioteka reklam TikToka</span>
            {!trwa && stan.kiedy && <span className="text-xs text-muted-foreground">{data(stan.kiedy)}</span>}
          </div>
          {stan.stan === 'w_kolejce' && <span className="text-muted-foreground">W kolejce</span>}
          {stan.stan === 'blad' && <span className="text-muted-foreground">{stan.blad}</span>}
          {frazy.length > 0 && (
            <div className="grid grid-cols-[1fr_auto_auto_auto] gap-x-4 gap-y-1.5 whitespace-nowrap tabular-nums">
              <span className="text-xs text-muted-foreground">Fraza</span>
              <span className="text-right text-xs text-muted-foreground">W bibliotece</span>
              <span className="text-right text-xs text-muted-foreground">Sprawdzone</span>
              <span className="text-right text-xs text-muted-foreground">Nowe</span>
              {frazy.map((fraza, i) => (
                <Wiersz key={fraza.fraza} fraza={fraza} szukana={i === szukana} />
              ))}
            </div>
          )}
          <Button size="sm" disabled={trwa} onClick={szukaj}>
            Szukaj ponownie
          </Button>
        </PopoverContent>
      )}
    </Popover>
  )
}
