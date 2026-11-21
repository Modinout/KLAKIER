import { liczba } from '../nazwy.js'

export default function Powody({ powody, wybrane, przelacz }) {
  return (
    <ul className="mb-3 flex shrink-0 flex-wrap gap-1.5 text-[13px]">
      {powody.map(([tag, ile]) => (
        <li key={tag}>
          <button
            aria-pressed={wybrane.includes(tag)}
            className={
              'flex max-w-[320px] rounded-full border px-2.5 py-0.5 ' +
              (wybrane.includes(tag)
                ? 'border-foreground bg-muted font-medium text-foreground'
                : 'border-border text-muted-foreground hover:text-foreground')
            }
            onClick={() => przelacz(tag)}
          >
            <span className="truncate">{tag}</span>
            <span className="ml-1.5 tabular-nums text-muted-foreground">{liczba(ile)}</span>
          </button>
        </li>
      ))}
    </ul>
  )
}
