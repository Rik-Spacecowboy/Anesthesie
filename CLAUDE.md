# Anesthesie Congres Tracker

## Artifact altijd bijwerken (zonder te vragen)

De site bestaat op twee plekken:
- GitHub Pages (https://rik-spacecowboy.github.io/Anesthesie/), publiceert vanzelf bij elke push naar `main`;
- een claude.ai-artifact: https://claude.ai/artifact/M6EVEsBU4KFehuVqLgvhPn. **De tegel op Rik's iPhone opent
  deze artifact**, en die werkt niet vanzelf bij.

Zodra een wijziging aan `index.html` of `data/congressen.js` op `main` staat, publiceer je de artifact meteen
opnieuw, zonder het eerst te vragen:

1. `python3 scripts/bouw_artifact.py` (schrijft `build/artifact/index.html` + `build/artifact/data/congressen.js`);
2. lees de artifact eerst (Artifact-tool, `action: "read"` op de URL hierboven, plus de file `data/congressen.js`);
3. publiceer met de Artifact-tool: `url` = de URL hierboven, `file_path` = `build/artifact/index.html`,
   `files` = `{"data/congressen.js": "build/artifact/data/congressen.js"}`. Geen `icon` meegeven.

Faalt het bouwscript (index.html is zo veranderd dat een aanpassing niet meer past), pas dan het script aan
in plaats van het over te slaan. Daarnaast checkt een geplande Routine twee keer per dag of de artifact
achterloopt op `main` (vangt bv. scraper-PR's op die in GitHub zelf gemerged worden).
