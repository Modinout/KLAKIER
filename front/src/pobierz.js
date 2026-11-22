export function pobierzPlik(tekst, typ, nazwa) {
  const adres = URL.createObjectURL(new Blob([tekst], { type: typ }))
  const link = document.createElement('a')
  link.href = adres
  link.download = nazwa
  link.click()
  URL.revokeObjectURL(adres)
}
