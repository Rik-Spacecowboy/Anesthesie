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
import datetime
import json
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from jsdata import lees_js_data

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

EUROPESE_LANDEN_NL = {
    "albania": "Albanië", "andorra": "Andorra", "austria": "Oostenrijk",
    "belarus": "Wit-Rusland", "belgium": "België",
    "bosnia and herzegovina": "Bosnië en Herzegovina", "bulgaria": "Bulgarije",
    "croatia": "Kroatië", "cyprus": "Cyprus", "czech republic": "Tsjechië",
    "czechia": "Tsjechië", "denmark": "Denemarken", "estonia": "Estland",
    "finland": "Finland", "france": "Frankrijk", "germany": "Duitsland",
    "greece": "Griekenland", "hungary": "Hongarije", "iceland": "IJsland",
    "ireland": "Ierland", "italy": "Italië", "latvia": "Letland",
    "liechtenstein": "Liechtenstein", "lithuania": "Litouwen", "luxembourg": "Luxemburg",
    "malta": "Malta", "moldova": "Moldavië", "monaco": "Monaco", "montenegro": "Montenegro",
    "netherlands": "Nederland", "the netherlands": "Nederland",
    "north macedonia": "Noord-Macedonië", "norway": "Noorwegen", "poland": "Polen",
    "portugal": "Portugal", "romania": "Roemenië", "russia": "Rusland", "serbia": "Servië",
    "slovakia": "Slowakije", "slovenia": "Slovenië", "spain": "Spanje", "sweden": "Zweden",
    "switzerland": "Zwitserland", "turkey": "Turkije", "türkiye": "Turkije",
    "ukraine": "Oekraïne", "united kingdom": "Verenigd Koninkrijk",
    "uk": "Verenigd Koninkrijk", "england": "Verenigd Koninkrijk",
    "scotland": "Verenigd Koninkrijk", "wales": "Verenigd Koninkrijk",
}

LANDEN_NL = {
    **EUROPESE_LANDEN_NL,
    "united states": "Verenigde Staten", "usa": "Verenigde Staten", "canada": "Canada",
    "bahamas": "Bahama's", "thailand": "Thailand", "singapore": "Singapore",
}

# Landen (Engelse namen) die binnen de scope van de site vallen: Europa + Noord-Amerika.
SCOPE_LANDEN = set(EUROPESE_LANDEN_NL) | {"united states", "usa", "canada"}


