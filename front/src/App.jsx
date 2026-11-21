import { useEffect, useState } from 'react'
import { pobierzProgi, pobierzReklamy, zmienStatus } from './api.js'
import Filtry from './Filtry.jsx'
import Karta from './Karta.jsx'
import Lista from './Lista.jsx'

export default function App() {
  const [filtry, setFiltry] = useState({ werdykt: '', status: '', prog: 0.3 })
  const [reklamy, setReklamy] = useState([])
  const [wybraneId, setWybraneId] = useState(null)
  const [progi, setProgi] = useState(null)
  const [blad, setBlad] = useState('')

  useEffect(() => {
    pobierzProgi().then(setProgi).catch((e) => setBlad(e.message))
  }, [])

  useEffect(() => {
    pobierzReklamy(filtry)
      .then((lista) => {
        setReklamy(lista)
        setBlad('')
      })
      .catch((e) => setBlad(e.message))
  }, [filtry])

  function ustawStatus(id, status) {
    zmienStatus(id, status)
      .then((nowa) => {
        setReklamy(reklamy.map((r) => (r.id === id ? nowa : r)))
        setBlad('')
      })
      .catch((e) => setBlad(e.message))
  }

  const wybrana = reklamy.find((r) => r.id === wybraneId)

  return (
    <>
      <header>
        <h1>KLAKIER</h1>
      </header>
      <Filtry filtry={filtry} zmien={setFiltry} progi={progi} />
      {blad && <p className="blad">{blad}</p>}
      <main>
        <Lista reklamy={reklamy} wybraneId={wybraneId} wybierz={setWybraneId} />
        {wybrana && <Karta reklama={wybrana} ustawStatus={ustawStatus} />}
      </main>
    </>
  )
}
