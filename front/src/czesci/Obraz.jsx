import { useState } from 'react'
import { adresObrazu } from '../api.js'

const NAJMNIEJ = 60
const PROBKI = 8
const ROZNICA = 8

// Niektóre kolektory zapisują pusty kafelek albo piksel zamiast obrazu reklamy.
function pusty(img) {
  if (img.naturalWidth < NAJMNIEJ || img.naturalHeight < NAJMNIEJ) return true
  const plotno = document.createElement('canvas')
  plotno.width = PROBKI
  plotno.height = PROBKI
  const kontekst = plotno.getContext('2d')
  kontekst.drawImage(img, 0, 0, PROBKI, PROBKI)
  const piksele = kontekst.getImageData(0, 0, PROBKI, PROBKI).data
  return piksele.every((wartosc, i) => Math.abs(wartosc - piksele[i % 4]) <= ROZNICA)
}

// Zrzut całej strony jest wielokrotnie wyższy niż szerszy; liczy się jego górna część.
function stronaCala(img) {
  return img.naturalHeight > 2 * img.naturalWidth
}

export default function Obraz({ reklama, ukryj }) {
  const [wysoki, setWysoki] = useState(false)

  function wczytany(img) {
    if (pusty(img)) return ukryj()
    setWysoki(stronaCala(img))
  }

  return (
    <div className="my-4 flex justify-center rounded-lg bg-muted p-3">
      <img
        src={adresObrazu(reklama.id)}
        alt="Obraz reklamy"
        className={wysoki ? 'h-[420px] w-full object-cover object-top' : 'max-h-80 max-w-full object-contain'}
        onLoad={(e) => wczytany(e.currentTarget)}
      />
    </div>
  )
}
