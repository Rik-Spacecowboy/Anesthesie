#!/usr/bin/env python3
"""Haalt bekende congresbronnen op en schrijft data/congressen.js opnieuw weg.

Bronnen die (nog) niet automatisch te scrapen zijn -- omdat de site
scrapers blokkeert (Cloudflare) of in de voorwaarden AI/automatisering
verbiedt -- staan handmatig in data/congressen.manual.json. Die worden
hier ongewijzigd overgenomen.

Gebruik:
    python3 scripts/scrape_congressen.py            schrijft data/congressen.js
    python3 scripts/scrape_congressen.py --check     exit 1 als er wijzigingen zouden zijn
"""
import json
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "congressen.js"
MANUAL_FILE = ROOT / "data" / "congressen.manual.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.0 Safari/605.1.15"
    )
}

MAANDEN = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
    "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12",
    # Nederlandse maandafkortingen die afwijken van de Engelse.
    "mrt": "03", "mei": "05", "okt": "10",
}

LANDEN_NL = {
    "italy": "Italië", "denmark": "Denemarken", "austria": "Oostenrijk",
    "spain": "Spanje", "portugal": "Portugal", "germany": "Duitsland",
    "france": "Frankrijk", "united kingdom": "Verenigd Koninkrijk",
    "netherlands": "Nederland", "belgium": "België", "greece": "Griekenland",
}


def vertaal_land(land):
    return LANDEN_NL.get(land.strip().lower(), land.strip())

WARNINGS = []


def warn(bron, boodschap):
    WARNINGS.append(f"[{bron}] {boodschap}")


def fetch_lines(url):
    """Haalt een pagina op en geeft de zichtbare tekst terug als lijst van regels."""
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    tekst = soup.get_text("\n")
    return [regel.strip() for regel in tekst.split("\n") if regel.strip()]


def maand_naar_nummer(naam):
    return MAANDEN.get(naam[:3].lower())


def maak_datum(jaar, maand_naam, dag):
    maand = maand_naar_nummer(maand_naam)
    if not maand:
        return None
    return f"{jaar}-{maand}-{int(dag):02d}"


def scrape_euroanaesthesia():
    """ESAIC (Euroanaesthesia). Voor 2026 staat de exacte datum op de venue-pagina;
    ESAIC's eigen homepage kondigt daarnaast al stad+jaar voor latere edities aan,
    maar (nog) niet de exacte datum -- die edities worden overgeslagen tot de
    datum bekend is, in plaats van met een geraden datum te werken."""
    bron_org = "https://esaic.org/"
    entries = []
    try:
        org_lines = fetch_lines(bron_org)
    except requests.RequestException as e:
        warn("Euroanaesthesia", f"kon {bron_org} niet ophalen: {e}")
        org_lines = []

    aangekondigd = {}
    for regel in org_lines:
        m = re.match(r"Euroanaesthesia\s+(20\d{2})\s*\|\s*(.+)", regel)
        if m:
            jaar, plaats = m.group(1), m.group(2).strip()
            aangekondigd[jaar] = plaats

    bron_venue = "https://www.ahoy.nl/en/events/congress/euroanaesthesia-2026"
    try:
        venue_lines = fetch_lines(bron_venue)
    except requests.RequestException as e:
        warn("Euroanaesthesia", f"kon {bron_venue} niet ophalen: {e}")
        venue_lines = []

    datum_2026 = None
    for regel in venue_lines:
        m = re.search(r"(\d{1,2})\s*[-–]\s*(\d{1,2})\s+(June|Jun)\s+2026", regel, re.I)
        if m:
            datum_2026 = (maak_datum("2026", "jun", m.group(1)), maak_datum("2026", "jun", m.group(2)))
            break

    if "2026" in aangekondigd and datum_2026:
        stad, _, land = aangekondigd["2026"].partition(",")
        entries.append({
            "id": "euroanaesthesia-2026",
            "naam": "Euroanaesthesia 2026",
            "organisatie": "ESAIC (European Society of Anaesthesiology and Intensive Care)",
            "land": land.strip() or "Nederland",
            "stad": stad.strip(),
            "datumStart": datum_2026[0],
            "datumEind": datum_2026[1],
            "onderwerp": ["algemene anesthesiologie", "intensive care"],
            "kosten": "Nog niet gepubliceerd",
            "bron": bron_venue,
        })
    elif "2026" in aangekondigd:
        warn("Euroanaesthesia", "2026-editie aangekondigd maar exacte datum niet gevonden op ahoy.nl -- entry overgeslagen.")

    for jaar, plaats in aangekondigd.items():
        if jaar == "2026":
            continue
        warn("Euroanaesthesia", f"{jaar}-editie al aangekondigd ({plaats.strip()}) maar zonder exacte datum -- nog niet toegevoegd, controleer {bron_org} handmatig.")

    return entries


