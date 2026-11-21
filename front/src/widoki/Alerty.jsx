import TabelaSpraw from '../czesci/TabelaSpraw.jsx'
import { data, ileSpraw } from '../nazwy.js'

function dodano(sprawa) {
  return sprawa.reklamy.reduce((najnowsze, r) => (r.dodano > najnowsze ? r.dodano : najnowsze), '')
}

export default function Alerty({ sprawy, nowe, otwarteId, otworz }) {
  const odNajnowszych = [...sprawy].sort((a, b) => dodano(b).localeCompare(dodano(a)))

  return (
    <>
      <h1 className="mb-5 text-2xl font-bold tracking-tight">Alerty</h1>
      <TabelaSpraw
        sprawy={odNajnowszych}
        ile={ileSpraw(odNajnowszych.length)}
        kiedy={(s) => data(dodano(s))}
        nowe={nowe}
        otwarteId={otwarteId}
        otworz={(s) => otworz(s.glowna.id, odNajnowszych)}
      />
    </>
  )
}
