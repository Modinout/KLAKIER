import TabelaSpraw from '../czesci/TabelaSpraw.jsx'
import { data, ileSpraw } from '../nazwy.js'
import { odNajgorszych } from '../sprawy.js'

function dodano(sprawa) {
  return sprawa.reklamy.reduce((najnowsze, r) => (r.dodano > najnowsze ? r.dodano : najnowsze), '')
}

const NA_STRONIE = 12

export default function Alerty({ sprawy, przybyla, nowe, otwarteId, otworz }) {
  const nowych = sprawy.filter(przybyla).sort((a, b) => dodano(b).localeCompare(dodano(a)))
  const wczesniejsze = sprawy.filter((s) => !przybyla(s)).sort(odNajgorszych)
  const wszystkie = [...nowych, ...wczesniejsze]

  function tabela(lista, pusto) {
    return (
      <TabelaSpraw
        sprawy={lista}
        ile={ileSpraw(lista.length)}
        kiedy={(s) => data(dodano(s))}
        nowe={nowe}
        otwarteId={otwarteId}
        otworz={(s) => otworz(s.glowna.id, wszystkie)}
        wierszy={NA_STRONIE}
        pusto={pusto}
      />
    )
  }

  return (
    <>
      <h1 className="mb-5 text-2xl font-bold tracking-tight">Alerty</h1>
      <h2 className="mb-2 text-lg font-semibold">Nowe</h2>
      {tabela(nowych, 'Brak nowych alertów od otwarcia panelu')}
      <h2 className="mt-8 mb-2 text-lg font-semibold">Wcześniejsze</h2>
      {tabela(wczesniejsze)}
    </>
  )
}
