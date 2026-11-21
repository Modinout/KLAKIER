import { NAZWY_STATUSOW, NAZWY_WERDYKTOW } from './nazwy.js'

export default function Lista({ reklamy, wybraneId, wybierz }) {
  return (
    <table>
      <thead>
        <tr>
          <th>Ryzyko</th>
          <th>Werdykt</th>
          <th>Reklamodawca</th>
          <th>Platforma</th>
          <th>Treść</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {reklamy.length === 0 && (
          <tr>
            <td colSpan="6">Brak reklam dla tych filtrów</td>
          </tr>
        )}
        {reklamy.map((r) => (
          <tr
            key={r.id}
            className={r.id === wybraneId ? 'wybrany' : ''}
            onClick={() => wybierz(r.id)}
          >
            <td>{Math.round(r.ryzyko * 100)}%</td>
            <td className={r.werdykt}>{NAZWY_WERDYKTOW[r.werdykt]}</td>
            <td>{r.reklamodawca}</td>
            <td>{r.platforma}</td>
            <td>{r.tekst.slice(0, 120)}</td>
            <td>{NAZWY_STATUSOW[r.status]}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
