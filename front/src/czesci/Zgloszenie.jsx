import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { nazwaPliku, zgloszenie } from '../zgloszenie.js'

export default function Zgloszenie({ reklamy, children }) {
  const tekst = zgloszenie(reklamy)

  function kopiuj() {
    navigator.clipboard
      .writeText(tekst)
      .then(() => toast('Skopiowano zgłoszenie'))
      .catch(() => toast.error('Nie udało się skopiować'))
  }

  function pobierz() {
    const adres = URL.createObjectURL(new Blob([tekst], { type: 'text/plain;charset=utf-8' }))
    const link = document.createElement('a')
    link.href = adres
    link.download = nazwaPliku(reklamy)
    link.click()
    URL.revokeObjectURL(adres)
  }

  return (
    <Dialog>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="p-6 sm:max-w-2xl" aria-describedby={undefined}>
        <DialogTitle className="text-base font-semibold">Zgłoszenie sprawy</DialogTitle>
        <pre className="max-h-[60vh] overflow-auto rounded-lg border bg-muted/30 p-4 font-sans text-sm whitespace-pre-wrap">{tekst}</pre>
        <DialogFooter className="-mx-6 -mb-6 px-6">
          <Button variant="outline" onClick={pobierz}>
            Pobierz plik
          </Button>
          <Button onClick={kopiuj}>Kopiuj</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
