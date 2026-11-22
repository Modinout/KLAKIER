import { useMemo } from 'react'
import { Bar, BarChart, XAxis } from 'recharts'
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart'
import { dzien, dzienCzytelny } from '../nazwy.js'
import { dzienReklamy, klucz } from '../sprawy.js'

const DNI = 30

const KONFIGURACJA = { ile: { label: 'Sprawy wysokiego ryzyka', color: 'var(--chart-3)' } }

// Dni z kilkoma sprawami zostają widoczne obok najbardziej obciążonego dnia.
const NAJNIZSZY_SLUPEK = 3

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
  return dni.map((d) => ({ kiedy: dzienCzytelny(d), ile: sprawyDnia.get(d).size }))
}

export default function Trend({ reklamy }) {
  const punkty = useMemo(() => zlicz(reklamy), [reklamy])
  const szczyt = punkty.reduce((max, p) => (p.ile >= max.ile ? p : max))

  return (
    <div className="w-[420px] shrink-0">
      <p className="text-xs text-muted-foreground">
        Wysokie ryzyko dziennie, ostatnie {DNI} dni
        {szczyt.ile > 0 && ' · najwięcej ' + szczyt.ile + ' (' + szczyt.kiedy.slice(0, 5) + ')'}
      </p>
      <ChartContainer config={KONFIGURACJA} className="aspect-auto h-[44px] w-full">
        <BarChart data={punkty} margin={{ top: 4, right: 0, bottom: 0, left: 0 }}>
          <XAxis dataKey="kiedy" tickLine={false} axisLine={false} tickMargin={4} minTickGap={24} height={20} fontSize={11} />
          <ChartTooltip cursor={false} content={<ChartTooltipContent />} />
          <Bar
            dataKey="ile"
            fill="var(--color-ile)"
            radius={2}
            maxBarSize={24}
            minPointSize={(ile) => (ile > 0 ? NAJNIZSZY_SLUPEK : 0)}
          />
        </BarChart>
      </ChartContainer>
    </div>
  )
}
