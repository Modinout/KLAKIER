async function wyslij(url, opcje) {
  const odpowiedz = await fetch(url, opcje)
  if (!odpowiedz.ok) {
    throw new Error('Błąd ' + odpowiedz.status + ' przy ' + url)
  }
  return odpowiedz.json()
}

export function pobierzReklamy(filtry) {
  const parametry = new URLSearchParams()
  if (filtry.werdykt) parametry.set('werdykt', filtry.werdykt)
  if (filtry.status) parametry.set('status', filtry.status)
  parametry.set('min_ryzyko', filtry.prog)
  return wyslij('/api/reklamy?' + parametry)
}

export function zmienStatus(id, status) {
  return wyslij('/api/reklamy/' + id, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  })
}

export function pobierzProgi() {
  return wyslij('/api/progi')
}
