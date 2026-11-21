import { ArrowRight } from 'lucide-react'
import { ileSpraw } from '../nazwy.js'
import { najmocniejszyTag } from '../sprawy.js'

export default function Srednie({ sprawy, wybierz }) {
  const powody = [...Map.groupBy(sprawy, najmocniejszyTag)].sort((a, b) => b[1].length - a[1].length)

  return (
    <div className="mt-3 flex shrink-0 flex-wrap items-center gap-x-5 gap-y-1 rounded-lg border px-4 py-2.5">
      <p className="flex items-center gap-2 font-medium">
        <ArrowRight className="size-4 text-muted-foreground" />
        Średnie ryzyko: {ileSpraw(sprawy.length)}
      </p>
      <ul className="contents">
        {powody.map(([tag, lista]) => (
          <li key={tag}>
            <button className="text-muted-foreground hover:text-foreground hover:underline" onClick={() => wybierz(tag)}>
              {tag} · {ileSpraw(lista.length)}
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
