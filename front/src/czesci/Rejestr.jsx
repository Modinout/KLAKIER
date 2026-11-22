import { domena, domenaDocelowa, pierwszaDomena } from '../nazwy.js'
import { kto, nazwaRejestru, STANY_REJESTRU, stanRejestru, wpisRejestru } from '../rejestr.js'
import { tytul } from '../sprawy.js'

const KOLORY = {
  w_rejestrze: 'bg-muted text-muted-foreground',
  spoza_rejestru: 'bg-amber-100 text-amber-800',
  poza_listami: 'bg-destructive/10 text-destructive',
  bank: 'bg-muted text-muted-foreground',
  mica: 'bg-muted text-muted-foreground',
}

function Wiersz({ nazwa, children }) {
  return (
    <div className="grid grid-cols-[130px_1fr_auto] items-center gap-3 px-3.5 py-2.5">
      <span className="text-muted-foreground">{nazwa}</span>
      {children}
    </div>
  )
}

export default function Rejestr({ reklama }) {
  const rejestr = reklama.rejestr
  const chip = stanRejestru(reklama)
  const cel = domenaDocelowa(reklama)
  // Tytuł od pierwszej domeny w tekście: bez linku, bo nie była sprawdzana jako cel.
  const zTekstu = !cel && !reklama.reklamodawca && tytul(reklama) === pierwszaDomena(reklama.tekst) ? tytul(reklama) : null
  if (!reklama.reklamodawca && !cel && !zTekstu) return null

  return (
    <div className="mb-4 divide-y rounded-lg border">
      {reklama.reklamodawca && (
        <Wiersz nazwa={kto(reklama)}>
          <span className="font-medium">{reklama.reklamodawca}</span>
          {chip && <span className={'rounded-md px-2 py-0.5 text-xs font-medium ' + KOLORY[chip]}>{STANY_REJESTRU[chip]}</span>}
        </Wiersz>
      )}
      {cel && (
        <Wiersz nazwa="Prowadzi do">
          <a
            href={reklama.url && domena(reklama.url) === cel ? reklama.url : 'https://' + cel}
            target="_blank"
            rel="noreferrer"
            className="truncate underline underline-offset-4"
          >
            {cel}
          </a>
        </Wiersz>
      )}
      {zTekstu && (
        <Wiersz nazwa="Prowadzi do">
          <span className="truncate">{zTekstu}</span>
        </Wiersz>
      )}
      {rejestr?.podmiot && (
        <Wiersz nazwa={nazwaRejestru(rejestr)}>
          <span className="font-medium">
            {rejestr.podmiot}
            <small className="block text-[13px] font-normal text-muted-foreground">
              {wpisRejestru(rejestr).join(' · ')}
            </small>
          </span>
        </Wiersz>
      )}
    </div>
  )
}
