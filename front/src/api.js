async function wyslij(url, opcje) {
  const odpowiedz = await fetch(url, opcje)
  if (!odpowiedz.ok) {
    const blad = new Error('Nie udało się połączyć z serwerem.')
    blad.status = odpowiedz.status
    blad.tresc = await odpowiedz.json().catch(() => null)
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

function zmienReklame(id, dane) {
  return wyslij('/api/reklamy/' + id, json('PATCH', dane))
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

export function dodajNagranie(id, nagranie) {
  return wyslij('/api/reklamy/' + id + '/nagranie', json('PUT', { nagranie }))
}

export function odczytajObraz(obraz) {
  return wyslij('/api/odczytaj', json('POST', { obraz }))
}

export function zmienStatus(id, status) {
  return zmienReklame(id, { status })
}

// Przyjmuje pary [id, status], żeby cofnięcie mogło przywrócić każdej reklamie jej poprzedni status.
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

export function pobierzPowiazane(id) {
  return wyslij('/api/reklamy/' + id + '/powiazane')
}

export function pobierzDowody(id) {
  return wyslij('/api/reklamy/' + id + '/dowody')
}

export function adresPaczki(id) {
  return '/api/reklamy/' + id + '/paczka'
}

export function adresDowodu(id, rodzaj) {
  return '/api/dowody/' + id + '/' + rodzaj
}

export function zlecSprawdzenie(url) {
  return wyslij('/api/sprawdz', json('POST', { url }))
}

export function pobierzSprawdzenie(id) {
  return wyslij('/api/sprawdz/' + id)
}

export function zlecWyszukiwanie() {
  return wyslij('/api/patrol', json('POST', {}))
}

export function pobierzWyszukiwanie(id) {
  return wyslij('/api/patrol/' + id)
}

export function ostatnieWyszukiwanie() {
  return wyslij('/api/patrol')
}

export function pobierzProg() {
  return wyslij('/api/prog')
}

export function zapiszProg(prog) {
  return wyslij('/api/prog', json('PUT', { prog }))
}

export function uczModel() {
  return wyslij('/api/ucz', { method: 'POST' })
}

export function pobierzProgi() {
  return wyslij('/api/progi')
}
