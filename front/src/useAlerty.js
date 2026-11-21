import { useEffect } from 'react'
import { toast } from 'sonner'
import { pobierzReklame } from './api.js'

const PONOWNIE_MS = 3000

export default function useAlerty(dolacz) {
  useEffect(() => {
    let gniazdo
    let zegar
    let koniec = false

    function polacz() {
      const protokol = location.protocol === 'https:' ? 'wss://' : 'ws://'
      gniazdo = new WebSocket(protokol + location.host + '/api/alerty')
      gniazdo.onmessage = (zdarzenie) => {
        const alert = JSON.parse(zdarzenie.data)
        if (alert.zrodlo === 'test') return
        pobierzReklame(alert.id)
          .then((reklama) => {
            dolacz([reklama])
            toast('Nowy alert', { description: reklama.reklamodawca ?? reklama.url })
          })
          // The next list refresh brings the ad anyway.
          .catch(() => {})
      }
      gniazdo.onclose = () => {
        if (!koniec) zegar = setTimeout(polacz, PONOWNIE_MS)
      }
    }

    polacz()
    return () => {
      koniec = true
      clearTimeout(zegar)
      gniazdo.close()
    }
  }, [dolacz])
}
