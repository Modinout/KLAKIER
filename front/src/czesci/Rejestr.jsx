import { domena, domenaDocelowa, pierwszaDomena } from '../nazwy.js'
import { kto, nazwaRejestru, polecanaFirma, STANY_REJESTRU, stanRejestru, wpisRejestru } from '../rejestr.js'
import { tytul } from '../sprawy.js'

const KOLORY = {
  w_rejestrze: 'bg-muted text-muted-foreground',
  spoza_rejestru: 'bg-amber-100 text-amber-800',
  poza_listami: 'bg-destructive/10 text-destructive',
  bank: 'bg-muted text-muted-foreground',
  mica: 'bg-muted text-muted-foreground',
  tfi: 'bg-muted text-muted-foreground',
}

function Chip({ stan }) {
  return stan && <span className={'whitespace-nowrap rounded-md px-2 py-0.5 text-xs font-medium ' + KOLORY[stan]}>{STANY_REJESTRU[stan]}</span>
}

function Wiersz({ nazwa, children }) {
  return (
    <div className="col-span-full grid grid-cols-subgrid items-baseline px-3.5 py-2.5">
      <span className="whitespace-nowrap text-muted-foreground">{nazwa}</span>
      <div className="flex min-w-0 flex-col items-start gap-1">{children}</div>
    </div>
  )
}

export default function Rejestr({ reklama }) {
  const rejestr = reklama.rejestr
  const chip = stanRejestru(reklama)
  const cel = domenaDocelowa(reklama)
  // Tytuł od pierwszej domeny w tekście: bez linku, bo nie była sprawdzana jako cel.
  const zTekstu = !cel && !reklama.reklamodawca && tytul(reklama) === pierwszaDomena(reklama.tekst) ? tytul(reklama) : null
  const polecona = polecanaFirma(reklama)
  if (!reklama.reklamodawca && !cel && !zTekstu && !polecona) return null

  // Wiersze dzielą kolumny, więc kolumna nazw ma szerokość najdłuższej nazwy.
  return (
    <div className="mb-4 grid grid-cols-[minmax(100px,auto)_minmax(0,1fr)] gap-x-3 divide-y rounded-lg border">
      {reklama.reklamodawca && (
        <Wiersz nazwa={kto(reklama)}>
          <span className="font-medium break-words">{reklama.reklamodawca}</span>
          <Chip stan={chip} />
        </Wiersz>
      )}
      {polecona && (
        <Wiersz nazwa="Polecana firma">
          <span className="font-medium">{polecona.nazwa}</span>
          <Chip stan={polecona.stan_rejestru} />
        </Wiersz>
      )}
      {cel && (
        <Wiersz nazwa="Prowadzi do">
          <a
            href={reklama.url && domena(reklama.url) === cel ? reklama.url : 'https://' + cel}
            target="_blank"
            rel="noreferrer"
            className="max-w-full truncate underline underline-offset-4"
          >
            {cel}
          </a>
        </Wiersz>
      )}
      {zTekstu && (
        <Wiersz nazwa="Prowadzi do">
          <span className="max-w-full truncate">{zTekstu}</span>
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
