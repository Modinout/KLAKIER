import { pobierzSprawdzenie } from './api.js'

export const BLAD_SPRAWDZANIA = 'Nie udało się sprawdzić strony. Spróbuj ponownie.'
const CO_ILE_MS = 2000
const NAJDLUZEJ_MS = 3 * 60 * 1000
// Sprawdzenie, które trwa tak długo, straciło swojego wykonawcę.
const BEZ_ZMIANY_MS = 2 * 60 * 1000

function czekaj(ms) {
  return new Promise((koniec) => setTimeout(koniec, ms))
}

// Zwraca { reklamaId } nowej reklamy albo { blad } z powodem do pokazania.
export async function czekajNaSprawdzenie(id) {
  const start = Date.now()
  let stan = 'w_kolejce'
  let odZmiany = start
  try {
    while (Date.now() - start < NAJDLUZEJ_MS) {
      await czekaj(CO_ILE_MS)
      const wynik = await pobierzSprawdzenie(id)
      if (wynik.stan === 'gotowe') return { reklamaId: wynik.reklama_id }
      if (wynik.stan === 'blad') return { blad: wynik.blad }
      if (wynik.stan !== stan) {
        stan = wynik.stan
        odZmiany = Date.now()
      } else if (stan === 'w_toku' && Date.now() - odZmiany >= BEZ_ZMIANY_MS) {
        return { blad: 'Sprawdzanie nie powiodło się. Spróbuj ponownie.' }
      }
    }
    return { blad: 'Sprawdzanie trwa zbyt długo. Spróbuj ponownie.' }
  } catch {
    return { blad: BLAD_SPRAWDZANIA }
  }
}
