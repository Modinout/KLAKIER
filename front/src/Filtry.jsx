function liczba(n) {
  return n.toLocaleString('pl-PL')
}

function opisProgu(progi, prog) {
  const wiersz = progi.progi.find((p) => Math.abs(p.prog - prog) < 0.001)
  if (!wiersz) return ''
  return (
    'łapie ' + liczba(wiersz.zlapane) + ' z ' + liczba(progi.oszustw) + ' oszustw, ' +
    liczba(wiersz.falszywe_alarmy) + ' fałszywych alarmów na ' + liczba(progi.uczciwych)
  )
}

export default function Filtry({ filtry, zmien, progi }) {
  function ustaw(pole, wartosc) {
    zmien({ ...filtry, [pole]: wartosc })
  }

  return (
    <div className="filtry">
      <label>
        Werdykt
        <select value={filtry.werdykt} onChange={(e) => ustaw('werdykt', e.target.value)}>
          <option value="">Wszystkie</option>
          <option value="oszustwo">Oszustwo</option>
          <option value="do_sprawdzenia">Do sprawdzenia</option>
          <option value="ok">OK</option>
        </select>
      </label>
      <label>
        Status
        <select value={filtry.status} onChange={(e) => ustaw('status', e.target.value)}>
          <option value="">Wszystkie</option>
          <option value="nowa">Nowa</option>
          <option value="w_toku">W toku</option>
          <option value="zamknieta">Zamknięta</option>
        </select>
      </label>
      <label>
        Próg ryzyka {filtry.prog.toLocaleString('pl-PL')}
        <input
          type="range"
          min="0.1"
          max="0.9"
          step="0.1"
          value={filtry.prog}
          onChange={(e) => ustaw('prog', Number(e.target.value))}
        />
      </label>
      {progi && <span>{opisProgu(progi, filtry.prog)}</span>}
    </div>
  )
}
