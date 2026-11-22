# Zamienia mowę z nagrania reklamy na tekst modelem Whisper na CPU. Model ładuje się raz, przy imporcie modułu.
#   from sluchaj import sluchaj
#   sluchaj(open('probka_mowa.mp3', 'rb').read())  ->  'Invest only two hundred and fifty dollars ...'
import io
import threading

from faster_whisper import WhisperModel

# Dłuższe nagranie to już nie reklama, a jego zamiana na tekst trwałaby kilka minut.
NAJDLUZEJ_S = 600

_model = WhisperModel('small', device='cpu', compute_type='int8', cpu_threads=4)
# Model nie może działać w dwóch wątkach naraz.
_kolejka = threading.Lock()


def sluchaj(nagranie):
    with _kolejka:
        try:
            fragmenty, info = _model.transcribe(io.BytesIO(nagranie), beam_size=1, vad_filter=True)
        except Exception as blad:
            raise ValueError('To nie jest nagranie.') from blad
        if info.duration > NAJDLUZEJ_S:
            raise ValueError('Nagranie jest za długie.')
        return ' '.join(f.text.strip() for f in fragmenty).strip()
