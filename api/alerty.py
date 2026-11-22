import anyio
from fastapi import WebSocket, WebSocketDisconnect

klienci = set()


async def sluchaj(gniazdo: WebSocket):
    await gniazdo.accept()
    klienci.add(gniazdo)
    try:
        # Klienci nic nie wysyłają; czekanie na wiadomość to sposób, w jaki wychodzi zamknięcie połączenia.
        while True:
            await gniazdo.receive_text()
    except WebSocketDisconnect:
        klienci.discard(gniazdo)


def wyslij(tekst):
    """Dla zwykłych endpointów def: działają w puli wątków, a gniazda żyją w pętli zdarzeń."""
    anyio.from_thread.run(rozeslij, tekst)


async def rozeslij(tekst):
    for gniazdo in list(klienci):
        try:
            await gniazdo.send_text(tekst)
        except Exception:
            klienci.discard(gniazdo)
