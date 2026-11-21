import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter, DialogTitle, DialogTrigger } from '@/components/ui/dialog'

export default function Potwierdzenie({ pytanie, przycisk, potwierdz, children }) {
  const [otwarte, setOtwarte] = useState(false)

  return (
    <Dialog open={otwarte} onOpenChange={setOtwarte}>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="p-6 sm:max-w-sm" aria-describedby={undefined}>
        <DialogTitle className="text-base font-semibold">{pytanie}</DialogTitle>
        <DialogFooter className="-mx-6 -mb-6 px-6">
          <Button variant="outline" onClick={() => setOtwarte(false)}>
            Anuluj
          </Button>
          <Button
            onClick={() => {
              setOtwarte(false)
              potwierdz()
            }}
          >
            {przycisk}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
