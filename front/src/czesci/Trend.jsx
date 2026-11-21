import { useMemo } from 'react'
import { Bar, BarChart, XAxis } from 'recharts'
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart'
import { dzien } from '../nazwy.js'
import { dzienReklamy, klucz } from '../sprawy.js'

const DNI = 30

const KONFIGURACJA = { ile: { label: 'Sprawy', color: 'var(--chart-3)' } }

function zlicz(reklamy) {
  const dni = Array.from({ length: DNI }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() - (DNI - 1 - i))
    return dzien(d)
  })
  const sprawyDnia = new Map(dni.map((d) => [d, new Set()]))
  for (const r of reklamy) {
    if (r.poziom === 'wysokie') sprawyDnia.get(dzienReklamy(r))?.add(klucz(r))
  }
  return dni.map((d) => ({ kiedy: d.slice(8, 10) + '.' + d.slice(5, 7), ile: sprawyDnia.get(d).size }))
}

export default function Trend({ reklamy }) {
  const punkty = useMemo(() => zlicz(reklamy), [reklamy])

  return (
    <div className="mb-3 shrink-0">
      <p className="text-xs text-muted-foreground">Wysokie ryzyko dziennie</p>
      <ChartContainer config={KONFIGURACJA} className="aspect-auto h-[88px] w-full">
        <BarChart data={punkty} margin={{ top: 4, right: 0, bottom: 0, left: 0 }}>
          <XAxis dataKey="kiedy" tickLine={false} axisLine={false} tickMargin={4} interval={0} height={20} fontSize={11} />
          <ChartTooltip cursor={false} content={<ChartTooltipContent />} />
          <Bar dataKey="ile" fill="var(--color-ile)" radius={2} maxBarSize={24} />
        </BarChart>
      </ChartContainer>
    </div>
  )
}
