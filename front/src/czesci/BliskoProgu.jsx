import { useMemo } from 'react'
import { Badge } from '@/components/ui/badge'
import { tytul } from '../sprawy.js'

const ILE = 5

// Rounding down keeps the shown score on the same side of the threshold as the real one.
function ocena(ryzyko) {
  return (Math.floor(ryzyko * 100 + 1e-9) / 100).toLocaleString('pl-PL', { minimumFractionDigits: 2 })
}

function najblizsze(wiersze, prog) {
  return wiersze
    .filter((r) => typeof r.ryzyko === 'number')
    .sort((a, b) => Math.abs(a.ryzyko - prog) - Math.abs(b.ryzyko - prog) || a.id - b.id)
    .slice(0, ILE)
    .sort((a, b) => b.ryzyko - a.ryzyko)
}

export default function BliskoProgu({ wiersze, prog }) {
  const lista = useMemo(() => najblizsze(wiersze, prog), [wiersze, prog])

  return (
    <>
      <h2 className="font-medium">Reklamy z bazy najbliżej progu</h2>
      {lista.length === 0 && <p className="mt-2 text-muted-foreground">Brak ocenionych reklam w bazie.</p>}
      <ul className="mt-2 divide-y">
        {lista.map((r) => (
          <li key={r.id} className="flex h-10 items-center gap-4">
            <span className="min-w-0 flex-1 truncate">{tytul(r)}</span>
            <span className="tabular-nums">{ocena(r.ryzyko)}</span>
            <Badge variant={r.ryzyko >= prog ? 'default' : 'outline'} className="w-24">
              {r.ryzyko >= prog ? 'Alarm' : 'Bez alarmu'}
            </Badge>
          </li>
        ))}
      </ul>
    </>
  )
}
