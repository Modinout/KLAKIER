// Mierzy ostrzeżenie o ryzyku na stronie tak, jak rysuje je przeglądarka. Zwraca rozmiar czcionki przeważający
// w widocznym tekście, informację, czy widoczny tekst wspomina o CFD, oraz najbardziej wyeksponowaną kopię
// ostrzeżenia: jej rozmiar i grubość czcionki, kontrast z tłem, czy jest widoczna i czy pokazuje się bez przewijania.
// Zwykłe pętle zamiast metod tablic: niektóre strony podmieniają Array.prototype.reduce lub sort na zepsute wersje.
() => {
  const OSTRZEZENIE = /inwestorów detalicznych|szybkiej utraty|retail investor accounts|losing money rapidly|Privatanleger|investisseurs particuliers|particuliere beleggers|retailových investorů|inversores minoristas|investitori al dettaglio/i;
  const CFD = /\bCFDs?\b|kontrakt\w* na różnic|contracts? for difference/i;
  const POMIJANE = { SCRIPT: true, STYLE: true, NOSCRIPT: true, TEMPLATE: true };
  const OBRAZ = /^(img|video|canvas|picture|svg)$/i;
  const plotno = document.createElement('canvas').getContext('2d', { willReadFrequently: true });

  // Dowolny kolor CSS, razem z oklch(), jako kanały sRGB 0-255 i alfa 0-1.
  function rgba(kolor) {
    plotno.clearRect(0, 0, 1, 1);
    plotno.fillStyle = 'rgba(0, 0, 0, 0)';
    plotno.fillStyle = kolor;
    plotno.fillRect(0, 0, 1, 1);
    const piksel = plotno.getImageData(0, 0, 1, 1).data;
    return { r: piksel[0], g: piksel[1], b: piksel[2], a: piksel[3] / 255 };
  }

  function nalozony(gora, dol) {
    const kanal = (nazwa) => gora[nazwa] * gora.a + dol[nazwa] * (1 - gora.a);
    return { r: kanal('r'), g: kanal('g'), b: kanal('b'), a: 1 };
  }

  // Czy obraz jest rysowany pod środkiem elementu nad pierwszym jednolitym kolorem. Obraz nie musi należeć do
  // przodka, np. zdjęcie z ujemnym z-index. Środek zawiniętego tekstu może wypaść między jego liniami, więc warstwy
  // liczy się od pierwszej, która zawiera element. Kolory html i body zwykle malują kanwę pod każdym obrazem, więc
  // nie uważa się ich za ukrywające obraz.
  function obrazPod(element) {
    const prostokat = element.getBoundingClientRect();
    if (!prostokat.width) return false;
    const pod = document.elementsFromPoint(prostokat.left + prostokat.width / 2, prostokat.top + prostokat.height / 2);
    let i = 0;
    while (i < pod.length && !pod[i].contains(element)) i++;
    for (; i < pod.length; i++) {
      const styl = getComputedStyle(pod[i]);
      if (OBRAZ.test(pod[i].tagName) || styl.backgroundImage !== 'none') return true;
      if (rgba(styl.backgroundColor).a === 1 && pod[i] !== document.body && pod[i] !== document.documentElement) return false;
    }
    return false;
  }

  // Kolor za elementem albo null, gdy jest nieznany: za nim jest obraz lub gradient albo przezroczyste warstwy
  // nie mają pod sobą jednolitego koloru, więc zdjęcie rysowane przez inny element może przeświecać.
  function tlo(element) {
    if (obrazPod(element)) return null;
    const warstwy = [];
    for (let el = element; el; el = el.parentElement) {
      const styl = getComputedStyle(el);
      if (styl.backgroundImage !== 'none') return null;
      const kolor = rgba(styl.backgroundColor);
      if (kolor.a > 0) warstwy[warstwy.length] = kolor;
      if (kolor.a === 1) break;
    }
    if (warstwy.length && warstwy[warstwy.length - 1].a < 1) return null;
    // Bez żadnej warstwy tekst leży na białej stronie.
    let wynik = { r: 255, g: 255, b: 255, a: 1 };
    for (let i = warstwy.length - 1; i >= 0; i--) wynik = nalozony(warstwy[i], wynik);
    return wynik;
  }

  function jasnosc(kolor) {
    const liniowy = (kanal) => {
      const k = kanal / 255;
      return k <= 0.04045 ? k / 12.92 : ((k + 0.055) / 1.055) ** 2.4;
    };
    return 0.2126 * liniowy(kolor.r) + 0.7152 * liniowy(kolor.g) + 0.0722 * liniowy(kolor.b);
  }

  // Współczynnik kontrastu WCAG, od 1 do 21.
  function kontrast(element) {
    const za = tlo(element);
    if (!za) return null;
    const jasnoscTekstu = jasnosc(nalozony(rgba(getComputedStyle(element).color), za));
    const jasnoscTla = jasnosc(za);
    const stosunek = (Math.max(jasnoscTekstu, jasnoscTla) + 0.05) / (Math.min(jasnoscTekstu, jasnoscTla) + 0.05);
    return Math.round(stosunek * 100) / 100;
  }

  // Tekst dla czytników ekranu jest przycięty do 1 px, a tekst wypchnięty leży na lewo od strony.
  function widoczny(element) {
    const prostokat = element.getBoundingClientRect();
    return prostokat.width > 1 && prostokat.height > 1 && prostokat.right > 0
      && element.checkVisibility({ opacityProperty: true, visibilityProperty: true });
  }

  function gora(element) {
    return element.getBoundingClientRect().top + scrollY;
  }

  // Banery cookies i paski przypięte do okna nie są tekstem samej strony.
  function naNakladce(element) {
    for (let el = element; el; el = el.parentElement) {
      const pozycja = getComputedStyle(el).position;
      if (pozycja === 'fixed' || pozycja === 'sticky') return true;
    }
    return false;
  }

  // Liczy się najbardziej wyeksponowana kopia: widoczna przed ukrytą, potem największa, potem najwyższa.
  function wyrazniejsza(a, b) {
    if (a.widac !== b.widac) return a.widac;
    if (a.px !== b.px) return a.px > b.px;
    return gora(a.element) < gora(b.element);
  }

  const znakiWedlugPx = {};
  let naj = null;
  const przechodzien = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let wezel = przechodzien.nextNode(); wezel; wezel = przechodzien.nextNode()) {
    const element = wezel.parentElement;
    const tekst = wezel.data.replace(/\s+/g, ' ').trim();
    if (!tekst || !element || POMIJANE[element.tagName]) continue;
    const px = Math.round(parseFloat(getComputedStyle(element).fontSize) * 10) / 10;
    const widac = widoczny(element);
    // Ostrzeżenie jest wyłączone z rozmiaru przeważającego, więc długie ostrzeżenie nie ustali rozmiaru,
    // względem którego jest mierzone.
    if (OSTRZEZENIE.test(tekst)) {
      const kopia = { element, tekst, px, widac };
      if (!naj || wyrazniejsza(kopia, naj)) naj = kopia;
    } else if (widac && !naNakladce(element)) {
      znakiWedlugPx[px] = (znakiWedlugPx[px] || 0) + tekst.length;
    }
  }

  let przewazajacyPx = 0;
  const rozmiary = Object.keys(znakiWedlugPx);
  for (let i = 0; i < rozmiary.length; i++) {
    if (!przewazajacyPx || znakiWedlugPx[rozmiary[i]] > znakiWedlugPx[przewazajacyPx]) przewazajacyPx = rozmiary[i];
  }
  return {
    przewazajacy_px: Number(przewazajacyPx),
    cfd: CFD.test(document.body.innerText),
    ostrzezenie: naj ? {
      tekst: naj.tekst.substring(0, 300),
      px: naj.px,
      pogrubienie: Number(getComputedStyle(naj.element).fontWeight),
      kontrast: kontrast(naj.element),
      widoczne: naj.widac,
      bez_przewijania: naj.widac && gora(naj.element) < innerHeight,
    } : null,
  };
}
