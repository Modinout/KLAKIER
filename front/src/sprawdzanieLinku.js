import { toast } from 'sonner'
import { pobierzSprawdzenie } from './api.js'

export const BLAD_SPRAWDZANIA = 'Nie udało się sprawdzić strony. Spróbuj ponownie.'
const CO_ILE_MS = 2000
const NAJDLUZEJ_MS = 3 * 60 * 1000
// A check that stays in progress this long has lost its worker.
const BEZ_ZMIANY_MS = 2 * 60 * 1000

function czekaj(ms) {
  return new Promise((koniec) => setTimeout(koniec, ms))
}

function blad(id, tekst) {
  toast.error(tekst, { id, duration: 10000 })
}

// Polls one link check in a toast, so it goes on after the add-ad dialog closes.
export async function sledzSprawdzenie(id, host, gotowe) {
  const start = Date.now()
  const pokaz = () => toast.loading('Sprawdzam link: ' + host + ' · ' + Math.round((Date.now() - start) / 1000) + ' s', { id })
  pokaz()
  let stan = 'w_kolejce'
  let odZmiany = start
  try {
    while (Date.now() - start < NAJDLUZEJ_MS) {
      await czekaj(CO_ILE_MS)
      const wynik = await pobierzSprawdzenie(id)
      if (wynik.stan === 'gotowe') return gotowe(wynik.reklama_id)
      if (wynik.stan === 'blad') return blad(id, wynik.blad)
      if (wynik.stan !== stan) {
        stan = wynik.stan
        odZmiany = Date.now()
      } else if (stan === 'w_toku' && Date.now() - odZmiany >= BEZ_ZMIANY_MS) {
        return blad(id, 'Sprawdzanie nie powiodło się. Spróbuj ponownie.')
      }
      pokaz()
    }
    blad(id, 'Sprawdzanie trwa zbyt długo. Spróbuj ponownie.')
  } catch {
    blad(id, BLAD_SPRAWDZANIA)
  }
}
