import { CartesianGrid, Line, LineChart, ReferenceLine, XAxis, YAxis } from 'recharts'
import { ChartContainer } from '@/components/ui/chart'
import { liczba } from '../nazwy.js'

const KONFIGURACJA = {
  przeoczone: { label: 'Przeoczone oszustwa', color: 'var(--chart-5)' },
  alarmy: { label: 'Fałszywe alarmy', color: 'var(--chart-2)' },
}

const KRESKI = '6 4'

function Legenda({ oszustw, uczciwych }) {
  return (
    <div className="flex flex-wrap gap-x-6 gap-y-1 text-xs text-muted-foreground">
      <span className="flex items-center gap-2">
        <span className="w-5 border-t-2 border-chart-5" />
        Przeoczone oszustwa (z {liczba(oszustw)})
      </span>
      <span className="flex items-center gap-2">
        <span className="w-5 border-t-2 border-dashed border-chart-2" />
        Fałszywe alarmy (z {liczba(uczciwych)} uczciwych)
      </span>
    </div>
  )
}

export default function WykresProgow({ punkty, prog, oszustw, uczciwych }) {
  return (
    <>
      <Legenda oszustw={oszustw} uczciwych={uczciwych} />
      <ChartContainer config={KONFIGURACJA} className="mt-3 aspect-auto h-[220px] w-full">
        <LineChart data={punkty} margin={{ top: 8, right: 12, bottom: 0, left: 0 }}>
          <CartesianGrid vertical={false} />
          <XAxis
            dataKey="prog"
            type="number"
            domain={['dataMin', 'dataMax']}
            ticks={punkty.map((p) => p.prog)}
            tickFormatter={liczba}
            tickLine={false}
            axisLine={false}
            tickMargin={8}
          />
          <YAxis width={32} allowDecimals={false} tickLine={false} axisLine={false} />
          <ReferenceLine x={prog} stroke="var(--foreground)" />
          <Line dataKey="przeoczone" stroke="var(--color-przeoczone)" strokeWidth={2} dot={false} />
          <Line dataKey="alarmy" stroke="var(--color-alarmy)" strokeWidth={2} strokeDasharray={KRESKI} dot={false} />
        </LineChart>
      </ChartContainer>
    </>
  )
}
