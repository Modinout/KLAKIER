import { analityk } from './analityk.js'

async function wyslij(url, opcje) {
  const odpowiedz = await fetch(url, opcje)
  if (!odpowiedz.ok) {
    const blad = new Error('Nie udało się połączyć z serwerem.')
    blad.status = odpowiedz.status
    throw blad
  }
  return odpowiedz.json()
}

function json(metoda, dane) {
  return {
    method: metoda,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dane),
  }
}

// A header carries only Latin-1, so a name with Polish letters goes encoded.
function podpis() {
  const nazwa = analityk()
  return nazwa ? { 'X-Analityk': encodeURIComponent(nazwa) } : {}
}

function zmienReklame(id, dane) {
  const opcje = json('PATCH', dane)
  return wyslij('/api/reklamy/' + id, { ...opcje, headers: { ...opcje.headers, ...podpis() } })
}

export function pobierzReklamy(od) {
  return wyslij('/api/reklamy' + (od ? '?od=' + encodeURIComponent(od) : ''))
}

export function pobierzReklame(id) {
  return wyslij('/api/reklamy/' + id)
}

export function dodajReklame(reklama) {
  return wyslij('/api/reklamy', json('POST', reklama))
}

export function adresObrazu(id) {
  return '/api/reklamy/' + id + '/obraz'
}

export function zapiszObraz(id, obraz) {
  return wyslij('/api/reklamy/' + id + '/obraz', json('PUT', { obraz }))
}

export function odczytajObraz(obraz) {
  return wyslij('/api/odczytaj', json('POST', { obraz }))
}

export function zmienStatus(id, status) {
  return zmienReklame(id, { status })
}

// Takes [id, status] pairs, so an undo can give each ad its own earlier status.
export function zmienStatusy(pary) {
  return Promise.all(pary.map(([id, status]) => zmienStatus(id, status)))
}

export function zmienWerdyktAnalityka(id, werdykt) {
  return zmienReklame(id, { werdykt_analityka: werdykt })
}

export function zmienNotatke(id, notatka) {
  return zmienReklame(id, { notatka })
}

export function pobierzHistorie(id) {
  return wyslij('/api/reklamy/' + id + '/historia')
}

export function pobierzPodobne(id) {
  return wyslij('/api/reklamy/' + id + '/podobne')
}

export function uczModel() {
  return wyslij('/api/ucz', { method: 'POST', headers: podpis() })
}

export function pobierzProgi() {
  return wyslij('/api/progi')
}