def scrape_esra_congress():
    """ESRA Europe events-kalender: jaartal-koppen gevolgd door groepjes van
    (dagrange, maand, naam, locatie). We filteren op de jaarlijkse Annual Congress."""
    url = "https://esraeurope.org/meetings/?meeting_type=esra-events"
    try:
        lines = fetch_lines(url)
    except requests.RequestException as e:
        warn("ESRA", f"kon {url} niet ophalen: {e}")
        return []

    entries = []
    huidig_jaar = None
    i = 0
    while i < len(lines):
        regel = lines[i]
        if re.fullmatch(r"20\d{2}", regel):
            huidig_jaar = regel
            i += 1
            continue
        m = re.fullmatch(r"(\d{1,2})\s*-\s*(\d{1,2})", regel)
        if m and huidig_jaar and i + 2 < len(lines):
            dag_start, dag_eind = m.group(1), m.group(2)
            maand_naam = lines[i + 1]
            naam = lines[i + 2]
            locatie = lines[i + 3] if i + 3 < len(lines) else ""
            if "annual congress" in naam.lower() and re.match(r"^[A-Za-z]{3}$", maand_naam):
                datum_start = maak_datum(huidig_jaar, maand_naam, dag_start)
                datum_eind = maak_datum(huidig_jaar, maand_naam, dag_eind)
                stad, _, land = locatie.partition(",")
                if datum_start and datum_eind:
                    entries.append({
                        "id": f"esra-congress-{huidig_jaar}",
                        "naam": naam,
                        "organisatie": "ESRA (European Society of Regional Anaesthesia and Pain Therapy)",
                        "land": vertaal_land(land) if land else locatie.strip(),
                        "stad": stad.strip(),
                        "datumStart": datum_start,
                        "datumEind": datum_eind,
                        "onderwerp": ["regionale anesthesie", "pijntherapie"],
                        "kosten": "Nog niet gepubliceerd",
                        "bron": url,
                    })
            i += 4
            continue
        i += 1

    if not entries:
        warn("ESRA", f"geen 'Annual Congress' gevonden op {url} -- pagina-structuur mogelijk gewijzigd.")
    return entries


