# Anesthesie Congres Tracker

Website die Europese en Amerikaanse anesthesiologie- en pijngeneeskunde-congressen
(en conferenties/symposia) bijhoudt: wanneer, waar, welk onderwerp, kosten, en of
de datum in een even of oneven weeknummer valt. Doorzoekbaar en filterbaar op
locatie, datum, weeknummer en onderwerp.

Gebouwd als leerproject met Claude, met pure HTML/CSS/JS (geen framework).

Verder per congres: toevoegen aan je agenda (`.ics` voor Apple Agenda/Outlook, of Google Agenda), en bewaren
met de ster. Bewaarde congressen staan alleen in de browser waarin je ze bewaart (`localStorage`); de iPhone-tegel
op je beginscherm telt daarbij als een aparte browser. Alle filters staan in de URL, dus een selectie is te delen
of te bookmarken via de "Deel"-knop.

Elke congreskaart heeft een stadsfoto als kop (Wikimedia Commons, vrije licentie, fotograaf vermeld op de foto;
zie `data/steden.js` en `img/steden/`) en een rand plus label in de kleur van het land. De weergave **Kaart** toont
de congressen als stippen op een kaart van Europa of Noord-Amerika (D3 + Natural Earth via world-atlas, pas geladen
als je de kaart opent); klik op een stip voor de congressen in die stad(en).

Weergave als kaarten of als compacte lijst (een regel per congres; klik voor de volledige kaart). Sorteren kan
op datum of prijs, en er is een maximumprijs; prijzen in $ en £ worden daarvoor omgerekend tegen een vaste koers
(alleen voor sorteren/filteren, getoond worden altijd de bedragen van de organisator). Wie congressen bewaart,
ziet bovenaan het aftellen naar het eigen eerstvolgende congres en een jaaroverzicht (congressen, landen,
nascholingspunten).

**Meldingen** ("Meld het" onderaan, "Klopt er iets niet?" per kaart) gaan via de formulierdienst Web3Forms naar de
beheerder; er staat geen e-mailadres op de site en melders hebben geen account nodig. De (openbare) sleutel staat
in `index.html` als `WEB3FORMS_SLEUTEL`; zolang die leeg is, is de meldfunctie verborgen. In de claude.ai-artifact
opent het formulier op GitHub Pages.

Afgelopen congressen zijn standaard verborgen; de chip "Ook afgelopen" toont ze weer ("Wis" zet alles terug naar
alleen komende congressen). Elke kaart linkt naar de vorige en volgende editie van dezelfde reeks.

### Deadlines en agenda-abonnement

Deadlines (einde early-bird, abstracts indienen, inschrijving sluit, annuleren met terugbetaling) staan per congres
in [`data/aanvullingen.js`](data/aanvullingen.js), handmatig en alleen letterlijk overgenomen van de organisator.
De kaart toont de komende deadlines met het aantal dagen dat nog rest; de chip "Deadline binnenkort" filtert op
deadlines binnen 30 dagen.

[`agenda.ics`](agenda.ics) is een agenda-abonnement met alle congressen en deadlines (deadlines met een herinnering
een week van tevoren). Abonneren: knop "Agenda-abonnement" op de site, of
`webcal://rik-spacecowboy.github.io/Anesthesie/agenda.ics`. Het bestand wordt gebouwd door
[`scripts/bouw_agenda.py`](scripts/bouw_agenda.py) uit de twee databestanden: draai dat na elke wijziging van
`data/`. De scrape-workflow doet het zelf; de workflow [Controle](.github/workflows/controle.yml) faalt als
`agenda.ics` achterloopt.

## Congresdata: automatisch gescraped

`data/congressen.js` wordt gegenereerd door [`scripts/scrape_congressen.py`](scripts/scrape_congressen.py) en dus
niet meer direct handmatig bewerkt. Een GitHub Action
([`.github/workflows/scrape-congressen.yml`](.github/workflows/scrape-congressen.yml)) draait dit script elke
maandag automatisch en opent een pull request met de wijzigingen -- er wordt nooit direct naar `main` gepusht,
zodat je alles even kunt checken voor het live gaat.

Het script bezoekt de bekende bronnen (ESAIC, ESRA, PAINWeek, ASRA, NVA, ESPA, EFIC, WCA/WFSA, SOAP, NYSORA,
BAPA, Association of Anaesthetists, London Pain Forum, SPA) en zoekt daarbij standaard meerdere jaren vooruit, niet
alleen de komende editie.

