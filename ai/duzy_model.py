# Client of the big open model behind an OpenAI-compatible chat completions endpoint.
import json
import os

import httpx


def skonfigurowany():
    return bool(os.environ.get('DUZY_MODEL_URL') and os.environ.get('DUZY_MODEL_NAZWA'))


def zapytaj(prosba, temperature, max_tokens):
    odpowiedz = httpx.post(
        os.environ['DUZY_MODEL_URL'],
        headers={'Authorization': 'Bearer ' + os.environ.get('DUZY_MODEL_KLUCZ', '')},
        json={'model': os.environ['DUZY_MODEL_NAZWA'], 'temperature': temperature, 'max_tokens': max_tokens,
              'messages': [{'role': 'user', 'content': prosba}]},
        timeout=120,
    )
    odpowiedz.raise_for_status()
    return odpowiedz.json()['choices'][0]['message']['content']


def obiekt_json(odpowiedz):
    # Models often wrap the object in prose or a code fence.
    return json.loads(odpowiedz[odpowiedz.index('{'):odpowiedz.rindex('}') + 1])
