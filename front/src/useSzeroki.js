import { useSyncExternalStore } from 'react'

// Od tej szerokości szczegóły sprawy stoją obok listy, węższy ekran dostaje wysuwany arkusz.
const ZAPYTANIE = window.matchMedia('(min-width: 1280px)')

function sledz(zmiana) {
  ZAPYTANIE.addEventListener('change', zmiana)
  return () => ZAPYTANIE.removeEventListener('change', zmiana)
}

export default function useSzeroki() {
  return useSyncExternalStore(sledz, () => ZAPYTANIE.matches)
}
