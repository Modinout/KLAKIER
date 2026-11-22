import { useEffect, useState } from 'react'
import { pobierzPowiazane } from '../api.js'
import { NAZWY_POWIAZAN } from '../nazwy.js'
import Sekcja from './Sekcja.jsx'

export default function Powiazane({ reklama, otworz }) {
  const [powiazane, setPowiazane] = useState([])

  useEffect(() => {
    let aktualne = true
    setPowiazane([])
    pobierzPowiazane(reklama.id)
      .then((lista) => aktualne && setPowiazane(lista))
      .catch(() => null)
    return () => {
      aktualne = false
    }
  }, [reklama.id])

  if (powiazane.length === 0) return null

  return (
    <Sekcja tytul={'Powiązane sprawy (' + powiazane.length + ')'}>
      <ul className="max-h-52 divide-y overflow-auto rounded-lg border">
        {powiazane.map((p) => (
          <li key={p.id}>
            <button className="grid w-full grid-cols-[auto_1fr] gap-x-4 px-3.5 py-2 text-left hover:bg-muted/50" onClick={() => otworz(p.id)}>
              <span className="font-mono text-xs leading-5 text-muted-foreground">{p.id}</span>
              <span className="truncate">{p.tytul}</span>
              <span className="col-start-2 truncate text-[13px]">
                {NAZWY_POWIAZAN[p.powod]} <span className="text-muted-foreground">{p.wartosc}</span>
              </span>
            </button>
          </li>
        ))}
      </ul>
    </Sekcja>
  )
}
