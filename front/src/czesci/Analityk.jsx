import { useState } from 'react'
import { User } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { analityk, ustawAnalityka } from '../analityk.js'

export default function Analityk() {
  const [nazwa, setNazwa] = useState(analityk())
  const [pole, setPole] = useState(nazwa)
  const [otwarte, setOtwarte] = useState(false)

  function zapisz(zdarzenie) {
    zdarzenie.preventDefault()
    const nowa = pole.trim()
    ustawAnalityka(nowa)
    setNazwa(nowa)
    setOtwarte(false)
  }

  return (
    <Popover
      open={otwarte}
      onOpenChange={(czy) => {
        setOtwarte(czy)
        setPole(nazwa)
      }}
    >
      <PopoverTrigger asChild>
        <Button variant="ghost" className="h-[34px] px-3">
          <User />
          {nazwa || 'Analityk'}
        </Button>
      </PopoverTrigger>
      <PopoverContent align="end">
        <form className="flex gap-2" onSubmit={zapisz}>
          <Input value={pole} placeholder="Imię i nazwisko" onChange={(e) => setPole(e.target.value)} />
          <Button type="submit">Zapisz</Button>
        </form>
      </PopoverContent>
    </Popover>
  )
}
