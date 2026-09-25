# Anesthesie Congres Tracker

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
   `files` = één entry per bestand in `build/artifact/data/`, bv.
   `{"data/congressen.js": "build/artifact/data/congressen.js", "data/aanvullingen.js": "build/artifact/data/aanvullingen.js"}`.
   Geen `icon` meegeven.

Faalt het bouwscript (index.html is zo veranderd dat een aanpassing niet meer past), pas dan het script aan
in plaats van het over te slaan. Daarnaast checkt een geplande Routine twee keer per dag of de artifact
achterloopt op `main` (vangt bv. scraper-PR's op die in GitHub zelf gemerged worden).

## Kosten en nascholingspunten

`data/congressen.js` komt uit de scraper; bewerk het niet met de hand. Kosten die de scraper niet vindt en
nascholingspunten staan in `data/aanvullingen.js` (handmatig, per congres-id, altijd met bron en
`gecontroleerd`-datum). Neem alleen bedragen en punten over die letterlijk bij de organisator staan; nooit
schatten. ASA en NWAS niet onderzoeken (hun voorwaarden verbieden AI/geautomatiseerd verzamelen).