def ordinaal(n):
    n = int(n)
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    return f"{n}" + {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


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
    schoon = (re.sub(r"\s+", " ", regel.replace("\xa0", " ")).strip() for regel in tekst.split("\n"))
    return [regel for regel in schoon if regel]


def fetch_lines_optional(url):
    """Zoals fetch_lines, maar geeft None terug bij een 404 (pagina bestaat (nog) niet)."""
    try:
        return fetch_lines(url)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return None
        raise


PRIJS_RE = re.compile(
    r"(?P<munt1>[€£$])\s?(?P<bedrag1>\d{1,3}(?:[.,]\d{3})*)(?:[.,]\d{2})?"
    r"|(?P<bedrag2>\d{1,3}(?:[.,]\d{3})*)(?:[.,]\d{2})?\s?(?P<munt2>EUR|USD|GBP|[€£$])",
)

MUNTTEKEN = {"EUR": "€", "USD": "$", "GBP": "£"}


def _prijs_uit_match(m):
    munt = m.group("munt1") or MUNTTEKEN.get(m.group("munt2"), m.group("munt2"))
    bedrag = (m.group("bedrag1") or m.group("bedrag2")).replace(".", "").replace(",", "")
    return munt, int(bedrag)


def vind_prijsrange_na_label(regels, label_patroon, aantal=3, max_afstand=6):
    """Zoekt de regel die op label_patroon matcht en pakt de eerstvolgende
    'aantal' bedragen erna (binnen max_afstand regels) als prijsrange.
    Geeft (laagste, hoogste, muntteken) terug, of None als niets gevonden is."""
    for i, regel in enumerate(regels):
        if re.search(label_patroon, regel, re.I):
            bedragen = []
            for j in range(i + 1, min(i + 1 + max_afstand, len(regels))):
                m = PRIJS_RE.search(regels[j])
                if m:
                    bedragen.append(_prijs_uit_match(m))
                    if len(bedragen) >= aantal:
                        break
            if bedragen:
                munt = bedragen[0][0]
                waarden = [b for _, b in bedragen]
                return min(waarden), max(waarden), munt
    return None


def formatteer_prijsrange(laag, hoog, munt, suffix=""):
    kern = f"{munt}{laag}" if laag == hoog else f"{munt}{laag}–{munt}{hoog}"
    return f"{kern}{suffix}"


def vind_prijsrange_tussen(regels, start_patroon, eind_patroon=None, min_bedrag=50, max_bedrag=3000):
    """Verzamelt alle bedragen tussen de regel die start_patroon matcht en de
    eerstvolgende regel die eind_patroon matcht (of het einde van de lijst).
    Bedragen buiten [min_bedrag, max_bedrag] worden genegeerd -- dat filtert
    dingen als overnachtingsprijzen per nacht of annuleringskosten eruit.
    Geeft (laagste, hoogste, muntteken) terug, of None als niets bruikbaars
    gevonden is."""
    start = None
    for i, regel in enumerate(regels):
        if re.search(start_patroon, regel, re.I):
            start = i
            break
    if start is None:
        return None
    eind = len(regels)
    if eind_patroon:
        for i in range(start + 1, len(regels)):
            if re.search(eind_patroon, regels[i], re.I):
                eind = i
                break
    bedragen = []
    for regel in regels[start:eind]:
        m = PRIJS_RE.search(regel)
        if m:
            munt, bedrag = _prijs_uit_match(m)
            if min_bedrag <= bedrag <= max_bedrag:
                bedragen.append((munt, bedrag))
    if not bedragen:
        return None
    munt = bedragen[0][0]
    waarden = [b for _, b in bedragen]
    return min(waarden), max(waarden), munt


def maand_naar_nummer(naam):
    return MAANDEN.get(naam[:3].lower())


def maak_datum(jaar, maand_naam, dag):
    maand = maand_naar_nummer(maand_naam)
    if not maand:
        return None
    return f"{jaar}-{maand}-{int(dag):02d}"


def parse_datumrange_engels(regel, jaar):
    """Herkent Engelse datumrange-teksten als '6-8 June 2026' of
    '30 April - 2 May 2026' en geeft (start, eind) als YYYY-MM-DD terug."""
    m = re.match(r"(\d{1,2})\s*[-–]\s*(\d{1,2})\s+([A-Za-z]+)\s+(20\d{2})", regel)
    if m and m.group(4) == str(jaar):
        d1, d2, maand, _ = m.groups()
        return maak_datum(jaar, maand, d1), maak_datum(jaar, maand, d2)
    m = re.match(r"(\d{1,2})\s+([A-Za-z]+)\s*[-–]\s*(\d{1,2})\s+([A-Za-z]+)\s+(20\d{2})", regel)
    if m and m.group(5) == str(jaar):
        d1, maand1, d2, maand2, _ = m.groups()
        return maak_datum(jaar, maand1, d1), maak_datum(jaar, maand2, d2)
    return None, None


def scrape_euroanaesthesia():
    """ESAIC (Euroanaesthesia). De homepage kondigt aankomende edities aan
    (stad + jaar); elke editie krijgt een eigen site op
    euroanaesthesia.org/<jaar>/ zodra de exacte datum bekend is -- deze
    blijkt in de praktijk al meerdere jaren vooruit te bestaan. Een editie
    zonder vindbare datum wordt overgeslagen in plaats van gegokt."""
    bron_org = "https://esaic.org/"
    try:
        org_lines = fetch_lines(bron_org)
    except requests.RequestException as e:
        warn("Euroanaesthesia", f"kon {bron_org} niet ophalen: {e}")
        return []

    aangekondigd = {}
    for regel in org_lines:
        m = re.match(r"Euroanaesthesia\s+(20\d{2})\s*\|\s*(.+)", regel)
        if m:
            jaar, plaats = m.group(1), m.group(2).strip()
            aangekondigd[jaar] = plaats

    entries = []
    for jaar, plaats in aangekondigd.items():
        jaar_url = f"https://euroanaesthesia.org/{jaar}/"
        try:
            jaar_lines = fetch_lines(jaar_url)
        except requests.RequestException as e:
            warn("Euroanaesthesia", f"kon {jaar_url} niet ophalen: {e}")
            continue

        datum_start = datum_eind = None
        for regel in jaar_lines:
            datum_start, datum_eind = parse_datumrange_engels(regel, jaar)
            if datum_start:
                break

        if not datum_start:
            warn("Euroanaesthesia", f"{jaar}-editie aangekondigd ({plaats}) maar geen datum gevonden op {jaar_url} -- overgeslagen.")
            continue

        kosten = "Nog niet gepubliceerd"
        try:
            reg_lines = fetch_lines(jaar_url + "registration/")
            bereik = vind_prijsrange_tussen(
                reg_lines, r"^Onsite Congress \(excluding", r"^Virtual Congress"
            )
            if bereik:
                kosten = formatteer_prijsrange(*bereik[:2], bereik[2], " (niet-lid, excl. btw)")
        except requests.RequestException:
            pass

        stad, _, land = plaats.partition(",")
        entries.append({
            "id": f"euroanaesthesia-{jaar}",
            "naam": f"Euroanaesthesia {jaar}",
            "organisatie": "ESAIC (European Society of Anaesthesiology and Intensive Care)",
            "land": vertaal_land(land) if land else plaats,
            "stad": stad.strip(),
            "datumStart": datum_start,
            "datumEind": datum_eind,
            "onderwerp": ["algemene anesthesiologie", "intensive care"],
            "kosten": kosten,
            "bron": jaar_url,
        })

    if not entries:
        warn("Euroanaesthesia", "geen enkele editie met vindbare datum gevonden.")
    return entries


ESRA_DAG_RE = re.compile(r"(\d{1,2})(?:\s*[-–]\s*(\d{1,2}))?")
ESRA_DAG_MAAND_RE = re.compile(r"(\d{1,2})(?:\s*[-–]\s*(\d{1,2}))?\s*([A-Za-z]{3})")
ESRA_MAAND_RE = re.compile(r"[A-Za-z]{3}")


def _esra_slug(naam):
    zonder_ordinaal = re.sub(r"^(\d+(st|nd|rd|th)|[IVXL]+)\s+", "", naam.strip())
    slug = re.sub(r"[^a-z0-9]+", "-", zonder_ordinaal.lower()).strip("-")
    return slug[len("esra-"):] if slug.startswith("esra-") else slug


def scrape_esra_congress():
    """ESRA Europe events-kalender (alle ESRA-events, niet alleen het Annual Congress):
    jaartal-koppen gevolgd door blokjes van (dagrange, maand, naam, locatie).
    Online events worden bewust overgeslagen; events zonder leesbare locatie of
    buiten de scope worden NIET stilzwijgend overgeslagen maar als warning gemeld."""
    url = "https://esraeurope.org/meetings/?meeting_type=esra-events"
    try:
        lines = fetch_lines(url)
    except requests.RequestException as e:
        warn("ESRA", f"kon {url} niet ophalen: {e}")
        return []

    entries = []
    gebruikte_ids = set()
    huidig_jaar = None
    i = 0
    while i < len(lines):
        regel = lines[i]
        if re.fullmatch(r"20\d{2}", regel):
            huidig_jaar = int(regel)
            i += 1
            continue
        if not huidig_jaar:
            i += 1
            continue

        # Datumblok: "17 - 22" + "Jan" op aparte regels, of samengevoegd ("17 - 22Jan").
        m = ESRA_DAG_RE.fullmatch(regel)
        if m and i + 2 < len(lines) and ESRA_MAAND_RE.fullmatch(lines[i + 1]):
            d1, d2, maand, volgende = m.group(1), m.group(2), lines[i + 1], i + 2
        else:
            m = ESRA_DAG_MAAND_RE.fullmatch(regel)
            if m and i + 1 < len(lines):
                d1, d2, maand, volgende = m.group(1), m.group(2), m.group(3), i + 1
            else:
                i += 1
                continue

        naam = lines[volgende]
        kandidaat = lines[volgende + 1] if volgende + 1 < len(lines) else ""
        is_locatie = bool(kandidaat) and not ESRA_DAG_RE.fullmatch(kandidaat) and (
            "," in kandidaat or kandidaat.lower() in {"online", "virtual", "webinar"}
        )
        locatie = kandidaat if is_locatie else ""
        i = volgende + (2 if is_locatie else 1)

        start = maak_datum(huidig_jaar, maand, d1)
        eind = maak_datum(huidig_jaar, maand, d2 or d1)
        if not start or not eind:
            warn("ESRA", f"datum niet te lezen voor '{naam}' ({d1}-{d2} {maand} {huidig_jaar}) -- niet toegevoegd, graag controleren.")
            continue
        if locatie.lower() in {"online", "virtual", "webinar"}:
            continue  # bewuste keuze (Rik, 23-09-2026): geen online events op de site
        if not locatie:
            warn("ESRA", f"'{naam}' ({start}) heeft geen locatie op de pagina -- niet toegevoegd, graag controleren.")
            continue

        stad, _, land = locatie.rpartition(",")
        stad, land = stad.strip(), land.strip()
        if land.lower() not in SCOPE_LANDEN:
            warn("ESRA", f"'{naam}' in {locatie} valt buiten de scope (Europa + Noord-Amerika) -- niet toegevoegd.")
            continue

        if "annual congress" in naam.lower():
            id_ = f"esra-congress-{huidig_jaar}"
        else:
            id_ = f"esra-{_esra_slug(naam)}-{huidig_jaar}"
        if id_ in gebruikte_ids:
            id_ = f"{id_}-{start}"
        gebruikte_ids.add(id_)

        entries.append({
            "id": id_,
            "naam": naam,
            "organisatie": "ESRA (European Society of Regional Anaesthesia and Pain Therapy)",
            "land": vertaal_land(land),
            "stad": stad,
            "datumStart": start,
            "datumEind": eind,
            "onderwerp": ["regionale anesthesie", "pijntherapie"],
            "kosten": "Nog niet gepubliceerd",
            "bron": url,
        })

    if not entries:
        warn("ESRA", f"geen enkel ESRA-event gevonden op {url} -- pagina-structuur mogelijk gewijzigd.")
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
            kosten = "Nog niet gepubliceerd"
            try:
                reg_lines = fetch_lines(f"{url}/pain-medicine-meeting/register")
                bereik = vind_prijsrange_tussen(
                    reg_lines, r"Physician Member of ASRA Pain Medicine", r"Additional Exhibitor Badge"
                )
                if bereik:
                    kosten = formatteer_prijsrange(*bereik[:2], bereik[2], " (afhankelijk van lidmaatschap/categorie)")
            except requests.RequestException:
                pass
            entries.append({
                "id": f"asra-pain-medicine-{jaar}",
                "naam": f"{ordinaal(nummer)} Annual Pain Medicine Meeting",
                "organisatie": "ASRA Pain Medicine",
                "land": "Verenigde Staten",
                "stad": stad.strip(),
                "datumStart": datum_start,
                "datumEind": datum_eind,
                "onderwerp": ["pijngeneeskunde"],
                "kosten": kosten,
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
                "letOpType": "data",
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
                    kosten = "Nog niet gepubliceerd"
                    try:
                        event_url = f"https://www.anesthesiologie.nl/agenda/anesthesiologendagen-{huidig_jaar}"
                        event_lines = fetch_lines_optional(event_url) or []
                        for j, eregel in enumerate(event_lines):
                            if re.match(r"Gewoon lid", eregel) and j + 1 < len(event_lines):
                                pm = re.search(
                                    r"€\s?(\d+)\s*\(gehele congres\).*?€\s?(\d+)\s*\(1 dag\)",
                                    event_lines[j + 1],
                                )
                                if pm:
                                    laag, hoog = sorted(int(x) for x in pm.groups())
                                    kosten = formatteer_prijsrange(laag, hoog, "€", " (leden-tarief, 1 dag t/m hele congres)")
                                break
                    except requests.RequestException:
                        pass
                    entries.append({
                        "id": f"nva-anesthesiologendagen-{huidig_jaar}",
                        "naam": naam,
                        "organisatie": "NVA (Nederlandse Vereniging voor Anesthesiologie)",
                        "land": "Nederland",
                        "stad": locatie or "Nog niet bekend",
                        "datumStart": datum_start,
                        "datumEind": datum_eind,
                        "onderwerp": ["algemene anesthesiologie"],
                        "kosten": kosten,
                        "bron": url,
                    })
            i += 2
            continue
        i += 1

    if not entries:
        warn("NVA", f"geen 'Anesthesiologendagen' gevonden op {url} -- pagina-structuur mogelijk gewijzigd.")
    return entries


def espa_volledige_registratie(regels):
    """De ESPA-tarieftabel heeft kolommen "Early/Late/On-site registration"
    gevolgd door "One Day Registration for ..."; per rij (ESPA Member,
    ESPA Non-Member, Reduced Fee) staan de bedragen in die kolomvolgorde.
    Geeft de range van de niet-lid-tarieven voor het volledige congres terug
    (dagkaarten niet meegerekend), als (laagste, hoogste, muntteken)."""
    try:
        kop = next(i for i, r in enumerate(regels) if re.fullmatch(r"Registration fees", r, re.I))
        lid = next(i for i in range(kop, len(regels)) if re.fullmatch(r"ESPA Member", regels[i], re.I))
        niet_lid = next(i for i in range(lid, len(regels)) if re.fullmatch(r"ESPA Non-Member", regels[i], re.I))
    except StopIteration:
        return None
    kolommen = [r for r in regels[kop + 1:lid] if re.search(r"registration", r, re.I)]
    aantal_volledig = sum(1 for k in kolommen if not re.match(r"One Day", k, re.I))
    if not aantal_volledig:
        return None
    bedragen = []
    for regel in regels[niet_lid + 1:]:
        m = PRIJS_RE.fullmatch(regel)
        if not m:
            break
        bedragen.append(_prijs_uit_match(m))
    volledig = bedragen[:aantal_volledig]
    if len(volledig) < aantal_volledig:
        return None
    waarden = [b for _, b in volledig]
    return min(waarden), max(waarden), volledig[0][0]


def scrape_espa():
    """ESPA (European Society for Paediatric Anaesthesiology): de jaarlijkse
    congressite toont de actuele editie in een titelregel ("16th European
    Congress for Paediatric Anaesthesiology, Madrid, Spain 24/09/2026 -
    26/09/2026") of, rond het congres, alleen in het welkomstwoord van de
    president ("... 16th European Congress for Paediatric Anaesthesiology
    taking place on 24–26 September 2026 in Madrid, Spain."). Toekomstige
    edities staan pas op een nieuwe site zodra die gepubliceerd wordt, dus
    verder dan het lopende/eerstvolgende jaar kijkt dit (nog) niet. Staat geen
    van beide op de site (bv. alleen een laadscherm), dan valt dit terug op de
    "Future Events"-widget van de officiele ESPA-site (euroespa.com), die geen
    stad vermeldt."""
    url = "https://www.espacongress.com/"
    try:
        lines = fetch_lines(url)
    except requests.RequestException as e:
        warn("ESPA", f"kon {url} niet ophalen: {e}")
        lines = []

    gevonden = None
    for regel in lines:
        m = re.search(
            r"(\d+)\w{2} European [Cc]ongress for Paediatric Anaesthesiology,\s*"
            r"([A-Za-z .]+),\s*([A-Za-z .]+)\s+(\d{2})/(\d{2})/(20\d{2})\s*-\s*(\d{2})/(\d{2})/(20\d{2})",
            regel,
        )
        if m:
            nummer, stad, land, d1, m1, j1, d2, m2, j2 = m.groups()
            if m1 == m2 and j1 == j2:
                gevonden = (nummer, stad, land, f"{j1}-{m1}-{d1}", f"{j2}-{m2}-{d2}", j1)
                break
        m = re.search(
            r"(\d+)\w{2} European [Cc]ongress for Paediatric Anaesthesiology,? taking place on\s+"
            r"(\d{1,2})\s*[-–]\s*(\d{1,2})\s+([A-Za-z]+)\s+(20\d{2})\s+in\s+([A-Za-z .]+?),\s*([A-Za-z .]+?)\s*[.,]",
            regel,
        )
        if m:
            nummer, d1, d2, maand, jaar, stad, land = m.groups()
            start, eind = maak_datum(jaar, maand, d1), maak_datum(jaar, maand, d2)
            if start and eind:
                gevonden = (nummer, stad, land, start, eind, jaar)
                break

    if gevonden:
        nummer, stad, land, start, eind, jaar = gevonden
        kosten = "Nog niet gepubliceerd"
        try:
            reg_lines = fetch_lines(url + "registration/")
            bereik = espa_volledige_registratie(reg_lines)
            if bereik:
                kosten = formatteer_prijsrange(*bereik[:2], bereik[2], " (niet-lid)")
        except requests.RequestException:
            pass
        return [{
            "id": f"espa-congress-{jaar}",
            "naam": f"{ordinaal(nummer)} European Congress for Paediatric Anaesthesiology",
            "organisatie": "ESPA (European Society for Paediatric Anaesthesiology)",
            "land": vertaal_land(land),
            "stad": stad.strip(),
            "datumStart": start,
            "datumEind": eind,
            "onderwerp": ["kinderanesthesiologie"],
            "kosten": kosten,
            "bron": url,
        }]

    fallback_url = "https://www.euroespa.com/"
    try:
        fb_lines = fetch_lines(fallback_url)
    except requests.RequestException as e:
        warn("ESPA", f"kon {url} niet parsen en {fallback_url} niet ophalen: {e}")
        return []

    for i, regel in enumerate(fb_lines):
        m = re.fullmatch(r"The (\d+)\w{2} ESPA Congress", regel)
        if m and i + 1 < len(fb_lines):
            md = re.fullmatch(r"([A-Za-z]+) (\d{1,2})\s*-\s*(\d{1,2}),?\s*(20\d{2})", fb_lines[i + 1])
            if md:
                maand, d1, d2, jaar = md.groups()
                return [{
                    "id": f"espa-congress-{jaar}",
                    "naam": f"{ordinaal(m.group(1))} European Congress for Paediatric Anaesthesiology",
                    "organisatie": "ESPA (European Society for Paediatric Anaesthesiology)",
                    "land": "Onbekend",
                    "stad": "Nog niet bekend",
                    "datumStart": maak_datum(jaar, maand, d1),
                    "datumEind": maak_datum(jaar, maand, d2),
                    "onderwerp": ["kinderanesthesiologie"],
                    "kosten": "Nog niet gepubliceerd",
                    "bron": fallback_url,
                    "letOp": f"Stad/land niet gevonden -- {url} toonde een laadscherm i.p.v. de congrespagina, dit komt van de terugval-bron. Controleer handmatig.",
                    "letOpType": "data",
                }]

    warn("ESPA", f"geen congresregel gevonden/gewijzigd op {url} of {fallback_url}.")
    return []


def maak_entry(id_, naam, organisatie, land, stad, start, eind, onderwerp, bron, let_op=None, kosten=None, let_op_type="data"):
    entry = {
        "id": id_, "naam": naam, "organisatie": organisatie, "land": land,
        "stad": stad, "datumStart": start, "datumEind": eind,
        "onderwerp": onderwerp, "kosten": kosten or "Nog niet gepubliceerd", "bron": bron,
    }
    if let_op:
        entry["letOp"] = let_op
        entry["letOpType"] = let_op_type
    return entry


def scrape_efic():
    """EFIC (European Pain Federation): elke tweejaarlijkse editie heeft een eigen
    pagina europeanpainfederation.eu/efic<jaar>/. We proberen de komende jaren."""
    entries = []
    dit_jaar = datetime.date.today().year
    for jaar in range(dit_jaar, dit_jaar + 6):
        url = f"https://europeanpainfederation.eu/efic{jaar}/"
        try:
            lines = fetch_lines_optional(url)
        except requests.RequestException as e:
            warn("EFIC", f"kon {url} niet ophalen: {e}")
            continue
        if not lines:
            continue
        stad = datum = None
        for regel in lines:
            m = re.match(rf"EFIC Congress {jaar} - (.+?), ([A-Za-z .]+)$", regel)
            if m and not stad:
                stad = m.group(2).strip()
            m = re.fullmatch(r"(\d{1,2}) to (\d{1,2}) ([A-Za-z]+) (20\d{2})", regel)
            if m and not datum and m.group(4) == str(jaar):
                datum = (maak_datum(jaar, m.group(3), m.group(1)), maak_datum(jaar, m.group(3), m.group(2)))
        if stad and datum and datum[0]:
            land = "Verenigd Koninkrijk" if stad.lower() == "glasgow" else "Onbekend"
            kosten = None
            try:
                reg_lines = fetch_lines(url + "registration/")
                bereik = vind_prijsrange_tussen(reg_lines, r"^Non-Member$", r"^Supported Countries$")
                if bereik:
                    kosten = formatteer_prijsrange(*bereik[:2], bereik[2], " (niet-lid)")
            except requests.RequestException:
                pass
            entries.append(maak_entry(
                f"efic-{jaar}", f"EFIC Congress {jaar} (Pain in Europe)",
                "EFIC (European Pain Federation)", land, stad, datum[0], datum[1],
                ["pijngeneeskunde"], url,
                None if land != "Onbekend" else "Land niet automatisch bepaald, aanvullen.",
                kosten=kosten,
            ))
        else:
            warn("EFIC", f"pagina {url} bestaat maar stad/datum niet gevonden.")
    return entries


def scrape_wca():
    """World Congress of Anaesthesiologists (WFSA): overzichtspagina met de
    komende edities, o.a. '20th WCA 2028 – Vancouver, Canada, 7-10 May 2028'."""
    url = "https://wfsahq.org/our-work/world-congress/"
    try:
        lines = fetch_lines(url)
    except requests.RequestException as e:
        warn("WCA", f"kon {url} niet ophalen: {e}")
        return []
    entries = []
    for regel in lines:
        m = re.match(
            r"(\d+)\w{2} WCA (20\d{2}) [–-] ([^,]+), ([^,]+), (\d{1,2})[-–](\d{1,2}) ([A-Za-z]+) (20\d{2})", regel
        )
        if m:
            nr, jaar, stad, land, d1, d2, maand, _ = m.groups()
            entries.append(maak_entry(
                f"wca-{jaar}", f"{ordinaal(nr)} World Congress of Anaesthesiologists (WCA {jaar})",
                "WFSA (World Federation of Societies of Anaesthesiologists)", vertaal_land(land),
                stad.strip(), maak_datum(jaar, maand, d1), maak_datum(jaar, maand, d2),
                ["algemene anesthesiologie"], url,
            ))
        else:
            m = re.match(r"(\d+)\w{2} WCA [–-] ([A-Za-z ]+), (20\d{2})$", regel)
            if m:
                warn("WCA", f"WCA {m.group(3)} ({m.group(2)}) aangekondigd maar zonder datum -- nog niet toegevoegd.")
    if not entries:
        warn("WCA", f"geen WCA-editie met datum gevonden op {url}.")
    return entries


def scrape_soap():
    """SOAP (Society for Obstetric Anesthesia and Perinatology): 'Future Meetings'."""
    url = "https://www.soap.org/future-meetings"
    try:
        lines = fetch_lines(url)
    except requests.RequestException as e:
        warn("SOAP", f"kon {url} niet ophalen: {e}")
        return []
    entries = []
    for i, regel in enumerate(lines):
        m = re.fullmatch(r"(20\d{2}) (\d+)\w{2} Annual Meeting", regel)
        if not m or i + 3 >= len(lines):
            continue
        jaar, nr = m.groups()
        md = re.fullmatch(r"([A-Za-z]+) (\d{1,2})-(\d{1,2}), (20\d{2})", lines[i + 1])
        if not md or md.group(4) != jaar:
            continue
        venue = lines[i + 2]
        stad, land, let_op = None, "Verenigde Staten", None
        mc = re.fullmatch(r"([A-Za-z .]+), ([A-Za-z .]+)", lines[i + 3])
        if mc:
            stad, land = mc.group(1).strip(), vertaal_land(mc.group(2))
        else:
            for extra in lines[i + 3:i + 8]:
                ma = re.search(r"activities in ([A-Za-z .]+?) -", extra)
                if ma:
                    stad = ma.group(1).strip()
                    let_op = f"Stad afgeleid uit de bron; exacte locatie: {venue}."
                    break
        if stad:
            entries.append(maak_entry(
                f"soap-{jaar}", f"SOAP {ordinaal(nr)} Annual Meeting",
                "SOAP (Society for Obstetric Anesthesia and Perinatology)", land, stad,
                maak_datum(jaar, md.group(1), md.group(2)), maak_datum(jaar, md.group(1), md.group(3)),
                ["obstetrische anesthesie"], url, let_op,
            ))
    if not entries:
        warn("SOAP", f"geen Annual Meeting gevonden op {url}.")
    return entries


def scrape_winter_pain_symposium():
    """London Pain Forum: Advances in Pain Medicine International Winter Symposium."""
    url = "https://www.winterpainsymposium.com/"
    try:
        lines = fetch_lines(url)
    except requests.RequestException as e:
        warn("Winter Pain Symposium", f"kon {url} niet ophalen: {e}")
        return []
    for regel in lines:
        m = re.match(
            r"(\d{1,2})-(\d{1,2}) ([A-Za-z]{3}) (20\d{2}) - (\d+)\w{2} (Advances in Pain Medicine Winter Symposium), ([^,]+), (.+)$",
            regel,
        )
        if m:
            d1, d2, maand, jaar, nr, naam, stad, regio = m.groups()
            kosten = None
            for regel2 in lines:
                pm = re.search(r"Early Bird Registration Fee:\s*([€£$])\s?([\d.]+)", regel2)
                if pm:
                    kosten = f"Vanaf {pm.group(1)}{int(float(pm.group(2)))} (excl. verblijf)"
                    break
            return [maak_entry(
                f"winter-pain-symposium-{jaar}", f"{ordinaal(nr)} {naam}",
                "London Pain Forum", "Frankrijk" if "french" in regio.lower() else regio, stad.strip(),
                maak_datum(jaar, maand, d1), maak_datum(jaar, maand, d2),
                ["pijngeneeskunde"], url, kosten=kosten,
            )]
    warn("Winter Pain Symposium", f"geen symposiumregel gevonden op {url}.")
    return []


def scrape_nysora():
    """NYSORA-conferenties in Europa/Noord-Amerika (workshops en boot camps
    worden niet meegenomen, alleen de conferenties)."""
    url = "https://nysora.com/events/conferences"
    try:
        lines = fetch_lines(url)
    except requests.RequestException as e:
        warn("NYSORA", f"kon {url} niet ophalen: {e}")
        return []
    entries = []
    for i, regel in enumerate(lines):
        m = re.fullmatch(
            r"([^|]+), ([^,|]+) \| ([A-Za-z]{3}) (\d{1,2})(?: - ([A-Za-z]{3}) (\d{1,2}))?, (20\d{2})", regel
        )
        if not m or i == 0:
            continue
        stad, land, m1, d1, m2, d2, jaar = m.groups()
        if land.strip().lower() not in SCOPE_LANDEN:
            continue
        titel = lines[i - 1]
        start = maak_datum(jaar, m1, d1)
        eind = maak_datum(jaar, m2 or m1, d2 or d1)
        slug = re.sub(r"[^a-z0-9]+", "-", stad.lower()).strip("-")
        entries.append(maak_entry(
            f"nysora-{slug}-{jaar}", f"NYSORA: {titel}", "NYSORA", vertaal_land(land),
            stad.strip(), start, eind, ["regionale anesthesie", "pijngeneeskunde"], url,
        ))
    if not entries:
        warn("NYSORA", f"geen conferenties in Europa/Noord-Amerika gevonden op {url}.")
    return entries


def scrape_bapa():
    """BAPA (Belgian Association for Paediatric Anaesthesiology): jaarlijkse Annual Scientific Meeting."""
    url = "https://www.bapanaesth.be/events/"
    try:
        lines = fetch_lines(url)
    except requests.RequestException as e:
        warn("BAPA", f"kon {url} niet ophalen: {e}")
        return []
    entries, gezien = [], set()
    for i, regel in enumerate(lines):
        if not regel.startswith("BAPA Annual Scientific Meeting"):
            continue
        for j in range(i + 1, min(i + 4, len(lines))):
            m = re.fullmatch(r"([A-Za-z]+) (\d{1,2}), (20\d{2})", lines[j])
            if m and j + 2 < len(lines):
                maand, dag, jaar = m.groups()
                if jaar in gezien:
                    break
                gezien.add(jaar)
                locatie = lines[j + 2]
                stad = re.sub(r"^UZ\s+", "", locatie.split(" - ")[0]).strip()
                datum = maak_datum(jaar, maand, dag)
                entries.append(maak_entry(
                    f"bapa-annual-{jaar}", f"BAPA Annual Scientific Meeting {jaar}",
                    "BAPA (Belgian Association for Paediatric Anaesthesiology)", "België", stad,
                    datum, datum, ["kinderanesthesiologie"], url,
                ))
                break
    if not entries:
        warn("BAPA", f"geen Annual Scientific Meeting gevonden op {url}.")
    return entries


def scrape_association_of_anaesthetists():
    """Association of Anaesthetists (GB & Ierland): alleen de items van het type
    'Conference' uit hun evenementenlijst (dus geen cursussen of webinars)."""
    url = "https://anaesthetists.org/CPD-and-events/Book-an-event"
    try:
        lines = fetch_lines(url)
    except requests.RequestException as e:
        warn("Association of Anaesthetists", f"kon {url} niet ophalen: {e}")
        return []
    entries = []
    for i, regel in enumerate(lines):
        if regel not in ("Conference", "Hybrid Conference") or i + 3 >= len(lines):
            continue
        m = re.match(r"\w+ (\d{1,2}) ?- \w+ (\d{1,2}) ([A-Za-z]+) (20\d{2})$", lines[i + 1])
        if not m:
            continue
        d1, d2, maand, jaar = m.groups()
        naam, stad = lines[i + 2], lines[i + 3]
        slug = re.sub(r"[^a-z0-9]+", "-", naam.lower()).strip("-")
        entries.append(maak_entry(
            f"association-of-anaesthetists-{slug}", naam,
            "Association of Anaesthetists (GB & Ierland)", "Verenigd Koninkrijk", stad,
            maak_datum(jaar, maand, d1), maak_datum(jaar, maand, d2),
            ["algemene anesthesiologie"], url,
        ))
    if not entries:
        warn("Association of Anaesthetists", f"geen conferenties gevonden op {url}.")
    return entries


def scrape_spa():
    """SPA (Society for Pediatric Anesthesia): 'Future Meetings' met de Annual
    Meeting en de gezamenlijke SPA-AAP-bijeenkomst (ook buiten Europa)."""
    url = "https://pedsanesthesia.org/education-and-meetings/upcoming-meetings/"
    try:
        lines = fetch_lines(url)
    except requests.RequestException as e:
        warn("SPA", f"kon {url} niet ophalen: {e}")
        return []
    entries = []
    for i, regel in enumerate(lines):
        m = re.fullmatch(r"SPA (\d+)\w{2} Annual Meeting", regel) or re.fullmatch(
            r"(SPA-AAP Pediatric Anesthesiology) (20\d{2})", regel
        )
        if not m or i + 3 >= len(lines):
            continue
        md = re.fullmatch(r"([A-Za-z]+) (\d{1,2})(?:-(\d{1,2}))?, ?(20\d{2})", lines[i + 1])
        if not md:
            continue
        maand, d1, d2, jaar = md.groups()
        stad = land = None
        for extra in lines[i + 2:i + 4]:
            mc = re.fullmatch(r"([A-Za-z .]+), ([A-Za-z .]+)", extra)
            if mc:
                stad = mc.group(1).strip()
                land = "Verenigde Staten" if re.fullmatch(r"[A-Z]{2}", mc.group(2)) else vertaal_land(mc.group(2))
                break
        if not stad:
            continue
        if "Annual Meeting" in regel:
            naam, id_ = f"SPA {ordinaal(m.group(1))} Annual Meeting", f"spa-annual-{jaar}"
        else:
            naam, id_ = f"SPA-AAP Pediatric Anesthesiology {jaar}", f"spa-aap-{jaar}"
        entries.append(maak_entry(
            id_, naam, "SPA (Society for Pediatric Anesthesia)", land, stad,
            maak_datum(jaar, maand, d1), maak_datum(jaar, maand, d2 or d1),
            ["kinderanesthesiologie"], url,
        ))
    if not entries:
        warn("SPA", f"geen meetings gevonden op {url}.")
    return entries


SCRAPERS = [
    scrape_euroanaesthesia, scrape_esra_congress, scrape_painweek, scrape_asra,
    scrape_nva_anesthesiologendagen, scrape_espa, scrape_efic, scrape_wca, scrape_soap,
    scrape_winter_pain_symposium, scrape_nysora, scrape_bapa, scrape_association_of_anaesthetists, scrape_spa,
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
        if "letOpType" in entry:
            velden.append("letOpType")
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
//   ESRA, PAINWeek, ASRA, NVA, ESPA, EFIC, WCA, SOAP, NYSORA, BAPA, Association
//   of Anaesthetists, London Pain Forum, SPA); zie het bron-veld per congres.
// - Congressen die niet automatisch te scrapen zijn (geblokkeerd door de
//   site, of expliciet verboden in de sitevoorwaarden) staan handmatig in
//   data/congressen.manual.json en worden hier ongewijzigd overgenomen.
// - Afgelopen congressen blijven staan als archief (vorige edities), ook als
//   de bron ze niet meer toont.
// - Kosten zijn vaak nog niet gepubliceerd zo ver van tevoren -- "Nog niet
//   gepubliceerd" betekent dus niet dat het gratis is.
"""


def archief(geziene_ids):
    """Afgelopen congressen die de bronnen niet meer tonen, blijven staan: de site laat
    ze zien als vorige editie (en gebruikt hun kosten/punten als indicatie voor de
    volgende). Alleen edities waarvan de einddatum voorbij is; een toekomstig congres
    dat uit de bron verdwijnt, verdwijnt hier dus ook (bv. geannuleerd of verplaatst)."""
    if not DATA_FILE.exists():
        return []
    vandaag = datetime.date.today().isoformat()
    return [e for e in lees_js_data(DATA_FILE, "CONGRESSEN")
            if e["id"] not in geziene_ids and e["datumEind"] < vandaag]


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
    alle_entries = []
    geziene_ids = set()
    for entry in gescraped + handmatig:
        if entry["id"] in geziene_ids:
            warn(entry["id"], "dubbele id gevonden (bron toonde dezelfde editie waarschijnlijk twee keer op de pagina) -- tweede exemplaar overgeslagen.")
            continue
        geziene_ids.add(entry["id"])
        alle_entries.append(entry)

    if not alle_entries:
        print("Geen enkele bron leverde data op, bestaand data/congressen.js blijft ongewijzigd.", file=sys.stderr)
        return 1

    alle_entries.extend(archief(geziene_ids))

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
