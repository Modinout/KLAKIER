import { NAZWY_STATUSOW, NAZWY_WERDYKTOW } from './nazwy.js'

export default function Karta({ reklama, ustawStatus }) {
  return (
    <aside>
      <h2>{reklama.reklamodawca}</h2>
      <p>{reklama.platforma}</p>
      {reklama.url && (
        <p>
          <a href={reklama.url} target="_blank" rel="noreferrer">
            {reklama.url}
          </a>
        </p>
      )}
      <p className="tekst">{reklama.tekst}</p>
      <p>
        Ryzyko {Math.round(reklama.ryzyko * 100)}%,{' '}
        <span className={reklama.werdykt}>{NAZWY_WERDYKTOW[reklama.werdykt]}</span>
      </p>
      {!reklama.pewny && <p>Model niepewny, do oceny przez człowieka</p>}
      {reklama.sygnaly.length > 0 && (
        <ul>
          {reklama.sygnaly.map((s) => (
            <li key={s.modul + s.kod}>
              {s.modul}: {s.opis}
              {s.podstawa && ' (' + s.podstawa + ')'}
            </li>
          ))}
        </ul>
      )}
      <div>
        {Object.entries(NAZWY_STATUSOW).map(([status, nazwa]) => (
          <button
            key={status}
            disabled={reklama.status === status}
            onClick={() => ustawStatus(reklama.id, status)}
          >
            {nazwa}
          </button>
        ))}
      </div>
    </aside>
  )
}