**Niet alles is automatisch te scrapen:**
- ASA/ANESTHESIOLOGY staat handmatig in [`data/congressen.manual.json`](data/congressen.manual.json). De oude bron
  (apsf.org) blokkeert scrapers met een Cloudflare-check, en ASA's eigen site (asahq.org) verbiedt in de
  sitevoorwaarden expliciet gebruik van hun content met AI/automatisering. Werk deze entry dus zelf bij.
- Wanneer een bron een congres wel aankondigt maar de exacte datum nog niet publiceert (bv. Euroanaesthesia 2027+),
  slaat het script die editie over in plaats van te gokken. Dit verschijnt als waarschuwing in de scriptoutput.
- NWAS (Northwest Anesthesia Seminars) staat handmatig in `data/congressen.manual.json`: hun voorwaarden verbieden
  geautomatiseerd verzamelen.
- WSAC, EACCM (Plenareno) en de International Conference on Surgery and Anesthesia (Inovine) zijn commerciele
  congresfabrieken, geen erkende beroepsverenigingen -- op uitdrukkelijk verzoek toegevoegd, handmatig bijgehouden
  en gelabeld met een `letOp` op de kaart. Zie ook het inklapbare infoblok bovenaan de site.
- Enkele pijncongressen (AAPM PainConnect, NANS, IASP World Congress on Pain) staan er ook handmatig bij, nog
  zonder scraper.
- Nog niet opgenomen: UF Ski Summit (robots.txt sluit ClaudeBot uit, en nog geen 2027-datum); Holiday Seminars
  (robots.txt sluit alle bots uit); OAA en Northern Lights (site blokkeert scrapers); SSAI 2028, PROSA 2028,
  British Pain Society 2027, WIP World Congress 2027 en het Refresher Course Obstetrische Anesthesiologie
  (nog geen datum gepubliceerd); IPME, Doctors Updates en de School/Academy for Integrative Medicine (onduidelijk
  welke organisatie precies bedoeld is).

### Kosten

Voor Euroanaesthesia, EFIC, ASRA Pain Medicine, NVA, Winter Pain Symposium en de handmatige entries haalt/heeft het
script een echt tarief op (meestal "vanaf X" of een range, want de meeste bronnen werken met meerdere tarieven
naargelang lidmaatschap/categorie -- de kaart zelf verwijst naar de bron voor de volledige tabel). Voor de overige
bronnen (ESRA, PAINWeek, WCA, SOAP, NYSORA, BAPA, Association of Anaesthetists, SPA, ICSA, PGA) is nog geen
betrouwbare, voorspelbare prijspagina gevonden; die tonen "Nog niet gepubliceerd" totdat dat lukt.

### `letOp`: twee soorten

Een kaart kan een `letOp`-label tonen, in twee smaken:
- **Grijs ("Let op")** -- een beperking in de data zelf (bv. stad niet gevonden, ordinal onzeker, bron blokkeert
  scrapers dus handmatig bijgehouden).
- **Oranje ("Commercieel congres")** -- geen datakwaliteitsprobleem, maar een waarschuwing dat de organisator een
  commerciële partij is (congresfabriek), geen erkende beroepsvereniging.

### Zelf draaien

```bash
pip install -r scripts/requirements.txt
python3 scripts/scrape_congressen.py            # schrijft data/congressen.js
python3 scripts/scrape_congressen.py --check    # exit 1 als er wijzigingen zouden zijn, schrijft niets
python3 scripts/bouw_agenda.py                  # schrijft agenda.ics (--check: exit 1 als die achterloopt)
```

Afgelopen congressen die een bron niet meer toont, blijven in `data/congressen.js` staan als archief (vorige
edities); een toekomstig congres dat uit de bron verdwijnt, verdwijnt wel.

## Tegel op je iPhone

Twee manieren:
- **Via Safari:** open [de site](https://rik-spacecowboy.github.io/Anesthesie/) → deelknop → "Zet op beginscherm".
- **Via profielbestand:** [`iphone/Anesthesie-Congressen.mobileconfig`](iphone/Anesthesie-Congressen.mobileconfig)
  op je iPhone zetten (bv. AirDrop of mail naar jezelf) en openen → Instellingen → "Profiel gedownload" → Installeer.
  Het profiel is niet ondertekend, dus iOS toont daar een waarschuwing; het bevat alleen de tegel (URL + icoon).
