import { bezTekstu, NAZWY_WERDYKTOW } from '../nazwy.js'
import { notatki, ocenaModelu, ustalenia } from '../ustalenia.js'

function Punkt({ tytul, szary, children }) {
  return (
    <li className="grid grid-cols-[8px_1fr] gap-2.5 py-2">
      <span className={'mt-1.5 size-2 rounded-full ' + (szary ? 'bg-border' : 'bg-foreground/70')} />
      <div>
        {tytul && <p className={szary ? 'text-muted-foreground' : 'font-medium'}>{tytul}</p>}
        {children}
      </div>
    </li>
  )
}

function Podpis({ children }) {
  return <p className="text-[13px] text-muted-foreground">{children}</p>
}

// The level sentence above the list already says it; the model line differs from it only in case and the final dot.
function powtarzaPowod(tytul, powod) {
  const bezKropki = (tekst) => tekst.replace(/\.$/, '').toLowerCase()
  return Boolean(powod) && bezKropki(tytul) === bezKropki(powod)
}

export default function ListaUstalen({ reklama }) {
  const lista = ustalenia(reklama)
  const model = ocenaModelu(reklama)
  const drugi = reklama.drugi_sedzia
  const modelPowtarza = model && powtarzaPowod(model, reklama.powod)

  return (
    <ul className="mt-4">
      {lista.map((s) => {
        const powtarza = powtarzaPowod(s.opis, reklama.powod)
        if (powtarza && !s.podstawa) return null
        return (
          <Punkt key={s.modul + s.kod} tytul={powtarza ? null : s.opis}>
            {s.podstawa && <Podpis>{s.podstawa}</Podpis>}
          </Punkt>
        )
      })}
      {model && (!modelPowtarza || drugi) && (
        <Punkt tytul={modelPowtarza ? null : model}>
          {drugi && (
            <Podpis>
              Drugi model: {NAZWY_WERDYKTOW[drugi.werdykt]}. {drugi.uzasadnienie}
            </Podpis>
          )}
        </Punkt>
      )}
      {!model && lista.length === 0 && !bezTekstu(reklama) && <Punkt szary tytul="Brak ustaleń" />}
      {bezTekstu(reklama) && <Punkt szary tytul="Reklama graficzna: tekst nie został jeszcze odczytany" />}
      {notatki(reklama).map((s) => <Punkt key={s.kod} szary tytul={s.opis} />)}
    </ul>
  )
}
