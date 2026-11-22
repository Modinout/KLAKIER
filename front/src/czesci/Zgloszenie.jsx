import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { pobierzPlik } from '../pobierz.js'
import { nazwaPliku, zgloszenie } from '../zgloszenie.js'

export default function Zgloszenie({ reklamy, children }) {
  const tekst = zgloszenie(reklamy)

  function kopiuj() {
    navigator.clipboard
      .writeText(tekst)
      .then(() => toast('Skopiowano zgłoszenie'))
      .catch(() => toast.error('Nie udało się skopiować'))
  }

  return (
    <Dialog>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="p-6 sm:max-w-2xl" aria-describedby={undefined}>
        <DialogTitle className="text-base font-semibold">Zgłoszenie sprawy</DialogTitle>
        <pre className="max-h-[60vh] overflow-auto rounded-lg border bg-muted/30 p-4 font-sans text-sm whitespace-pre-wrap">{tekst}</pre>
        <DialogFooter className="-mx-6 -mb-6 px-6">
          <Button variant="outline" onClick={() => pobierzPlik(tekst, 'text/plain;charset=utf-8', nazwaPliku(reklamy))}>
            Pobierz plik
          </Button>
          <Button onClick={kopiuj}>Kopiuj</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
