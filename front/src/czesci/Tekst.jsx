import { useState } from 'react'

// Some collectors save a page's scripts instead of its text.
function wygladaNaKod(tekst) {
  return tekst.trimStart().startsWith('(function') || ['SPDX-License', '<script', 'function('].some((k) => tekst.includes(k))
}

function dlugi(tekst) {
  return tekst.length > 280 || tekst.split('\n').length > 4
}

export default function Tekst({ reklama }) {
  const [caly, setCaly] = useState(false)
  const tekst = reklama.tekst.trim()
  if (tekst === '') return null
  if (wygladaNaKod(tekst)) return <p className="text-muted-foreground">Tekst strony nie został poprawnie pobrany</p>

  const slowa = reklama.powody.map((p) => p.slowo)

  return (
    <>
      <p className={'whitespace-pre-wrap' + (caly ? '' : ' line-clamp-4')}>
        {tekst.split(/(\s+)/).map((kawalek, i) =>
          slowa.includes(kawalek) ? (
            <mark key={i} className="rounded-sm bg-muted px-0.5 font-medium text-foreground">
              {kawalek}
            </mark>
          ) : (
            kawalek
          )
        )}
      </p>
      {dlugi(tekst) && (
        <button className="mt-1 text-[13px] font-medium" onClick={() => setCaly(!caly)}>
          {caly ? 'Zwiń' : 'Pokaż całość'}
        </button>
      )}
    </>
  )
}
