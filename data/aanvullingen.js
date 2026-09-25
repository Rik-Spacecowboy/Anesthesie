// Handmatige aanvullingen op data/congressen.js, per congres-id. Dit bestand wordt NIET door de
// scraper gegenereerd; bewerk het met de hand (of laat Claude het doen).
//
// Velden (allemaal optioneel):
// - kosten / kostenBron: deelnamekosten die de scraper niet vindt. Vindt de scraper later zelf
//   een prijs, dan wint die (die is actueler).
// - punten / puntenBron: nascholingspunten, met soort erbij, bv. "18 ECMEC (EACCME)" of
//   "max. 23 AMA PRA Category 1".
// - kostenIndicatie / puntenIndicatie: alleen nodig als de vorige editie niet (meer) in de
//   dataset staat; anders berekent de pagina de indicatie zelf uit de vorige editie.
// - gecontroleerd: datum waarop de gegevens bij de bron zijn nagekeken.
//
// ASA en NWAS verbieden in hun voorwaarden AI/geautomatiseerd verzamelen: die vult Rik zelf in.

const AANVULLINGEN = {
  "euroanaesthesia-2026": {
    punten: "18 ECMEC (EACCME)",
    puntenBron: "https://euroanaesthesia.org/2026/congress-information/",
    gecontroleerd: "2026-09-25"
  },
  "painweek-2027": {
    puntenIndicatie: "2026: max. 23 AMA PRA Category 1",
    puntenBron: "https://conference.painweek.org/",
    gecontroleerd: "2026-09-25"
  },
  "spa-annual-2026": {
    punten: "max. 7,25 AMA PRA Category 1 (+ losse workshops)",
    puntenBron: "https://www2.pedsanesthesia.org/meetings/2026annual/guide/info/general.iphtml",
    gecontroleerd: "2026-09-25"
  }
};
