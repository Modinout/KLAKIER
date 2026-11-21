import anyio
from fastapi import WebSocket, WebSocketDisconnect

klienci = set()


async def sluchaj(gniazdo: WebSocket):
    await gniazdo.accept()
    klienci.add(gniazdo)
    try:
        # Clients send nothing; waiting for a message is how a closed connection shows up.
        while True:
            await gniazdo.receive_text()
    except WebSocketDisconnect:
        klienci.discard(gniazdo)


def wyslij(tekst):
    """For plain def endpoints: they run in the threadpool, the sockets live on the event loop."""
    anyio.from_thread.run(rozeslij, tekst)


async def rozeslij(tekst):
    for gniazdo in list(klienci):
        try:
            await gniazdo.send_text(tekst)
        except Exception:
            klienci.discard(gniazdo)
