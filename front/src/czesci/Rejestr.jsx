import { domena, NAZWY_LIST_KNF } from '../nazwy.js'

const KTO = {
  youtube: 'Kanał',
  strony_doradcow: 'Właściciel strony',
  patrol_ostrzezen: 'Właściciel strony',
}

const STANY = {
  w_rejestrze: { tekst: 'na liście KNF', kolor: 'bg-muted text-muted-foreground' },
  spoza_rejestru: { tekst: 'inna spółka niż w rejestrze', kolor: 'bg-amber-100 text-amber-800' },
  poza_listami: { tekst: 'brak na listach KNF', kolor: 'bg-destructive/10 text-destructive' },
  bank: { tekst: 'bank, poza listami firm inwestycyjnych', kolor: 'bg-muted text-muted-foreground' },
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
  const stan = STANY[rejestr?.stan]
  if (!reklama.reklamodawca && !reklama.url) return null

  return (
    <div className="mb-4 divide-y rounded-lg border">
      {reklama.reklamodawca && (
        <Wiersz nazwa={KTO[reklama.zrodlo] ?? 'Zapłacił'}>
          <span className="font-medium">{reklama.reklamodawca}</span>
          {stan && <span className={'rounded-md px-2 py-0.5 text-xs font-medium ' + stan.kolor}>{stan.tekst}</span>}
        </Wiersz>
      )}
      {reklama.url && (
        <Wiersz nazwa="Prowadzi do">
          <a href={reklama.url} target="_blank" rel="noreferrer" className="truncate underline underline-offset-4">
            {domena(reklama.url)}
          </a>
        </Wiersz>
      )}
      {rejestr?.podmiot && (
        <Wiersz nazwa="W rejestrze KNF">
          <span className="font-medium">
            {rejestr.podmiot}
            <small className="block text-[13px] font-normal text-muted-foreground">
              {[rejestr.panstwo, NAZWY_LIST_KNF[rejestr.lista] ?? rejestr.lista].filter(Boolean).join(' · ')}
            </small>
          </span>
        </Wiersz>
      )}
    </div>
  )
}
