import { liczba } from '../nazwy.js'

export default function Powody({ powody, wybrane, przelacz }) {
  return (
    <ul className="mb-3 flex shrink-0 flex-wrap gap-x-1 gap-y-1 text-[13px]">
      {powody.map(([tag, ile]) => (
        <li key={tag}>
          <button
            aria-pressed={wybrane.includes(tag)}
            className={
              'flex max-w-[320px] rounded-md px-2 py-1 ' +
              (wybrane.includes(tag) ? 'bg-muted font-medium' : 'text-muted-foreground hover:bg-muted hover:text-foreground')
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
