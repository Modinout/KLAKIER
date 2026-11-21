import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { toast } from 'sonner'
import { Toaster } from '@/components/ui/sonner'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { pobierzReklamy } from './api.js'
import { poziomRyzyka } from './ryzyko.js'
import useAlerty from './useAlerty.js'
import DodajReklame from './czesci/DodajReklame.jsx'
import Szczegoly from './czesci/Szczegoly.jsx'
import Alerty from './widoki/Alerty.jsx'
import Analityka from './widoki/Analityka.jsx'
import Kalibracja from './widoki/Kalibracja.jsx'

// New ads arrive through the alert socket; this refresh catches the rest.
const CO_ILE_MS = 15000

const BLAD_LISTY = 'Brak połączenia z serwerem. Panel spróbuje ponownie.'

function bezTestowych(lista) {
  return lista.filter((r) => r.zrodlo !== 'test')
}

export default function App() {
  const [reklamy, setReklamy] = useState(null)
  const [prog, setProg] = useState(0.4)
  const [otwarte, setOtwarte] = useState(null)
  const [obejrzane, setObejrzane] = useState(new Set())
  const najnowszeDodano = useRef(null)

  function zapamietajNajnowsze(lista) {
    for (const r of lista) {
      if (!najnowszeDodano.current || r.dodano > najnowszeDodano.current) najnowszeDodano.current = r.dodano
    }
  }

  const dolacz = useCallback((nowe) => {
    zapamietajNajnowsze(nowe)
    setReklamy((lista) => {
      const poId = new Map((lista ?? []).map((r) => [r.id, r]))
      for (const r of bezTestowych(nowe)) poId.set(r.id, r)
      return [...poId.values()]
    })
  }, [])

  function odswiez() {
    pobierzReklamy()
      .then((lista) => {
        zapamietajNajnowsze(lista)
        setReklamy(bezTestowych(lista))
      })
      .catch(() => toast.error(BLAD_LISTY, { id: 'lista' }))
  }

  useEffect(() => {
    odswiez()
    const zegar = setInterval(() => {
      if (!najnowszeDodano.current) return odswiez()
      pobierzReklamy(najnowszeDodano.current)
        .then(dolacz)
        .catch(() => toast.error(BLAD_LISTY, { id: 'lista' }))
    }, CO_ILE_MS)
    return () => clearInterval(zegar)
  }, [dolacz])

  useAlerty(dolacz)

  const wiersze = useMemo(
    () => reklamy?.map((r) => ({ ...r, poziom: poziomRyzyka(r, prog) })),
    [reklamy, prog]
  )
  const alerty = useMemo(() => wiersze?.filter((r) => r.poziom === 'wysokie') ?? [], [wiersze])
  const nieobejrzane = alerty.filter((r) => !obejrzane.has(r.id)).length

  function podmien(nowa) {
    setReklamy((lista) => lista.map((r) => (r.id === nowa.id ? nowa : r)))
  }

  function otworz(id, sprawy) {
    setOtwarte({ id, sprawy })
    setObejrzane((zbior) => new Set(zbior).add(id))
  }

  const otwarta = otwarte && wiersze?.find((r) => r.id === otwarte.id)

  return (
    <Tabs defaultValue="analityka" className="h-svh gap-0">
      <header className="flex h-15 shrink-0 items-center gap-6 border-b px-8">
        <span className="font-bold tracking-[.08em]">KLAKIER</span>
        <TabsList className="h-9">
          <TabsTrigger value="analityka" className="px-3">Interfejs analityczny</TabsTrigger>
          <TabsTrigger value="alerty" className="px-3">
            Alerty
            {nieobejrzane > 0 && (
              <span className="rounded-full bg-foreground px-1.5 text-xs leading-4 text-background">{nieobejrzane}</span>
            )}
          </TabsTrigger>
          <TabsTrigger value="kalibracja" className="px-3">Kalibracja</TabsTrigger>
        </TabsList>
        <DodajReklame poDodaniu={(nowa) => dolacz([nowa])} />
      </header>
      <main className="flex min-h-0 flex-1 flex-col px-8 py-6">
        {wiersze ? (
          <>
            <TabsContent value="analityka" className="flex min-h-0 flex-col">
              <Analityka wiersze={wiersze} otwarteId={otwarte?.id} otworz={otworz} />
            </TabsContent>
            <TabsContent value="alerty" className="flex min-h-0 flex-col">
              <Alerty alerty={alerty} obejrzane={obejrzane} otwarteId={otwarte?.id} otworz={otworz} />
            </TabsContent>
            <TabsContent value="kalibracja" className="min-h-0 overflow-auto">
              <Kalibracja prog={prog} ustawProg={setProg} wiersze={wiersze} odswiez={odswiez} />
            </TabsContent>
          </>
        ) : (
          <p className="text-muted-foreground">Wczytywanie…</p>
        )}
      </main>
      {otwarta && (
        <Szczegoly
          reklama={otwarta}
          wiersze={wiersze}
          sprawy={otwarte.sprawy}
          otworz={(id) => otworz(id, otwarte.sprawy)}
          zamknij={() => setOtwarte(null)}
          podmien={podmien}
          odswiez={odswiez}
        />
      )}
      {/* The open sheet makes the rest of the page inert; the undo button in a toast must stay clickable. */}
      <Toaster position="top-right" className="toaster group pointer-events-auto" />
    </Tabs>
  )
}
