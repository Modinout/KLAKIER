import { useEffect, useState } from 'react'
import { buttonVariants } from '@/components/ui/button'
import { adresDowodu, adresPaczki, pobierzDowody } from '../api.js'
import { data } from '../nazwy.js'

const RODZAJE = { komputer: 'Komputer', telefon: 'Telefon' }

// Api zwraca wiersze od najstarszego, po jednym wierszu z komputera i z telefonu na wizytę.
function wizyty(dowody) {
  const grupy = []
  for (const d of dowody) {
    const ostatnia = grupy.at(-1)
    if (ostatnia && !ostatnia.some((x) => x.rodzaj === d.rodzaj)) ostatnia.push(d)
    else grupy.push([d])
  }
  return grupy.reverse()
}

function Karta({ dowod }) {
  const obraz = adresDowodu(dowod.id, 'obraz')
  return (
    <div className="min-w-0 rounded-lg border p-2.5 text-[13px]">
      <div className="mb-2 flex justify-between gap-2">
        <span className="font-medium">{RODZAJE[dowod.rodzaj]}</span>
        <span className="text-muted-foreground">{data(dowod.kiedy)}</span>
      </div>
      <a href={obraz} target="_blank" rel="noreferrer">
        <img src={obraz} alt={'Zrzut strony: ' + RODZAJE[dowod.rodzaj]} loading="lazy" className="h-[120px] w-full rounded border object-cover object-top" />
      </a>
      <div className="mt-2 font-mono text-xs leading-5 text-muted-foreground" title={dowod.sha256.obraz}>
        SHA-256 {dowod.sha256.obraz.slice(0, 16)}
      </div>
      <a href={adresDowodu(dowod.id, 'html')} className="underline underline-offset-4">
        Kod strony
      </a>
    </div>
  )
}

export default function Dowody({ reklama }) {
  const [dowody, setDowody] = useState([])

  useEffect(() => {
    let aktualne = true
    setDowody([])
    pobierzDowody(reklama.id)
      .then((lista) => aktualne && setDowody(lista))
      .catch(() => null)
    return () => {
      aktualne = false
    }
  }, [reklama.id])

  if (dowody.length === 0) return null

  return (
    <section className="mt-6">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="font-medium">Dowody</h3>
        <a href={adresPaczki(reklama.id)} download className={buttonVariants({ variant: 'outline', size: 'sm' })}>
          Pobierz paczkę
        </a>
      </div>
      <div className="space-y-4">
        {wizyty(dowody).map((wizyta) => (
          <div key={wizyta[0].id}>
            {wizyta[0].lancuch.length > 1 && (
              <p className="mb-2 text-[13px] break-words text-muted-foreground">{wizyta[0].lancuch.join(' → ')}</p>
            )}
            <div className="grid grid-cols-2 gap-3">
              {wizyta.map((d) => (
                <Karta key={d.id} dowod={d} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
