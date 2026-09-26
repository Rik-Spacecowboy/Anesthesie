"""Leest de JS-databestanden (data/congressen.js, data/aanvullingen.js) in Python.

Die bestanden zijn JavaScript-literals (`const NAAM = [...]` / `{...}`) met kale
veldnamen, //-commentaar en soms een komma na het laatste element. Dit zet zo'n
literal om naar JSON; strings moeten tussen dubbele aanhalingstekens staan (zoals
in beide bestanden het geval is).
"""
import json
import re


def js_naar_json(tekst):
    uit = []
    i, n = 0, len(tekst)
    while i < n:
        c = tekst[i]
        if c == '"':
            j = i + 1
            while tekst[j] != '"':
                j += 2 if tekst[j] == "\\" else 1
            uit.append(tekst[i:j + 1])
            i = j + 1
        elif tekst.startswith("//", i):
            eind = tekst.find("\n", i)
            i = n if eind == -1 else eind
        elif c.isalpha() or c == "_":
            woord = re.match(r"[A-Za-z_]\w*", tekst[i:]).group(0)
            i += len(woord)
            # Kale veldnaam (gevolgd door ':') krijgt aanhalingstekens; true/false/null blijven.
            uit.append(json.dumps(woord) if tekst[i:].lstrip().startswith(":") else woord)
        elif c == ",":
            # Komma na het laatste element is in JS toegestaan, in JSON niet.
            if not re.match(r"\s*[}\]]", tekst[i + 1:]):
                uit.append(c)
            i += 1
        else:
            uit.append(c)
            i += 1
    return "".join(uit)


def lees_js_data(pad, naam):
    """Geeft de waarde van `const <naam> = ...;` uit het bestand terug als Python-object."""
    tekst = pad.read_text(encoding="utf-8")
    m = re.search(rf"^const {naam}\s*=", tekst, re.M)
    if not m:
        raise ValueError(f"'const {naam} =' niet gevonden in {pad}")
    literal = tekst[m.end():].strip()
    if literal.endswith(";"):
        literal = literal[:-1]
    return json.loads(js_naar_json(literal))
