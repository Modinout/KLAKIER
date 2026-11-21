import { useLayoutEffect, useRef, useState } from 'react'

// Text this short next to a picture only repeats what the picture says.
const KROTKI_PRZY_OBRAZIE = 400

const SAM_ADRES = /^(https?:\/\/)?[\w.-]+\.[a-z]{2,}(\/\S*)?$/i
const SAMA_DATA = /^\d{1,4}[.\-/]\d{1,2}[.\-/]\d{1,4}( \d{1,2}:\d{2}(:\d{2})?)?$/

// Some collectors save a page's scripts instead of its text.
function wygladaNaKod(tekst) {
  return tekst.trimStart().startsWith('(function') || ['SPDX-License', '<script', 'function('].some((k) => tekst.includes(k))
}

function bezNaglowka(tekst) {
  const linie = tekst.split('\n')
  const pierwsza = linie.findIndex((l) => !SAM_ADRES.test(l.trim()) && !SAMA_DATA.test(l.trim()) && l.trim() !== '')
  return pierwsza === -1 ? tekst : linie.slice(pierwsza).join('\n')
}

export default function Tekst({ reklama, obraz }) {
  const [caly, setCaly] = useState(false)
  const [uciety, setUciety] = useState(false)
  const akapit = useRef(null)
  const tekst = bezNaglowka(reklama.tekst.trim())
  const linii = obraz && tekst.length < KROTKI_PRZY_OBRAZIE ? 1 : 3

  useLayoutEffect(() => {
    const el = akapit.current
    if (el && !caly) setUciety(el.scrollHeight > el.clientHeight)
  }, [tekst, linii, caly])

  if (tekst === '') return null
  if (wygladaNaKod(tekst)) return <p className="text-muted-foreground">Tekst strony nie został poprawnie pobrany</p>

  return (
    <>
      <p ref={akapit} className={'whitespace-pre-wrap' + (caly ? '' : linii === 1 ? ' line-clamp-1' : ' line-clamp-3')}>
        {tekst}
      </p>
      {(uciety || caly) && (
        <button className="mt-1 text-[13px] font-medium" onClick={() => setCaly(!caly)}>
          {caly ? 'Zwiń' : 'Pokaż całość'}
        </button>
      )}
    </>
  )
}
