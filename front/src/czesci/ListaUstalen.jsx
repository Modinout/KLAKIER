import { bezTekstu } from '../nazwy.js'
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

// Przy niskim ryzyku zdanie o poziomie nad listą już to mówi; wiersz modelu różni się od niego tylko wielkością liter i końcową kropką.
function powtarzaPowod(tytul, powod) {
  const bezKropki = (tekst) => tekst.replace(/\.$/, '').toLowerCase()
  return Boolean(powod) && bezKropki(tytul) === bezKropki(powod)
}

export default function ListaUstalen({ reklama }) {
  const lista = ustalenia(reklama)
  const model = ocenaModelu(reklama)
  const powod = reklama.poziom === 'niskie' ? reklama.powod : null
  const modelPowtarza = model && powtarzaPowod(model, powod)

  return (
    <ul className="mt-4">
      {lista.map((s) => {
        const powtarza = powtarzaPowod(s.opis, powod)
        if (powtarza && !s.podstawa) return null
        return (
          <Punkt key={s.modul + s.kod} tytul={powtarza ? null : s.opis}>
            {s.podstawa && <Podpis>{s.podstawa}</Podpis>}
          </Punkt>
        )
      })}
      {model && !modelPowtarza && <Punkt tytul={model} />}
      {!model && lista.length === 0 && !bezTekstu(reklama) && reklama.poziom !== 'niskie' && <Punkt szary tytul="Brak ustaleń" />}
      {bezTekstu(reklama) && <Punkt szary tytul="Reklama graficzna: tekst nie został jeszcze odczytany" />}
      {notatki(reklama).map((s) => <Punkt key={s.kod} szary tytul={s.opis} />)}
    </ul>
  )
}
