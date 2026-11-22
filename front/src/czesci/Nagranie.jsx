import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { dodajNagranie } from '../api.js'
import Sekcja from './Sekcja.jsx'

const NAJWIECEJ_MB = 50
// Dłuższa mowa nie mieści się w czterech liniach.
const DLUGA = 300
const TYPY = 'video/mp4,video/webm,audio/mpeg,audio/wav,audio/x-wav,audio/mp4,audio/x-m4a,audio/webm'

function bladNagrania(blad) {
  const szczegol = blad.tresc?.detail
  if (blad.status === 422) return (typeof szczegol === 'string' ? szczegol : szczegol?.[0]?.msg?.replace(/^Value error, /, '')) ?? 'To nie jest nagranie.'
  if (blad.status === 503) return 'Odczyt mowy jest teraz niedostępny.'
  return 'Nie udało się odczytać nagrania. Spróbuj ponownie.'
}

export default function Nagranie({ reklama, podmien }) {
  const [start, setStart] = useState(null)
  const [sekundy, setSekundy] = useState(0)
  const [caly, setCaly] = useState(false)

  useEffect(() => {
    if (!start) return
    const zegar = setInterval(() => setSekundy(Math.round((Date.now() - start) / 1000)), 1000)
    return () => clearInterval(zegar)
  }, [start])

  function wczytaj(plik) {
    if (!plik) return
    if (plik.size > NAJWIECEJ_MB * 1024 * 1024) return toast.error('Nagranie jest większe niż ' + NAJWIECEJ_MB + ' MB.')
    const czytnik = new FileReader()
    czytnik.onload = () => {
      setSekundy(0)
      setStart(Date.now())
      dodajNagranie(reklama.id, czytnik.result.split(',')[1])
        .then((nowa) => {
          podmien(nowa)
          toast(nowa.mowa ? 'Dodano nagranie i odczytano mowę' : 'W nagraniu nie ma mowy')
        })
        .catch((e) => toast.error(bladNagrania(e)))
        .finally(() => setStart(null))
    }
    czytnik.readAsDataURL(plik)
  }

  return (
    <Sekcja tytul="Mowa w nagraniu">
      {reklama.mowa ? (
        <>
          <p className={'whitespace-pre-wrap break-words' + (caly ? '' : ' line-clamp-4')}>{reklama.mowa}</p>
          {reklama.mowa.length > DLUGA && (
            <button className="mt-1 text-[13px] font-medium" onClick={() => setCaly(!caly)}>
              {caly ? 'Zwiń' : 'Pokaż całość'}
            </button>
          )}
        </>
      ) : (
        <p className="text-muted-foreground">Brak nagrania.</p>
      )}
      <div className="mt-2">
        <Button asChild variant="outline" size="sm" disabled={Boolean(start)}>
          <label className={start ? 'pointer-events-none opacity-50' : 'cursor-pointer'}>
            {start ? 'Odczytuję mowę… ' + sekundy + ' s' : 'Dodaj nagranie'}
            <input
              type="file"
              accept={TYPY}
              className="hidden"
              onChange={(e) => {
                wczytaj(e.target.files[0])
                e.target.value = ''
              }}
            />
          </label>
        </Button>
      </div>
    </Sekcja>
  )
}
