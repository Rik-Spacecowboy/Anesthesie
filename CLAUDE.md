# Anesthesie Congres Tracker

De site is Nederlandstalig: steden en landen met een Nederlandse naam altijd in het Nederlands (Wenen, niet
Vienna). De scraper vertaalt via `LANDEN_NL`/`STEDEN_NL` in `scripts/scrape_congressen.py`; vul die aan als er een
Engelse naam doorheen glipt.

## Live zetten: altijd deze drie stappen

Rik's vaste instructie: elke live-gang omvat altijd alle drie, zonder dat hij erom hoeft te vragen.

1. **Lokaal testen**: `python3 -m http.server 8080` en de wijziging in de browser (Playwright/Chromium) controleren.
2. **GitHub**: via een PR naar `main`; GitHub Pages publiceert dan vanzelf. Controleer dat de run
   "pages build and deployment" voor die commit geslaagd is.
3. **Artifact**: direct daarna opnieuw publiceren, zie hieronder.

## Artifact altijd bijwerken (zonder te vragen)

De site bestaat op twee plekken:
- GitHub Pages (https://rik-spacecowboy.github.io/Anesthesie/), publiceert vanzelf bij elke push naar `main`;
- een claude.ai-artifact: https://claude.ai/artifact/M6EVEsBU4KFehuVqLgvhPn. **De tegel op Rik's iPhone opent
  deze artifact**, en die werkt niet vanzelf bij.

Zodra een wijziging aan `index.html` of een bestand in `data/` op `main` staat, publiceer je de artifact meteen
opnieuw, zonder het eerst te vragen:

1. `python3 scripts/bouw_artifact.py` (schrijft `build/artifact/index.html` + alle databestanden in `build/artifact/data/`);
2. lees de artifact eerst (Artifact-tool, `action: "read"` op de URL hierboven, plus elk bestand in `data/`);
3. publiceer met de Artifact-tool: `url` = de URL hierboven, `file_path` = `build/artifact/index.html`,
   `files` = één entry per bestand in `build/artifact/data/` én in `build/artifact/img/steden/`, bv.
   `{"data/congressen.js": "build/artifact/data/congressen.js", "data/steden.js": "build/artifact/data/steden.js",
   "img/steden/madrid.jpg": "build/artifact/img/steden/madrid.jpg", ...}`. Geen `icon` meegeven.

Faalt het bouwscript (index.html is zo veranderd dat een aanpassing niet meer past), pas dan het script aan
in plaats van het over te slaan. Daarnaast checkt een geplande Routine twee keer per dag of de artifact
achterloopt op `main` (vangt bv. scraper-PR's op die in GitHub zelf gemerged worden).

## PR's: Claude maakt én merget ze

Rik doet zelf geen PR's, ook niet de wekelijkse scrape-PR (`auto/scrape-congressen`). Laat dus nooit een PR
voor hem liggen: maak, controleer en merge hem zelf, en zet daarna live (zie hierboven). Elke maandag om 9:00
(Amsterdam) handelt de routine "Anesthesie: maandag scrape-PR + deadlines" de scrape-PR af en zoekt hij nieuwe
deadlines bij alle congressen (ook de commerciële; alleen ASA en NWAS niet).

## Steden: kaart en stadsfoto's

`data/steden.js` geeft per stad (sleutel = stadsnaam zoals in `data/congressen.js`) de coördinaten, de kaartregio
(`eu`, `na` of `null`) en een stadsfoto in `img/steden/`. Komt er een nieuwe stad in de data, voeg die dan toe:
coördinaten plus een foto van Wikimedia Commons met vrije licentie (CC BY, CC BY-SA, CC0 of publiek domein), met
fotograaf, licentie en bronpagina. Bekijk elke foto zelf (zoekresultaten op Commons zijn regelmatig een andere
plek of een detailfoto) en snijd bij tot 640×300 jpg (~35 KB). Zonder foto toont de kaart een zwarte kop.

## Agenda-feed (agenda.ics)

`agenda.ics` wordt gebouwd uit `data/congressen.js` + `data/aanvullingen.js`. Na elke wijziging in `data/`:
`python3 scripts/bouw_agenda.py` en `agenda.ics` meecommitten (de workflow "Controle" faalt anders).

## Kosten, nascholingspunten en deadlines

`data/congressen.js` komt uit de scraper; bewerk het niet met de hand. Kosten die de scraper niet vindt en
nascholingspunten staan in `data/aanvullingen.js` (handmatig, per congres-id, altijd met bron en
`gecontroleerd`-datum). Neem alleen bedragen, punten en deadlines over die letterlijk bij de organisator
staan; nooit schatten. Deadlines (`deadlines` in `data/aanvullingen.js`): datum = laatste dag die zeker nog
telt ("vóór 13 dec" wordt 12 dec). ASA en NWAS niet onderzoeken (hun voorwaarden verbieden AI/geautomatiseerd verzamelen).
