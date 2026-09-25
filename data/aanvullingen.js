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
  },
  "esra-sunny-autumn-meeting-2026": {
    kosten: "€730–€1.070 (trainee-lid t/m niet-lid, incl. diners/lunches)",
    kostenBron: "https://esraeurope.org/meeting/10th-esra-sunny-autumn-meeting/",
    gecontroleerd: "2026-09-25"
  },
  "esra-eastern-european-cadaver-workshop-2026": {
    kosten: "€385–€835 (Oost-Europees lid t/m niet-lid elders) · volgeboekt",
    kostenBron: "https://esraeurope.org/meeting/xxiii-esra-eastern-european-cadaver-workshop/",
    punten: "14,5 ESRA-DRA (voor EDRA-diploma; geen ECMEC)",
    puntenBron: "https://esraeurope.org/meeting/xxiii-esra-eastern-european-cadaver-workshop/",
    gecontroleerd: "2026-09-25"
  },
  "asra-pain-medicine-2026": {
    punten: "max. 24,25 AMA PRA Category 1 (ook EACCME-erkend)",
    puntenBron: "https://asra.com/events-education/pain-medicine-meeting/cme-cpd",
    gecontroleerd: "2026-09-25"
  },
  "esra-pocus-workshop-2026": {
    kosten: "€695–€995 (trainee-lid t/m niet-lid) · volgeboekt",
    kostenBron: "https://esraeurope.org/meeting/1st-esra-pocus-workshop/",
    gecontroleerd: "2026-09-25"
  },
  "bapa-annual-2026": {
    kosten: "€125–€220 (aios/verpleegkundige lid t/m specialist niet-lid)",
    kostenBron: "https://www.bapanaesth.be/events/bapa-annual-scientific-meeting-21st-of-november-2026/",
    gecontroleerd: "2026-09-25"
  },
  "esra-instructor-course-2026": {
    kosten: "€875 (alleen voor ESRA-leden)",
    kostenBron: "https://esraeurope.org/meeting/7th-esra-instructor-course/",
    gecontroleerd: "2026-09-25"
  },
  "pga-80-2026": {
    kosten: "Niet-lid arts $995 (was $895 t/m 30 sep) · resident $175–$225, zie bron",
    kostenBron: "https://www.pga.nyc/registration--session-fees.html",
    gecontroleerd: "2026-09-25"
  },
  "nysora-kitzb-hel-2027": {
    kosten: "€1.075 (early bird t/m 13 dec 2026), daarna €1.175",
    kostenBron: "https://nysora.com/event/conferences/update-on-regional-anesthesia-and-pain-management-including-hands-on-scanning-practice/",
    gecontroleerd: "2026-09-25"
  },
  "association-of-anaesthetists-winter-scientific-meeting-2027": {
    kosten: "Lid £220–£610 (online/fysiek, 1–2 dagen) · niet-lid £750–£1.025",
    kostenBron: "https://anaesthetists.org/Home/Education-events/Winter-Scientific-Meeting/How-to-book",
    gecontroleerd: "2026-09-25"
  },
  "nans-annual-2027": {
    puntenIndicatie: "2026: max. 23,5 AMA PRA Category 1",
    puntenBron: "https://www.nans.org/cmeaccreditation/",
    gecontroleerd: "2026-09-25"
  },
  "nysora-val-d-isere-2027": {
    kosten: "€1.075 (early bird t/m 8 jan 2027), daarna €1.175",
    kostenBron: "https://nysora.com/event/conferences/anesthesia-review-conference-valdisere-2027/",
    gecontroleerd: "2026-09-25"
  },
  "nysora-leuven-2027": {
    kosten: "€695 (early bird)",
    kostenBron: "https://nysora.com/event/conferences/leuven-masterclass-ultrasound-guided-joint-interventions-denervation-2027/",
    gecontroleerd: "2026-09-25"
  },
  "aapm-painconnect-2027": {
    puntenIndicatie: "2025: 24,5 CME",
    puntenBron: "https://painconnect.org/about-painconnect/",
    gecontroleerd: "2026-09-25"
  },
  "icsa-2027": {
    punten: "16+ CPD (volgens organisator; accrediterende instantie niet vermeld)",
    puntenBron: "https://surgery.inovineconferences.com/",
    gecontroleerd: "2026-09-25"
  },
  "efic-2027": {
    puntenIndicatie: "2025: 24 ECMEC (EACCME)",
    puntenBron: "https://europeanpainfederation.eu/news/efic2025-has-received-24-eaccme-credits/",
    gecontroleerd: "2026-09-25"
  },
  "nva-anesthesiologendagen-2027": {
    kostenIndicatie: "2026: lid €435 (hele congres) / €320 (1 dag); aios €305 / €240",
    kostenBron: "https://www.anesthesiologie.nl/agenda/anesthesiologendagen-2026/",
    gecontroleerd: "2026-09-25"
  },
  "association-of-anaesthetists-gasfest-2027": {
    punten: "5 CPD per dag",
    puntenBron: "https://anaesthetists.org/Events/Event-Details.aspx?eventDateId=1076",
    gecontroleerd: "2026-09-25"
  }
};
