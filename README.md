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

Het script bezoekt de bekende bronnen (ESAIC, ESRA, PAINWeek, ASRA, NVA, ESPA) en zoekt daarbij standaard
meerdere jaren vooruit, niet alleen de komende editie.

**Niet alles is automatisch te scrapen:**
- ASA/ANESTHESIOLOGY staat handmatig in [`data/congressen.manual.json`](data/congressen.manual.json). De oude bron
  (apsf.org) blokkeert scrapers met een Cloudflare-check, en ASA's eigen site (asahq.org) verbiedt in de
  sitevoorwaarden expliciet gebruik van hun content met AI/automatisering. Werk deze entry dus zelf bij.
- Wanneer een bron een congres wel aankondigt maar de exacte datum nog niet publiceert (bv. Euroanaesthesia 2027+),
  slaat het script die editie over in plaats van te gokken. Dit verschijnt als waarschuwing in de scriptoutput.
- Sommige congressen zijn bewust **niet** toegevoegd, zoals WSAC (World Surgery and Anesthesia Congress): dat
  wordt georganiseerd door "Iris Scientific Group", een commerciële partij die tientallen bijna-identieke "World
  [Vakgebied] Congress"-events host over totaal ongerelateerde vakgebieden -- een klassiek kenmerk van een
  predatory conference. Nieuwe bronnen alleen toevoegen als het een erkende beroepsvereniging is.

### Zelf draaien

```bash
pip install -r scripts/requirements.txt
python3 scripts/scrape_congressen.py            # schrijft data/congressen.js
python3 scripts/scrape_congressen.py --check    # exit 1 als er wijzigingen zouden zijn, schrijft niets
```
