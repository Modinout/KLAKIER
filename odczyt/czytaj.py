# Reads the text from an ad image with PP-OCR on the CPU. The models load once, when this module is imported.
#   from czytaj import czytaj
#   czytaj(open('probka.png', 'rb').read())  ->  'Zainwestuj 900 zł i zarabiaj\n20 000 zł miesięcznie\n...'
import threading

import cv2
import numpy as np
from paddleocr import PaddleOCR

# oneDNN is off: with it this Paddle version fails on the CPU.
# Four threads: with more, a read took longer and its time varied more on a busy machine.
_ocr = PaddleOCR(text_detection_model_name='PP-OCRv6_medium_det', text_recognition_model_name='PP-OCRv6_medium_rec',
                 use_doc_orientation_classify=False, use_doc_unwarping=False, use_textline_orientation=True,
                 device='cpu', enable_mkldnn=False, cpu_threads=4)
# The predictor must not run in two threads at once.
_kolejka = threading.Lock()


def czytaj(obraz):
    piksele = cv2.imdecode(np.frombuffer(obraz, np.uint8), cv2.IMREAD_COLOR)
    if piksele is None:
        raise ValueError('To nie jest obraz.')
    with _kolejka:
        strony = list(_ocr.predict(piksele))
    return '\n'.join(linia for strona in strony for linia in strona['rec_texts'])
