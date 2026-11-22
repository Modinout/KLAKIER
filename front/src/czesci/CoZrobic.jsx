import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { rodzaj } from '../dzialanie.js'
import { malaLitera } from '../nazwy.js'
import { pismo } from '../pisma.js'
import { polecanaFirma } from '../rejestr.js'
import { modelZalecaSprawdzenie, zdaniePowodu } from '../ustalenia.js'

const WKLEJ = {
  platforma: 'Skopiowano. Wklej do formularza zgłoszenia reklamy na platformie i do zgłoszenia w CERT Polska (incydent.cert.pl).',
  firma: 'Skopiowano. Wklej do wiadomości do firmy.',
  broker: 'Skopiowano. Wklej do wiadomości do firmy.',
}

function zdanie(r, glowna) {
  if (r === 'platforma') {
    return 'Firma nie ma zezwolenia KNF albo strona jest na liście ostrzeżeń. Poproś platformę o usunięcie reklam i zgłoś stronę do CERT Polska.'
  }
  if (r === 'firma') return 'Firma ma zezwolenie, ale reklama łamie zasady dla reklam usług inwestycyjnych. Napisz do firmy, żeby ją poprawiła.'
  if (r === 'broker') {
    const nazwa = polecanaFirma(glowna).nazwa
    return 'Influencer poleca ' + nazwa + ' linkiem bez oznaczenia, że to reklama. Napisz do ' + nazwa + '.'
  }
  if (r === 'sprawdz') {
    const powod = zdaniePowodu(glowna)
    return powod ? 'Sprawdź reklamę ręcznie: ' + malaLitera(powod.replace(/\.$/, '')) + '.' : 'Sprawdź reklamę ręcznie.'
  }
  return modelZalecaSprawdzenie(glowna) ? 'Przeczytaj tekst reklamy: model KAPSEL zaleca sprawdzenie.' : 'Nic do zrobienia: nie znaleziono naruszeń.'
}

function napisPrzycisku(r, glowna) {
  if (r === 'platforma') return 'Przygotuj zgłoszenie'
  if (r === 'firma') return 'Przygotuj pismo do firmy'
  return 'Przygotuj pismo do ' + polecanaFirma(glowna).nazwa
}

// Pierwsza z reklam to główna reklama sprawy.
export default function CoZrobic({ reklamy, status, ustawStatus }) {
  const glowna = reklamy[0]
  const r = rodzaj(glowna)
  const pismem = r in WKLEJ

  function przygotuj() {
    navigator.clipboard
      .writeText(pismo(r, reklamy))
      .then(() => (status === 'nowa' ? ustawStatus('w_toku', WKLEJ[r]) : toast(WKLEJ[r])))
      .catch(() => toast.error('Nie udało się skopiować'))
  }

  return (
    <div className="mb-4 rounded-lg border p-4">
      <p className="font-semibold">Co zrobić</p>
      <p className="mt-1">{zdanie(r, glowna)}</p>
      <div className="mt-3 flex flex-wrap gap-2 empty:hidden">
        {pismem && <Button onClick={przygotuj}>{napisPrzycisku(r, glowna)}</Button>}
        {pismem && status === 'w_toku' && (
          <Button variant="outline" onClick={() => ustawStatus('zamknieta')}>
            Gotowe, następna sprawa
          </Button>
        )}
        {r === 'sprawdz' && status === 'nowa' && <Button onClick={() => ustawStatus('w_toku')}>Biorę do wyjaśnienia</Button>}
        {r === 'nic' && status !== 'zamknieta' && <Button onClick={() => ustawStatus('zamknieta')}>Zamknij sprawę</Button>}
      </div>
    </div>
  )
}
