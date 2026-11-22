# Kontakty w tekście reklamy, które wiążą ją z innymi reklamami: numery telefonów i adresy komunikatorów.
import re

TELEGRAM = re.compile(
    r'\b(?:t|telegram)\.me/(?:s/)?(?:(?:joinchat/|\+)([\w-]{8,})|([A-Za-z][A-Za-z0-9_]{4,31}))', re.IGNORECASE)
WHATSAPP = re.compile(r'\b(?:wa\.me/|whatsapp\.com/send/?\?phone=)\+?(\d{8,15})', re.IGNORECASE)
MIEDZYNARODOWY = re.compile(r'\+\(?\d{1,4}\)?(?:[ .\-]?\(?\d{1,4}\)?){2,7}')
# Polskie numery mają dziewięć cyfr i nie zaczynają się od 0. Ciąg cyfr przyklejony do słowa, adresu URL lub części
# dziesiętnej to identyfikator albo kwota, tak samo jak ciąg, po którym stoi waluta.
KRAJOWY = re.compile(
    r'(?<![\w+\-.,/=#&?%])'
    r'(?:[1-9]\d{2}[ \-]\d{3}[ \-]\d{3}|[1-9]\d{8}|\(?[1-9]\d\)?[ \-]\d{3}[ \-]\d{2}[ \-]\d{2})'
    r'(?![\w\-]|[./=]\w|\s?(?:zł|zl|pln|eur|usd|€|\$|%|tys|mln|mld))',
    re.IGNORECASE,
)
NUMER_FIRMY = re.compile(r'(?:nip|regon|krs|pesel|konta|rachunku|iban)\W{0,3}$', re.IGNORECASE)


def kontakty(tekst):
    """Pary (powod, wartosc): ten_sam_telefon z numerem jako +<cyfry>, ten_sam_komunikator z adresem."""
    znalezione = set()
    for adres in TELEGRAM.finditer(tekst):
        # Linki zaproszeń rozróżniają wielkość liter, nazwy kanałów nie.
        znalezione.add(('ten_sam_komunikator', 't.me/+' + adres[1] if adres[1] else 't.me/' + adres[2].lower()))
    for adres in WHATSAPP.finditer(tekst):
        znalezione.add(('ten_sam_komunikator', 'wa.me/' + adres[1]))
    for zapis in MIEDZYNARODOWY.finditer(tekst):
        numer = miedzynarodowy(re.sub(r'\D', '', zapis[0]))
        if numer:
            znalezione.add(('ten_sam_telefon', numer))
    # Zagraniczny numer bez prefiksu mógłby wyglądać jak polski.
    bez_miedzynarodowych = MIEDZYNARODOWY.sub(' ', tekst)
    for zapis in KRAJOWY.finditer(bez_miedzynarodowych):
        cyfry = re.sub(r'\D', '', zapis[0])
        if not NUMER_FIRMY.search(bez_miedzynarodowych[max(0, zapis.start() - 12):zapis.start()]) and not wzor(cyfry):
            znalezione.add(('ten_sam_telefon', '+48' + cyfry))
    return znalezione


def miedzynarodowy(cyfry):
    if cyfry.startswith('48'):
        # Polski numer ma dokładnie dziewięć cyfr po 48; dalsze cyfry należą do słów po nim.
        return '+' + cyfry[:11] if len(cyfry) >= 11 and not wzor(cyfry[2:11]) else None
    return '+' + cyfry if 9 <= len(cyfry) <= 15 and not wzor(cyfry) else None


def wzor(cyfry):
    """Wzorzec z formularza, jak 512 345 678 czy 999 999 999, a nie numer, pod którym ktoś odbiera."""
    return re.search(r'(\d)\1{5}|123456|234567|345678|456789', cyfry) is not None
