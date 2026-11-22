import { useEffect, useState } from 'react'
import { Plus } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { dodajReklame, odczytajObraz, zapiszObraz, zlecSprawdzenie } from '../api.js'
import { BLAD_ZAPISU, OPISY, PLATFORMY } from '../nazwy.js'
import { BLAD_SPRAWDZANIA, czekajNaSprawdzenie } from '../sprawdzanieLinku.js'

const PUSTE = { reklamodawca: '', url: '', tekst: '', platforma: 'google', obraz: null }

function bladOdczytu(blad) {
  if (blad.status === 422) return 'To nie jest obraz.'
  if (blad.status === 503 || blad.status === 404) return 'Odczyt obrazu jest teraz niedostępny.'
  return 'Nie udało się odczytać obrazu. Spróbuj ponownie.'
}

function bladSprawdzenia(blad) {
  // Komunikaty walidacji z api zaczynają się angielskim przedrostkiem walidatora.
  if (blad.status === 422) return blad.tresc?.detail?.[0]?.msg?.replace(/^Value error, /, '') ?? 'Podaj poprawny adres strony.'
  if (blad.status === 503) return blad.tresc?.detail ?? 'Sprawdzanie stron jest teraz niedostępne.'
  return BLAD_SPRAWDZANIA
}

export default function DodajReklame({ poDodaniu, poSprawdzeniu }) {
  const [otwarte, setOtwarte] = useState(false)
  const [pola, setPola] = useState(PUSTE)
  const [czyta, setCzyta] = useState(false)
  const [wysyla, setWysyla] = useState(false)
  // Sekundy od zlecenia sprawdzenia linku; null, gdy nic się nie sprawdza.
  const [sekundy, setSekundy] = useState(null)
  const [bladLinku, setBladLinku] = useState('')

  function ustaw(pole, wartosc) {
    setPola((p) => ({ ...p, [pole]: wartosc }))
  }

  function otworz(czy) {
    setOtwarte(czy)
    if (czy) return
    setPola(PUSTE)
    setBladLinku('')
  }

  useEffect(() => {
    if (sekundy === null) return
    const zegar = setTimeout(() => setSekundy((s) => (s === null ? null : s + 1)), 1000)
    return () => clearTimeout(zegar)
  }, [sekundy])

  async function sprawdzLink() {
    setBladLinku('')
    setSekundy(0)
    try {
      const { id } = await zlecSprawdzenie(pola.url)
      const wynik = await czekajNaSprawdzenie(id)
      if (wynik.blad) return setBladLinku(wynik.blad)
      otworz(false)
      poSprawdzeniu(wynik.reklamaId)
    } catch (e) {
      setBladLinku(bladSprawdzenia(e))
    } finally {
      setSekundy(null)
    }
  }

  function wczytajObraz(plik) {
    if (!plik) return
    const czytnik = new FileReader()
    czytnik.onload = () => {
      const obraz = czytnik.result.split(',')[1]
      ustaw('obraz', obraz)
      setCzyta(true)
      odczytajObraz(obraz)
        .then((w) => ustaw('tekst', w.tekst))
        .catch((e) => toast.error(bladOdczytu(e)))
        .finally(() => setCzyta(false))
    }
    czytnik.readAsDataURL(plik)
  }

  function upusc(zdarzenie) {
    zdarzenie.preventDefault()
    wczytajObraz(zdarzenie.dataTransfer.files[0])
  }

  async function wyslij(zdarzenie) {
    zdarzenie.preventDefault()
    setWysyla(true)
    const teraz = new Date()
    try {
      let nowa = await dodajReklame({
        zrodlo: 'panel',
        id_zrodla: String(teraz.getTime()),
        platforma: pola.platforma,
        url: pola.url || null,
        reklamodawca: pola.reklamodawca || null,
        tekst: pola.tekst,
        zebrano: teraz.toISOString(),
      })
      if (pola.obraz) {
        nowa = await zapiszObraz(nowa.id, pola.obraz).catch(() => {
          toast.error('Reklamę dodano bez obrazu. Nie udało się go zapisać.')
          return nowa
        })
      }
      toast.success('Dodano reklamę')
      otworz(false)
      poDodaniu(nowa)
    } catch (e) {
      toast.error(e.status === 409 ? 'Taka reklama już jest.' : BLAD_ZAPISU)
    } finally {
      setWysyla(false)
    }
  }

  return (
    <Dialog open={otwarte} onOpenChange={otworz}>
      <DialogTrigger asChild>
        <Button className="h-[34px] px-3.5">
          <Plus />
          Dodaj reklamę
        </Button>
      </DialogTrigger>
      <DialogContent className="p-6 sm:max-w-lg" aria-describedby={undefined}>
        <DialogTitle className="text-lg font-semibold">Dodaj reklamę</DialogTitle>
        <p className="text-muted-foreground">{OPISY.dodaj}</p>
        <div className="grid gap-1.5">
          <Label htmlFor="link">Link do strony</Label>
          <div className="flex gap-2">
            <Input id="link" type="url" placeholder="https://" value={pola.url} onChange={(e) => ustaw('url', e.target.value)} />
            <Button type="button" variant="outline" disabled={!pola.url.trim() || sekundy !== null} onClick={sprawdzLink}>
              {sekundy === null ? 'Sprawdź link' : 'Sprawdzam stronę… ' + sekundy + ' s'}
            </Button>
          </div>
          {bladLinku && <p className="text-destructive">{bladLinku}</p>}
        </div>
        <form className="grid gap-4" onSubmit={wyslij}>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor="reklamodawca">Reklamodawca</Label>
              <Input id="reklamodawca" value={pola.reklamodawca} onChange={(e) => ustaw('reklamodawca', e.target.value)} />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="platforma">Platforma</Label>
              <Select value={pola.platforma} onValueChange={(v) => ustaw('platforma', v)}>
                <SelectTrigger id="platforma" className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(PLATFORMY).map(([wartosc, nazwa]) => (
                    <SelectItem key={wartosc} value={wartosc}>
                      {nazwa}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <label
            className="flex h-20 cursor-pointer items-center justify-center rounded-lg border border-dashed text-muted-foreground hover:bg-muted/50"
            onDragOver={(e) => e.preventDefault()}
            onDrop={upusc}
          >
            {czyta ? 'Odczytuję tekst z obrazu…' : pola.obraz ? 'Zrzut ekranu dodany. Upuść inny, aby go zmienić' : 'Upuść zrzut ekranu albo kliknij'}
            <input type="file" accept="image/png,image/jpeg" className="hidden" onChange={(e) => wczytajObraz(e.target.files[0])} />
          </label>
          <div className="grid gap-1.5">
            <Label htmlFor="tresc">Treść</Label>
            <Textarea id="tresc" className="min-h-28" value={pola.tekst} onChange={(e) => ustaw('tekst', e.target.value)} required />
          </div>
          <DialogFooter className="-mx-6 -mb-6 px-6">
            <Button type="button" variant="outline" onClick={() => otworz(false)}>
              Anuluj
            </Button>
            <Button type="submit" disabled={wysyla || czyta}>
              Dodaj
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
