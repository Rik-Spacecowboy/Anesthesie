#!/usr/bin/env python3
"""Bouwt agenda.ics: een agenda-abonnement met alle congressen en hun deadlines.

GitHub Pages serveert het bestand op https://rik-spacecowboy.github.io/Anesthesie/agenda.ics;
wie zich daarop abonneert (webcal://...), krijgt nieuwe congressen, gewijzigde data en
deadlines vanzelf in de eigen agenda. De inhoud komt uit data/congressen.js en
data/aanvullingen.js, dus na elke wijziging daarvan opnieuw bouwen (de scrape-workflow
doet dat zelf; de controle-workflow faalt als agenda.ics achterloopt).

Gebruik:
    python3 scripts/bouw_agenda.py            schrijft agenda.ics
    python3 scripts/bouw_agenda.py --check    exit 1 als agenda.ics niet actueel is
"""
import datetime
import sys
from pathlib import Path

from jsdata import lees_js_data

ROOT = Path(__file__).resolve().parent.parent
UITVOER = ROOT / "agenda.ics"
SITE = "https://rik-spacecowboy.github.io/Anesthesie/"
ONBEKEND = "Nog niet gepubliceerd"
# Vaste DTSTAMP: het bestand hangt dan alleen van de data af (idempotent, --check werkt).
DTSTAMP = "20260101T000000Z"

DEADLINE_TITEL = {
    "early-bird": "Laatste dag early-bird",
    "abstracts": "Laatste dag abstracts indienen",
    "registratie": "Laatste dag inschrijven",
    "annuleren": "Laatste dag annuleren met terugbetaling",
}


def ics_tekst(t):
    return str(t).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def vouw(regel):
    """RFC 5545: regels langer dan 75 octets vouwen (vervolgregel begint met een spatie)."""
    delen, huidig = [], ""
    for teken in regel:
        if len((huidig + teken).encode("utf-8")) > (74 if delen else 75):
            delen.append(huidig)
            huidig = ""
        huidig += teken
    delen.append(huidig)
    return "\r\n ".join(delen)


def compact(datum):
    return datum.replace("-", "")


def dag_erna(datum):
    return (datetime.date.fromisoformat(datum) + datetime.timedelta(days=1)).isoformat()


def locatie(c):
    return ", ".join(w for w in (c["stad"], c["land"]) if w and w.lower() not in ("nog niet bekend", "onbekend"))


def verrijk(congressen, aanvullingen):
    """Zelfde regels als pasAanvullingenToe() in index.html."""
    for c in congressen:
        a = aanvullingen.get(c["id"], {})
        if a.get("kosten") and c["kosten"] == ONBEKEND:
            c["kosten"] = a["kosten"]
        if a.get("punten"):
            c["punten"] = a["punten"]
        c["deadlines"] = sorted(a.get("deadlines", []), key=lambda d: d["datum"])


def vevent(uid, start, eind, titel, plek, omschrijving, url, alarm=False):
    regels = [
        "BEGIN:VEVENT",
        f"UID:{uid}@rik-spacecowboy.github.io",
        f"DTSTAMP:{DTSTAMP}",
        f"DTSTART;VALUE=DATE:{compact(start)}",
        f"DTEND;VALUE=DATE:{compact(dag_erna(eind))}",
        f"SUMMARY:{ics_tekst(titel)}",
    ]
    if plek:
        regels.append(f"LOCATION:{ics_tekst(plek)}")
    regels += [f"DESCRIPTION:{ics_tekst(omschrijving)}", f"URL:{url}", "TRANSP:TRANSPARENT"]
    if alarm:
        regels += ["BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{ics_tekst(titel)}",
                   "TRIGGER:-P7D", "END:VALARM"]
    regels.append("END:VEVENT")
    return regels


def bouw(congressen, aanvullingen):
    verrijk(congressen, aanvullingen)
    regels = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Anesthesie en Pijn Congressen//NL",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
        "X-WR-CALNAME:Anesthesie & Pijn congressen",
        f"X-WR-CALDESC:{ics_tekst('Congressen en deadlines (early-bird, abstracts) van ' + SITE)}",
        "REFRESH-INTERVAL;VALUE=DURATION:PT12H", "X-PUBLISHED-TTL:PT12H",
    ]
    for c in sorted(congressen, key=lambda c: (c["datumStart"], c["id"])):
        deadlines = [f"{DEADLINE_TITEL[d['soort']]}: {d['datum']}" for d in c["deadlines"]]
        omschrijving = "\n".join(filter(None, [
            c["organisatie"],
            f"Let op: {c['letOp']}" if c.get("letOp") else "",
            f"Kosten: {c['kosten']}",
            f"Nascholing: {c['punten']}" if c.get("punten") else "",
            *deadlines,
            f"Bron: {c['bron']}",
        ]))
        regels += vevent(c["id"], c["datumStart"], c["datumEind"], c["naam"], locatie(c), omschrijving, c["bron"])
        for d in c["deadlines"]:
            titel = f"{DEADLINE_TITEL[d['soort']]}: {c['naam']}"
            tekst = f"{c['naam']} ({c['datumStart']} t/m {c['datumEind']}, {locatie(c) or 'locatie onbekend'})\nBron: {d['bron']}"
            regels += vevent(f"{c['id']}-{d['soort']}", d["datum"], d["datum"], titel, "", tekst, d["bron"], alarm=True)
    regels.append("END:VCALENDAR")
    return "\r\n".join(vouw(r) for r in regels) + "\r\n"


def main():
    congressen = lees_js_data(ROOT / "data" / "congressen.js", "CONGRESSEN")
    aanvullingen = lees_js_data(ROOT / "data" / "aanvullingen.js", "AANVULLINGEN")
    onbekend = [d["soort"] for a in aanvullingen.values() for d in a.get("deadlines", []) if d["soort"] not in DEADLINE_TITEL]
    if onbekend:
        sys.exit(f"bouw_agenda: onbekende deadline-soort(en) in aanvullingen.js: {sorted(set(onbekend))}")
    nieuw = bouw(congressen, aanvullingen)
    bestaand = UITVOER.read_bytes().decode("utf-8") if UITVOER.exists() else ""
    if nieuw == bestaand:
        print("agenda.ics is actueel.")
        return 0
    if "--check" in sys.argv:
        print("agenda.ics loopt achter op de data: draai python3 scripts/bouw_agenda.py.")
        return 1
    UITVOER.write_bytes(nieuw.encode("utf-8"))
    print(f"agenda.ics bijgewerkt ({len(congressen)} congressen).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
