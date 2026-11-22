import { useLayoutEffect, useRef, useState } from 'react'

const SAM_ADRES = /^(https?:\/\/)?[\w.-]+\.[a-z]{2,}(\/\S*)?$/i
const SAMA_DATA = /^\d{1,4}[.\-/]\d{1,2}[.\-/]\d{1,4}( \d{1,2}:\d{2}(:\d{2})?)?$/

// Niektóre kolektory zapisują skrypty strony zamiast jej tekstu.
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
  // Tekst odczytany z obrazu to szum: zostaje zwinięty, dopóki ktoś o niego nie poprosi.
  const zwiniety = !obraz && !caly

  useLayoutEffect(() => {
    const el = akapit.current
    if (el && zwiniety) setUciety(el.scrollHeight > el.clientHeight)
  }, [tekst, zwiniety])

  if (tekst === '') return null
  if (wygladaNaKod(tekst)) return <p className="text-muted-foreground">Tekst strony nie został poprawnie pobrany</p>

  const przycisk = obraz ? (caly ? 'Ukryj' : 'Pokaż odczytany tekst') : uciety || caly ? (caly ? 'Zwiń' : 'Pokaż całość') : null

  return (
    <>
      {(!obraz || caly) && (
        <p ref={akapit} className={'whitespace-pre-wrap break-words' + (zwiniety ? ' line-clamp-3' : '')}>
          {tekst}
        </p>
      )}
      {przycisk && (
        <button className="mt-1 text-[13px] font-medium" onClick={() => setCaly(!caly)}>
          {przycisk}
        </button>
      )}
    </>
  )
}
