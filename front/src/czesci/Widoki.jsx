import { liczba } from '../nazwy.js'

// Pierwszy widok jest widokiem startowym.
export const WIDOKI = [
  { nazwa: 'Podejrzane', zakres: { statusy: ['nowa'], ryzyka: ['wysokie', 'srednie'] } },
  { nazwa: 'Niskie ryzyko', zakres: { statusy: ['nowa'], ryzyka: ['niskie'] } },
  { nazwa: 'W toku', zakres: { statusy: ['w_toku'], ryzyka: [] } },
  { nazwa: 'Zamknięte', zakres: { statusy: ['zamknieta'], ryzyka: [] } },
]

function wybrany(widok, filtry) {
  return JSON.stringify(widok.zakres) === JSON.stringify({ statusy: filtry.statusy, ryzyka: filtry.ryzyka })
}

export default function Widoki({ filtry, zmien, ile }) {
  return (
    <div className="mb-3 flex shrink-0 gap-6 border-b">
      {WIDOKI.map((w) => (
        <button
          key={w.nazwa}
          aria-pressed={wybrany(w, filtry)}
          className={
            '-mb-px flex gap-1.5 border-b-2 pb-2 text-[15px] ' +
            (wybrany(w, filtry) ? 'border-foreground font-semibold text-foreground' : 'border-transparent text-muted-foreground hover:text-foreground')
          }
          onClick={() => zmien({ ...filtry, ...w.zakres, tagi: [] })}
        >
          {w.nazwa}
          <span className="font-normal tabular-nums text-muted-foreground">{liczba(ile({ ...w.zakres, tagi: [] }))}</span>
        </button>
      ))}
    </div>
  )
}
