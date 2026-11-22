import { adresObrazu } from '../api.js'

const NAJMNIEJ = 60
const PROBKI = 8
const ROZNICA = 8

// Some collectors save a blank tile or a pixel instead of the ad picture.
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

export default function Obraz({ reklama, ukryj }) {
  return (
    <div className="my-4 flex justify-center rounded-lg bg-muted p-3">
      <img
        src={adresObrazu(reklama.id)}
        alt="Obraz reklamy"
        className="max-h-80 max-w-full object-contain"
        onLoad={(e) => pusty(e.currentTarget) && ukryj()}
      />
    </div>
  )
}
