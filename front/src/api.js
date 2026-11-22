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
  return wyslij('/api/reklamy/' + id, json('PATCH', { status }))
}

// Takes [id, status] pairs, so an undo can give each ad its own earlier status.
export function zmienStatusy(pary) {
  return Promise.all(pary.map(([id, status]) => zmienStatus(id, status)))
}

export function zmienWerdyktAnalityka(id, werdykt) {
  return wyslij('/api/reklamy/' + id, json('PATCH', { werdykt_analityka: werdykt }))
}

export function pobierzPodobne(id) {
  return wyslij('/api/reklamy/' + id + '/podobne')
}

export function uczModel() {
  return wyslij('/api/ucz', { method: 'POST' })
}

export function pobierzProgi() {
  return wyslij('/api/progi')
}
