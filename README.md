# Anesthesie Congres Tracker

Website die Europese en Amerikaanse anesthesiologie- en pijngeneeskunde-congressen
(en conferenties/symposia) bijhoudt: wanneer, waar, welk onderwerp, kosten, en of
de datum in een even of oneven weeknummer valt. Doorzoekbaar en filterbaar op
locatie, datum, weeknummer en onderwerp.

Gebouwd als leerproject met Claude, met pure HTML/CSS/JS (geen framework).

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

### Zelf draaien

```bash
pip install -r scripts/requirements.txt
python3 scripts/scrape_congressen.py            # schrijft data/congressen.js
python3 scripts/scrape_congressen.py --check    # exit 1 als er wijzigingen zouden zijn, schrijft niets
```

## Tegel op je iPhone

Twee manieren:
- **Via Safari:** open [de site](https://rik-spacecowboy.github.io/Anesthesie/) → deelknop → "Zet op beginscherm".
- **Via profielbestand:** [`iphone/Anesthesie-Congressen.mobileconfig`](iphone/Anesthesie-Congressen.mobileconfig)
  op je iPhone zetten (bv. AirDrop of mail naar jezelf) en openen → Instellingen → "Profiel gedownload" → Installeer.
  Het profiel is niet ondertekend, dus iOS toont daar een waarschuwing; het bevat alleen de tegel (URL + icoon).
