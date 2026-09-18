// Congresdataset. Dit bestand wordt automatisch gegenereerd door
// scripts/scrape_congressen.py -- pas het dus niet direct handmatig aan.
//
// - Automatisch gescrapete congressen komen uit de bekende bronnen (ESAIC,
//   ESRA, PAINWeek, ASRA, NVA, ESPA); zie het bron-veld per congres.
// - Congressen die niet automatisch te scrapen zijn (geblokkeerd door de
//   site, of expliciet verboden in de sitevoorwaarden) staan handmatig in
//   data/congressen.manual.json en worden hier ongewijzigd overgenomen.
// - Kosten zijn vaak nog niet gepubliceerd zo ver van tevoren -- "Nog niet
//   gepubliceerd" betekent dus niet dat het gratis is.

const CONGRESSEN = [
  {
    id: "espa-congress-2026",
    naam: "16th European Congress for Paediatric Anaesthesiology",
    organisatie: "ESPA (European Society for Paediatric Anaesthesiology)",
    land: "Spanje",
    stad: "Madrid",
    datumStart: "2026-09-24",
    datumEind: "2026-09-26",
    onderwerp: ["kinderanesthesiologie"],
    kosten: "Nog niet gepubliceerd",
    bron: "https://www.espacongress.com/"
  },
  {
    id: "asa-anesthesiology-2026",
    naam: "ANESTHESIOLOGY 2026 (ASA Annual Meeting)",
    organisatie: "American Society of Anesthesiologists (ASA)",
    land: "Verenigde Staten",
    stad: "San Diego",
    datumStart: "2026-10-16",
    datumEind: "2026-10-20",
    onderwerp: ["algemene anesthesiologie"],
    kosten: "Nog niet gepubliceerd",
    bron: "https://www.asahq.org/annualmeeting",
    letOp: "Niet automatisch gescraped: apsf.org (oude bron) blokkeert scrapers en asahq.org verbiedt in de site-voorwaarden expliciet gebruik van hun content met AI/automatisering. Handmatig controleren en bijwerken."
  },
  {
    id: "asra-pain-medicine-2026",
    naam: "25th Annual Pain Medicine Meeting",
    organisatie: "ASRA Pain Medicine",
    land: "Verenigde Staten",
    stad: "Tampa",
    datumStart: "2026-11-05",
    datumEind: "2026-11-07",
    onderwerp: ["pijngeneeskunde"],
    kosten: "Nog niet gepubliceerd",
    bron: "https://asra.com/events-education"
  },
  {
    id: "asra-regional-2027",
    naam: "Annual Regional Anesthesiology and Acute Pain Medicine Meeting",
    organisatie: "ASRA Pain Medicine",
    land: "Verenigde Staten",
    stad: "Houston",
    datumStart: "2027-05-13",
    datumEind: "2027-05-15",
    onderwerp: ["regionale anesthesie", "acute pijn"],
    kosten: "Nog niet gepubliceerd",
    bron: "https://asra.com/events-education",
    letOp: "Automatisch gevonden; ordinal (bv. '52nd') stond niet in de brontekst, controleer de exacte naam."
  },
  {
    id: "nva-anesthesiologendagen-2027",
    naam: "Anesthesiologendagen 2027",
    organisatie: "NVA (Nederlandse Vereniging voor Anesthesiologie)",
    land: "Nederland",
    stad: "Nog niet bekend",
    datumStart: "2027-05-27",
    datumEind: "2027-05-28",
    onderwerp: ["algemene anesthesiologie"],
    kosten: "Nog niet gepubliceerd",
    bron: "https://www.anesthesiologie.nl/agenda/"
  },
  {
    id: "esra-congress-2027",
    naam: "44th ESRA Annual Congress",
    organisatie: "ESRA (European Society of Regional Anaesthesia and Pain Therapy)",
    land: "Italië",
    stad: "Bologna",
    datumStart: "2027-09-01",
    datumEind: "2027-09-04",
    onderwerp: ["regionale anesthesie", "pijntherapie"],
    kosten: "Nog niet gepubliceerd",
    bron: "https://esraeurope.org/meetings/?meeting_type=esra-events"
  },
  {
    id: "painweek-2027",
    naam: "PAINWeek 2027",
    organisatie: "PAINWeek",
    land: "Verenigde Staten",
    stad: "Las Vegas",
    datumStart: "2027-09-07",
    datumEind: "2027-09-10",
    onderwerp: ["pijnmanagement", "multidisciplinair"],
    kosten: "Nog niet gepubliceerd",
    bron: "https://conference.painweek.org/"
  },
  {
    id: "asa-anesthesiology-2027",
    naam: "ANESTHESIOLOGY 2027 (ASA Annual Meeting)",
    organisatie: "American Society of Anesthesiologists (ASA)",
    land: "Verenigde Staten",
    stad: "Boston",
    datumStart: "2027-10-15",
    datumEind: "2027-10-19",
    onderwerp: ["algemene anesthesiologie"],
    kosten: "Nog niet gepubliceerd",
    bron: "https://www.asahq.org/annualmeeting/attend/futuredates",
    letOp: "Niet automatisch gescraped (zie asa-anesthesiology-2026). Datum/stad komt van ASA's eigen 'Future Dates'-pagina; kosten en programma nog niet gepubliceerd."
  },
  {
    id: "nva-anesthesiologendagen-2028",
    naam: "Anesthesiologendagen 2028",
    organisatie: "NVA (Nederlandse Vereniging voor Anesthesiologie)",
    land: "Nederland",
    stad: "Nog niet bekend",
    datumStart: "2028-05-18",
    datumEind: "2028-05-19",
    onderwerp: ["algemene anesthesiologie"],
    kosten: "Nog niet gepubliceerd",
    bron: "https://www.anesthesiologie.nl/agenda/"
  },
  {
    id: "asa-anesthesiology-2028",
    naam: "ANESTHESIOLOGY 2028 (ASA Annual Meeting)",
    organisatie: "American Society of Anesthesiologists (ASA)",
    land: "Verenigde Staten",
    stad: "Chicago",
    datumStart: "2028-10-20",
    datumEind: "2028-10-24",
    onderwerp: ["algemene anesthesiologie"],
    kosten: "Nog niet gepubliceerd",
    bron: "https://www.asahq.org/annualmeeting/attend/futuredates",
    letOp: "Niet automatisch gescraped (zie asa-anesthesiology-2026). Datum/stad komt van ASA's eigen 'Future Dates'-pagina; kosten en programma nog niet gepubliceerd."
  }
];
