import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { pobierzPodobne, zmienStatusy } from '../api.js'
import { BLAD_ZAPISU, ileReklam, NAZWY_STATUSOW } from '../nazwy.js'
import { tytul } from '../sprawy.js'
import Potwierdzenie from './Potwierdzenie.jsx'
import Sekcja from './Sekcja.jsx'

export default function Podobne({ reklama, wSprawie, otworz, odswiez }) {
  const [podobne, setPodobne] = useState([])

  function wczytaj() {
    pobierzPodobne(reklama.id)
      .then((lista) => setPodobne(lista.filter((p) => p.zrodlo !== 'test' && !wSprawie.includes(p.id))))
      .catch(() => setPodobne([]))
  }

  useEffect(wczytaj, [reklama.id])

  function ustaw(pary, komunikat, cofnij) {
    zmienStatusy(pary)
      .then(() => {
        toast(komunikat, cofnij && { duration: 5000, action: { label: 'Cofnij', onClick: cofnij } })
        odswiez()
        wczytaj()
      })
      .catch(() => toast.error(BLAD_ZAPISU))
  }

  function zamknijWszystkie() {
    const poprzednie = [[reklama.id, reklama.status], ...podobne.map((p) => [p.id, p.status])]
    ustaw(
      poprzednie.map(([id]) => [id, 'zamknieta']),
      'Zamknięto ' + ileReklam(poprzednie.length),
      () => ustaw(poprzednie, 'Przywrócono poprzednie statusy')
    )
  }

  if (podobne.length === 0) return null
  const ile = podobne.length + 1

  return (
    <Sekcja tytul={'Podobne reklamy (' + podobne.length + ')'}>
      <ul className="max-h-52 divide-y overflow-auto rounded-lg border">
        {podobne.map((p) => (
          <li key={p.id}>
            <button className="grid w-full grid-cols-[1fr_auto_auto] gap-4 px-3.5 py-2 text-left hover:bg-muted/50" onClick={() => otworz(p.id)}>
              <span className="truncate">{tytul(p)}</span>
              <span className="font-mono text-xs leading-5 text-muted-foreground">{p.id}</span>
              <span className="w-20 text-muted-foreground">{NAZWY_STATUSOW[p.status]}</span>
            </button>
          </li>
        ))}
      </ul>
      <Potwierdzenie pytanie={'Zamknąć ' + ileReklam(ile) + '?'} przycisk="Zamknij" potwierdz={zamknijWszystkie}>
        <Button variant="outline" className="mt-2">
          Zamknij wszystkie
        </Button>
      </Potwierdzenie>
    </Sekcja>
  )
}
