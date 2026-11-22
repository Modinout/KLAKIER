# Czyta tekst z obrazu reklamy za pomocą PP-OCR na CPU. Modele ładują się raz, przy imporcie tego modułu.
#   from czytaj import czytaj
#   czytaj(open('probka.png', 'rb').read())  ->  'Zainwestuj 900 zł i zarabiaj\n20 000 zł miesięcznie\n...'
import io
import threading

import cv2
import numpy as np
from paddleocr import PaddleOCR
from PIL import Image

# Mały plik może się rozpakować w ogromną bitmapę, więc rozmiar czyta się z nagłówka przed dekodowaniem.
NAJWIECEJ_PIKSELI = 25_000_000

# oneDNN wyłączone: z nim ta wersja Paddle zawodzi na CPU.
# Cztery wątki: przy większej liczbie odczyt trwał dłużej, a jego czas bardziej się wahał na zajętej maszynie.
_ocr = PaddleOCR(text_detection_model_name='PP-OCRv6_medium_det', text_recognition_model_name='PP-OCRv6_medium_rec',
                 use_doc_orientation_classify=False, use_doc_unwarping=False, use_textline_orientation=True,
                 device='cpu', enable_mkldnn=False, cpu_threads=4)
# Predyktor nie może działać w dwóch wątkach naraz.
_kolejka = threading.Lock()


def czytaj(obraz):
    try:
        with Image.open(io.BytesIO(obraz)) as naglowek:
            szerokosc, wysokosc = naglowek.size
    except Exception as blad:
        raise ValueError('To nie jest obraz.') from blad
    if szerokosc * wysokosc > NAJWIECEJ_PIKSELI:
        raise ValueError('Obraz jest za duży.')
    piksele = cv2.imdecode(np.frombuffer(obraz, np.uint8), cv2.IMREAD_COLOR)
    if piksele is None:
        raise ValueError('To nie jest obraz.')
    with _kolejka:
        strony = list(_ocr.predict(piksele))
    return '\n'.join(linia for strona in strony for linia in strona['rec_texts'])
