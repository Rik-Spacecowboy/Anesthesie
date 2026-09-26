#!/usr/bin/env python3
"""Bouwt de claude.ai-artifactversie van de site uit index.html + data/congressen.js.

De artifact (https://claude.ai/artifact/M6EVEsBU4KFehuVqLgvhPn) is een losse kopie van de
site, en de tegel op de iPhone opent die. Hij werkt niet vanzelf bij: na elke wijziging
op main moet hij opnieuw gepubliceerd worden (zie CLAUDE.md).

Aanpassingen t.o.v. de GitHub Pages-versie, omdat het artifact-frame dit afdwingt:
- geen eigen <html>/<head>/<body>: het platform levert dat skelet;
- donkere modus ook via data-theme (de thema-keuze van de viewer);
- sticky filterbalk onder de safe area van de telefoon;
- downloads, querystring en Web Share werken niet in een artifact, dus de .ics-knoppen
  en "Deel" worden verborgen en de filters gaan niet naar de URL;
- het meldformulier opent op GitHub Pages (versturen naar Web3Forms kan niet vanuit het frame).

Gebruik:
    python3 scripts/bouw_artifact.py [uitvoermap]    # standaard: build/artifact
Schrijft <uitvoermap>/index.html en <uitvoermap>/data/*.js (zie DATABESTANDEN).
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Alle databestanden die index.html laadt; publiceer ze allemaal mee (zie CLAUDE.md).
DATABESTANDEN = ["congressen.js", "aanvullingen.js"]


def vervang(tekst, oud, nieuw):
    # Hard falen als index.html zo veranderd is dat een aanpassing niet meer past,
    # in plaats van stilletjes een half werkende artifact te publiceren.
    if tekst.count(oud) != 1:
        sys.exit(f"bouw_artifact: verwacht precies 1x {oud!r} in index.html, gevonden {tekst.count(oud)}x")
    return tekst.replace(oud, nieuw)


def bouw(bron):
    head = bron[bron.index("<head>") + 6:bron.index("</head>")]
    body = bron[bron.index("<body>") + 6:bron.index("</body>")]
    titel = re.search(r"<title>.*?</title>", head).group(0)
    fonts = re.search(r'<link href="https://fonts.googleapis.com[^>]+>', head).group(0)
    stijl = head[head.index("<style>"):head.index("</style>") + 8]
    s = f"{titel}\n{fonts}\n{stijl}\n{body}"

    donker = re.search(r"    @media \(prefers-color-scheme: dark\) \{\n      :root \{\n(.*?)      \}\n    \}\n", s, re.S)
    if not donker:
        sys.exit("bouw_artifact: dark-mode-blok in index.html niet gevonden")
    tokens = donker.group(1)
    s = s.replace(donker.group(0),
        "    @media (prefers-color-scheme: dark) {\n      :root:not([data-theme=\"light\"]) {\n        color-scheme: dark;\n"
        + tokens + "      }\n    }\n    :root[data-theme=\"dark\"] {\n      color-scheme: dark;\n"
        + tokens.replace("        ", "      ") + "    }\n")

    s = vervang(s, "position: sticky; top: 0; z-index: 20;", "position: sticky; top: env(safe-area-inset-top, 0px); z-index: 20;")
    s = vervang(s, '<button type="button" id="deelFilters" class="knop"', '<button type="button" id="deelFilters" class="knop" hidden')
    s = vervang(s, '<button type="button" class="actie ics"', '<button type="button" class="actie ics" hidden')
    s = vervang(s, "knop.hidden = aantal === 0;", "knop.hidden = true; // downloads werken niet in een artifact")
    s = vervang(s, "    function filtersNaarUrl() {\n", "    function filtersNaarUrl() {\n      return; // in een artifact komt de querystring niet door\n")
    # Versturen naar de formulierdienst mag vanuit het artifact-frame niet; open het meldformulier
    # daarom op GitHub Pages.
    s = vervang(s, "const MELDEN_EXTERN = '';", "const MELDEN_EXTERN = 'https://rik-spacecowboy.github.io/Anesthesie/';")
    return s


def main():
    uit = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "build" / "artifact"
    (uit / "data").mkdir(parents=True, exist_ok=True)
    (uit / "index.html").write_text(bouw((ROOT / "index.html").read_text(encoding="utf-8")), encoding="utf-8")
    for naam in DATABESTANDEN:
        shutil.copyfile(ROOT / "data" / naam, uit / "data" / naam)
    print(f"Artifact gebouwd in {uit}")


if __name__ == "__main__":
    main()
