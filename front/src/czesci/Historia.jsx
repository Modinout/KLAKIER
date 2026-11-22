import { useEffect, useState } from 'react'
import { pobierzHistorie } from '../api.js'
import { data } from '../nazwy.js'
import Sekcja from './Sekcja.jsx'

const NA_POCZATEK = 5

export default function Historia({ reklama }) {
  const [wpisy, setWpisy] = useState([])
  const [wszystkie, setWszystkie] = useState(false)

  // Api nie wysyła historii samo, więc jest czytana ponownie po każdej zmianie tej reklamy.
  useEffect(() => {
    let aktualne = true
    pobierzHistorie(reklama.id)
      .then((lista) => aktualne && setWpisy(lista))
      .catch(() => null)
    return () => {
      aktualne = false
    }
  }, [reklama.id, reklama.status, reklama.werdykt_analityka, reklama.notatka])

  if (wpisy.length === 0) return null
  const widoczne = wszystkie ? wpisy : wpisy.slice(0, NA_POCZATEK)

  return (
    <Sekcja tytul="Historia zmian">
      <ul className="space-y-1 text-[13px]">
        {widoczne.map((w, i) => (
          <li key={i}>
            <span className="text-muted-foreground">
              {data(w.kiedy)} · {w.kto} ·{' '}
            </span>
            {w.co}
          </li>
        ))}
      </ul>
      {!wszystkie && wpisy.length > NA_POCZATEK && (
        <button className="mt-2 text-[13px] text-muted-foreground hover:text-foreground" onClick={() => setWszystkie(true)}>
          Pokaż wszystkie ({wpisy.length})
        </button>
      )}
    </Sekcja>
  )
}