def scrape_painweek():
    """PAINWeek-conferentiesite toont zelf al de meest recent aangekondigde editie."""
    url = "https://conference.painweek.org/"
    try:
        lines = fetch_lines(url)
    except requests.RequestException as e:
        warn("PAINWeek", f"kon {url} niet ophalen: {e}")
        return []

    jaar = None
    for regel in lines:
        m = re.fullmatch(r"PAINWeek\s+(20\d{2})", regel)
        if m:
            jaar = m.group(1)
            break
    if not jaar:
        warn("PAINWeek", f"kon jaartal van de aangekondigde editie niet vinden op {url}.")
        return []

    for regel in lines:
        m = re.match(
            r"([A-Za-z]+)\s+(\d{1,2})\s*[-–]\s*(\d{1,2}),\s*20\d{2}\s*\|\s*(.+)", regel
        )
        if m:
            maand, dag_start, dag_eind, venue = m.groups()
            datum_start = maak_datum(jaar, maand, dag_start)
            datum_eind = maak_datum(jaar, maand, dag_eind)
            if datum_start and datum_eind:
                stad = "Las Vegas" if "las vegas" in venue.lower() else venue.split(",")[-1].strip()
                return [{
                    "id": f"painweek-{jaar}",
                    "naam": f"PAINWeek {jaar}",
                    "organisatie": "PAINWeek",
                    "land": "Verenigde Staten",
                    "stad": stad,
                    "datumStart": datum_start,
                    "datumEind": datum_eind,
                    "onderwerp": ["pijnmanagement", "multidisciplinair"],
                    "kosten": "Nog niet gepubliceerd",
                    "bron": url,
                }]

    warn("PAINWeek", f"jaartal {jaar} gevonden maar geen bijpassende datumregel op {url}.")
    return []


def scrape_asra():
    """ASRA Pain Medicine: events-education pagina bevat lopende tekst met de
    twee jaarlijkse bijeenkomsten (Regional Anesthesiology + Pain Medicine)."""
    url = "https://asra.com/events-education"
    try:
        lines = fetch_lines(url)
    except requests.RequestException as e:
        warn("ASRA", f"kon {url} niet ophalen: {e}")
        return []

    entries = []
    # Regels blijven gescheiden door \n (niet spatie) zodat een kop die vlak voor
    # een alinea staat (zonder scheidingsteken) niet per ongeluk aan elkaar plakt.
    volledige_tekst = "\n".join(lines)

    m = re.search(
        r"\b([A-Za-z .]{2,30}),\s*([A-Z]{2}),\s*is the site for the (\d+)\w{2} Annual Pain Medicine Meeting "
        r"being held ([A-Za-z]+) (\d{1,2})-(\d{1,2}),\s*(20\d{2})",
        volledige_tekst,
    )
    if m:
        stad, staat, nummer, maand, dag_start, dag_eind, jaar = m.groups()
        datum_start, datum_eind = maak_datum(jaar, maand, dag_start), maak_datum(jaar, maand, dag_eind)
        if datum_start and datum_eind:
            entries.append({
                "id": f"asra-pain-medicine-{jaar}",
                "naam": f"{nummer}th Annual Pain Medicine Meeting",
                "organisatie": "ASRA Pain Medicine",
                "land": "Verenigde Staten",
                "stad": stad.strip(),
                "datumStart": datum_start,
                "datumEind": datum_eind,
                "onderwerp": ["pijngeneeskunde"],
                "kosten": "Nog niet gepubliceerd",
                "bron": url,
            })
    else:
        warn("ASRA", "Pain Medicine Meeting-zin niet gevonden/gewijzigd op events-education pagina.")

    m2 = re.search(
        r"Join colleagues in ([A-Za-z .]{2,30}),\s*([A-Z]{2}),\s*on ([A-Za-z]+) (\d{1,2})-(\d{1,2}),\s*(20\d{2}),"
        r".{0,400}?regional anesthesia",
        volledige_tekst,
        re.I | re.S,
    )
    if m2:
        stad, staat, maand, dag_start, dag_eind, jaar = m2.groups()
        datum_start, datum_eind = maak_datum(jaar, maand, dag_start), maak_datum(jaar, maand, dag_eind)
        if datum_start and datum_eind:
            entries.append({
                "id": f"asra-regional-{jaar}",
                "naam": "Annual Regional Anesthesiology and Acute Pain Medicine Meeting",
                "organisatie": "ASRA Pain Medicine",
                "land": "Verenigde Staten",
                "stad": stad.strip(),
                "datumStart": datum_start,
                "datumEind": datum_eind,
                "onderwerp": ["regionale anesthesie", "acute pijn"],
                "kosten": "Nog niet gepubliceerd",
                "bron": url,
                "letOp": "Automatisch gevonden; ordinal (bv. '52nd') stond niet in de brontekst, controleer de exacte naam.",
            })
    else:
        warn("ASRA", "Regional Anesthesiology meeting-zin niet gevonden/gewijzigd op events-education pagina.")

    return entries


