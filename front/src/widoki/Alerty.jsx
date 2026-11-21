import TabelaSpraw from '../czesci/TabelaSpraw.jsx'
import { data, ileReklam } from '../nazwy.js'
import { sprawa } from '../sprawy.js'

function odNajnowszych(a, b) {
  return b.glowna.dodano.localeCompare(a.glowna.dodano)
}

export default function Alerty({ alerty, obejrzane, otwarteId, otworz }) {
  const sprawy = alerty.map((r) => sprawa([r])).sort(odNajnowszych)

  return (
    <>
      <h1 className="mb-5 text-2xl font-bold tracking-tight">Alerty</h1>
      <TabelaSpraw
        sprawy={sprawy}
        ile={ileReklam(sprawy.length)}
        kiedy={(s) => data(s.glowna.dodano)}
        nowe={(s) => !obejrzane.has(s.glowna.id)}
        otwarteId={otwarteId}
        otworz={(s) => otworz(s.glowna.id, sprawy)}
      />
    </>
  )
}
