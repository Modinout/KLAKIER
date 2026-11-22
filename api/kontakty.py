# Contacts in the text of an ad that tie it to other ads: phone numbers and messenger addresses.
import re

TELEGRAM = re.compile(
    r'\b(?:t|telegram)\.me/(?:s/)?(?:(?:joinchat/|\+)([\w-]{8,})|([A-Za-z][A-Za-z0-9_]{4,31}))', re.IGNORECASE)
WHATSAPP = re.compile(r'\b(?:wa\.me/|whatsapp\.com/send/?\?phone=)\+?(\d{8,15})', re.IGNORECASE)
MIEDZYNARODOWY = re.compile(r'\+\(?\d{1,4}\)?(?:[ .\-]?\(?\d{1,4}\)?){2,7}')
# Polish numbers have nine digits and never start with 0. A digit run glued to a word, a URL or a decimal part is an
# id or an amount, and so is one followed by a currency.
KRAJOWY = re.compile(
    r'(?<![\w+\-.,/=#&?%])'
    r'(?:[1-9]\d{2}[ \-]\d{3}[ \-]\d{3}|[1-9]\d{8}|\(?[1-9]\d\)?[ \-]\d{3}[ \-]\d{2}[ \-]\d{2})'
    r'(?![\w\-]|[./=]\w|\s?(?:zł|zl|pln|eur|usd|€|\$|%|tys|mln|mld))',
    re.IGNORECASE,
)
NUMER_FIRMY = re.compile(r'(?:nip|regon|krs|pesel|konta|rachunku|iban)\W{0,3}$', re.IGNORECASE)


def kontakty(tekst):
    """(powod, wartosc) pairs: ten_sam_telefon with the number as +<digits>, ten_sam_komunikator with the address."""
    znalezione = set()
    for adres in TELEGRAM.finditer(tekst):
        # Invite links are case-sensitive, channel names are not.
        znalezione.add(('ten_sam_komunikator', 't.me/+' + adres[1] if adres[1] else 't.me/' + adres[2].lower()))
    for adres in WHATSAPP.finditer(tekst):
        znalezione.add(('ten_sam_komunikator', 'wa.me/' + adres[1]))
    for zapis in MIEDZYNARODOWY.finditer(tekst):
        numer = miedzynarodowy(re.sub(r'\D', '', zapis[0]))
        if numer:
            znalezione.add(('ten_sam_telefon', numer))
    # A foreign number without its prefix could read as a Polish one.
    bez_miedzynarodowych = MIEDZYNARODOWY.sub(' ', tekst)
    for zapis in KRAJOWY.finditer(bez_miedzynarodowych):
        cyfry = re.sub(r'\D', '', zapis[0])
        if not NUMER_FIRMY.search(bez_miedzynarodowych[max(0, zapis.start() - 12):zapis.start()]) and not wzor(cyfry):
            znalezione.add(('ten_sam_telefon', '+48' + cyfry))
    return znalezione


def miedzynarodowy(cyfry):
    if cyfry.startswith('48'):
        # A Polish number has exactly nine digits after 48; more digits belong to the words after it.
        return '+' + cyfry[:11] if len(cyfry) >= 11 and not wzor(cyfry[2:11]) else None
    return '+' + cyfry if 9 <= len(cyfry) <= 15 and not wzor(cyfry) else None


def wzor(cyfry):
    """A form placeholder such as 512 345 678 or 999 999 999, not a number anyone answers."""
    return re.search(r'(\d)\1{5}|123456|234567|345678|456789', cyfry) is not None
