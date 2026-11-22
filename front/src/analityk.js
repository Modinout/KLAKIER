const KLUCZ = 'analityk'

function czytaj() {
  try {
    return localStorage.getItem(KLUCZ) ?? ''
  } catch {
    return ''
  }
}

// Kept in memory too, so the name still signs changes when the browser blocks storage.
let nazwa = czytaj()

export function analityk() {
  return nazwa
}

export function ustawAnalityka(nowa) {
  nazwa = nowa
  try {
    if (nowa) localStorage.setItem(KLUCZ, nowa)
    else localStorage.removeItem(KLUCZ)
  } catch {
    // The name lasts until the page reloads.
  }
}