def scrape_nva_anesthesiologendagen():
    """NVA (Nederlandse Vereniging voor Anesthesiologie): de agenda-pagina toont
    een jaaroverzicht-kalender per maand met daarin de jaarlijkse
    Anesthesiologendagen. Andere NVA-events (cursussen, ledenbijeenkomsten,
    examens) worden genegeerd."""
    url = "https://www.anesthesiologie.nl/agenda/"
    try:
        lines = fetch_lines(url)
    except requests.RequestException as e:
        warn("NVA", f"kon {url} niet ophalen: {e}")
        return []

    maand_header = re.compile(
        r"^(Januari|Februari|Maart|April|Mei|Juni|Juli|Augustus|September|Oktober|November|December)\s+(20\d{2})$"
    )
    dag_regel = re.compile(r"^(\d{1,2})\s*(?:-\s*(\d{1,2}))?\s+([a-zA-Z]{3})$")

    entries = []
    huidig_jaar = None
    i = 0
    while i < len(lines):
        regel = lines[i]
        if maand_header.match(regel):
            huidig_jaar = maand_header.match(regel).group(2)
            i += 1
            continue
        m_dag = dag_regel.match(regel)
        if m_dag and huidig_jaar and i + 1 < len(lines):
            naam = lines[i + 1]
            if "anesthesiologendagen" in naam.lower():
                dag_start = m_dag.group(1)
                dag_eind = m_dag.group(2) or dag_start
                maand_naam = m_dag.group(3)
                datum_start = maak_datum(huidig_jaar, maand_naam, dag_start)
                datum_eind = maak_datum(huidig_jaar, maand_naam, dag_eind)
                if datum_start and datum_eind:
                    locatie = ""
                    if (
                        i + 3 < len(lines)
                        and not maand_header.match(lines[i + 3])
                        and not dag_regel.match(lines[i + 3])
                        and lines[i + 3] not in ("Congres", "Opleiding")
                    ):
                        locatie = lines[i + 3]
                    entries.append({
                        "id": f"nva-anesthesiologendagen-{huidig_jaar}",
                        "naam": naam,
                        "organisatie": "NVA (Nederlandse Vereniging voor Anesthesiologie)",
                        "land": "Nederland",
                        "stad": locatie or "Nog niet bekend",
                        "datumStart": datum_start,
                        "datumEind": datum_eind,
                        "onderwerp": ["algemene anesthesiologie"],
                        "kosten": "Nog niet gepubliceerd",
                        "bron": url,
                    })
            i += 2
            continue
        i += 1

    if not entries:
        warn("NVA", f"geen 'Anesthesiologendagen' gevonden op {url} -- pagina-structuur mogelijk gewijzigd.")
    return entries


def scrape_espa():
    """ESPA (European Society for Paediatric Anaesthesiology): de jaarlijkse
    congressite toont de actuele editie in een enkele titelregel. Toekomstige
    edities staan pas op een nieuwe site zodra die gepubliceerd wordt, dus
    verder dan het lopende/eerstvolgende jaar kijkt dit (nog) niet."""
    url = "https://www.espacongress.com/"
    try:
        lines = fetch_lines(url)
    except requests.RequestException as e:
        warn("ESPA", f"kon {url} niet ophalen: {e}")
        return []

    for regel in lines:
        m = re.search(
            r"(\d+)\w{2} European [Cc]ongress for Paediatric Anaesthesiology,\s*"
            r"([A-Za-z .]+),\s*([A-Za-z .]+)\s+(\d{2})/(\d{2})/(20\d{2})\s*-\s*(\d{2})/(\d{2})/(20\d{2})",
            regel,
        )
        if m:
            nummer, stad, land, d1, m1, j1, d2, m2, j2 = m.groups()
            if m1 == m2 and j1 == j2:
                return [{
                    "id": f"espa-congress-{j1}",
                    "naam": f"{nummer}th European Congress for Paediatric Anaesthesiology",
                    "organisatie": "ESPA (European Society for Paediatric Anaesthesiology)",
                    "land": vertaal_land(land),
                    "stad": stad.strip(),
                    "datumStart": f"{j1}-{m1}-{d1}",
                    "datumEind": f"{j2}-{m2}-{d2}",
                    "onderwerp": ["kinderanesthesiologie"],
                    "kosten": "Nog niet gepubliceerd",
                    "bron": url,
                }]

    warn("ESPA", f"geen congresregel gevonden/gewijzigd op {url}.")
    return []


