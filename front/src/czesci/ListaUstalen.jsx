import { bezTekstu, NAZWY_WERDYKTOW } from '../nazwy.js'
import { notatkiCert, ocenaModelu, ustalenia } from '../ustalenia.js'
import Ocena from './Ocena.jsx'

function Punkt({ tytul, szary, children }) {
  return (
    <li className="grid grid-cols-[8px_1fr] gap-2.5 py-2">
      <span className={'mt-1.5 size-2 rounded-full ' + (szary ? 'bg-border' : 'bg-foreground/70')} />
      <div>
        <p className={szary ? 'text-muted-foreground' : 'font-medium'}>{tytul}</p>
        {children}
      </div>
    </li>
  )
}

function Podpis({ children }) {
  return <p className="text-[13px] text-muted-foreground">{children}</p>
}

export default function ListaUstalen({ reklama, podmien }) {
  const lista = ustalenia(reklama)
  const model = ocenaModelu(reklama)
  const drugi = reklama.drugi_sedzia

  return (
    <ul className="mt-4">
      {lista.map((s) => (
        <Punkt key={s.modul + s.kod} tytul={s.opis}>
          {s.podstawa && <Podpis>{s.podstawa}</Podpis>}
        </Punkt>
      ))}
      {model && (
        <Punkt tytul={model}>
          {reklama.rodzaj && <Podpis>Rodzaj: {reklama.rodzaj}</Podpis>}
          {drugi && (
            <Podpis>
              Drugi model: {NAZWY_WERDYKTOW[drugi.werdykt]}. {drugi.uzasadnienie}
            </Podpis>
          )}
        </Punkt>
      )}
      {!model && lista.length === 0 && !bezTekstu(reklama) && <Punkt szary tytul="Brak ustaleń" />}
      {bezTekstu(reklama) ? (
        <Punkt szary tytul="Reklama graficzna: tekst nie został jeszcze odczytany" />
      ) : (
        <li>
          <Ocena reklama={reklama} podmien={podmien} />
        </li>
      )}
      {notatkiCert(reklama).map((s) => (
        <Punkt key={s.kod} szary tytul={s.opis}>
          {s.kod === 'brak_na_liscie_cert' && <Podpis>Do przekazania CERT Polska</Podpis>}
        </Punkt>
      ))}
    </ul>
  )
}
