import { CartesianGrid, Line, LineChart, ReferenceDot, ReferenceLine, XAxis, YAxis } from 'recharts'
import { ChartContainer } from '@/components/ui/chart'
import { procent } from '../nazwy.js'

// Te same kolory co kafelki wyniku: text-emerald-600 i text-destructive.
const KONFIGURACJA = {
  zlapane: { label: 'Wyłapane oszustwa (%)', color: 'var(--color-emerald-600)' },
  alarmy: { label: 'Fałszywe alarmy (%)', color: 'var(--destructive)' },
}

const OS_Y = [0, 25, 50, 75, 100]

function Legenda() {
  return (
    <div className="flex flex-wrap gap-x-6 gap-y-1 text-xs text-muted-foreground">
      {Object.entries(KONFIGURACJA).map(([klucz, { label, color }]) => (
        <span key={klucz} className="flex items-center gap-2">
          <span className="w-5 border-t-2" style={{ borderColor: color }} />
          {label}
        </span>
      ))}
    </div>
  )
}

function Etykieta({ viewBox, value, color }) {
  return (
    <text x={viewBox.x + 8} y={viewBox.y - 8} fill={color} fontSize={12} fontWeight={600}>
      {value}
    </text>
  )
}

export default function WykresProgow({ punkty, prog }) {
  const punkt = punkty.find((p) => Math.abs(p.prog - prog) < 0.001)
  return (
    <>
      <Legenda />
      <ChartContainer config={KONFIGURACJA} className="mt-3 aspect-auto h-[220px] w-full">
        <LineChart data={punkty} margin={{ top: 16, right: 40, bottom: 0, left: 0 }}>
          <CartesianGrid vertical={false} />
          <XAxis
            dataKey="prog"
            type="number"
            domain={['dataMin', 'dataMax']}
            ticks={punkty.map((p) => p.prog)}
            tickFormatter={procent}
            tickLine={false}
            axisLine={false}
            tickMargin={8}
          />
          <YAxis width={40} domain={[0, 100]} ticks={OS_Y} tickFormatter={(v) => v + '%'} tickLine={false} axisLine={false} />
          <ReferenceLine x={prog} stroke="var(--foreground)" />
          <Line dataKey="zlapane" stroke="var(--color-zlapane)" strokeWidth={2} dot={false} isAnimationActive={false} />
          <Line dataKey="alarmy" stroke="var(--color-alarmy)" strokeWidth={2} dot={false} isAnimationActive={false} />
          {punkt &&
            Object.entries(KONFIGURACJA).map(([klucz, { color }]) => (
              <ReferenceDot
                key={klucz}
                x={punkt.prog}
                y={punkt[klucz]}
                r={4}
                fill={color}
                stroke="var(--background)"
                label={<Etykieta value={Math.round(punkt[klucz]) + '%'} color={color} />}
              />
            ))}
        </LineChart>
      </ChartContainer>
    </>
  )
}