SCRAPERS = [
    scrape_euroanaesthesia, scrape_esra_congress, scrape_painweek, scrape_asra,
    scrape_nva_anesthesiologendagen, scrape_espa,
]


def laad_handmatige_entries():
    if not MANUAL_FILE.exists():
        return []
    return json.loads(MANUAL_FILE.read_text())


def js_string(waarde):
    return json.dumps(waarde, ensure_ascii=False)


def render_entry(entry):
    velden = ["id", "naam", "organisatie", "land", "stad", "datumStart", "datumEind", "onderwerp", "kosten", "bron"]
    if "letOp" in entry:
        velden.append("letOp")
    regels = ["  {"]
    for idx, veld in enumerate(velden):
        komma = "," if idx < len(velden) - 1 else ""
        regels.append(f"    {veld}: {js_string(entry[veld])}{komma}")
    regels.append("  }")
    return "\n".join(regels)


HEADER = """// Congresdataset. Dit bestand wordt automatisch gegenereerd door
// scripts/scrape_congressen.py -- pas het dus niet direct handmatig aan.
//
// - Automatisch gescrapete congressen komen uit de bekende bronnen (ESAIC,
//   ESRA, PAINWeek, ASRA, NVA, ESPA); zie het bron-veld per congres.
// - Congressen die niet automatisch te scrapen zijn (geblokkeerd door de
//   site, of expliciet verboden in de sitevoorwaarden) staan handmatig in
//   data/congressen.manual.json en worden hier ongewijzigd overgenomen.
// - Kosten zijn vaak nog niet gepubliceerd zo ver van tevoren -- "Nog niet
//   gepubliceerd" betekent dus niet dat het gratis is.
"""


def bouw_bestand(entries):
    entries_sorted = sorted(entries, key=lambda e: e["datumStart"])
    body = ",\n".join(render_entry(e) for e in entries_sorted)
    return f"{HEADER}\nconst CONGRESSEN = [\n{body}\n];\n"


def main():
    check_only = "--check" in sys.argv

    gescraped = []
    for scraper in SCRAPERS:
        try:
            gescraped.extend(scraper())
        except Exception as e:
            warn(scraper.__name__, f"onverwachte fout: {e}")

    handmatig = laad_handmatige_entries()
    alle_entries = gescraped + handmatig

    if not alle_entries:
        print("Geen enkele bron leverde data op, bestaand data/congressen.js blijft ongewijzigd.", file=sys.stderr)
        return 1

    nieuwe_inhoud = bouw_bestand(alle_entries)
    bestaande_inhoud = DATA_FILE.read_text() if DATA_FILE.exists() else ""

    if WARNINGS:
        print("Waarschuwingen tijdens scrapen:", file=sys.stderr)
        for w in WARNINGS:
            print(f"  - {w}", file=sys.stderr)

    if nieuwe_inhoud == bestaande_inhoud:
        print("Geen wijzigingen.")
        return 0

    if check_only:
        print("Er zijn wijzigingen (niet geschreven, --check actief).")
        return 1

    DATA_FILE.write_text(nieuwe_inhoud)
    print(f"data/congressen.js bijgewerkt met {len(alle_entries)} congressen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
