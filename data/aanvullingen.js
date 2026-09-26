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
// - deadlines: lijst van { soort, datum, bron, gecontroleerd }. soort is "early-bird" (laatste dag
//   van het goedkopere tarief), "abstracts" (laatste dag abstracts indienen), "registratie" (laatste
//   dag inschrijven) of "annuleren" (laatste dag annuleren met (gedeeltelijke) terugbetaling).
//   datum = de laatste dag die zeker nog telt: "vóór 13 dec" wordt dus 12 dec, "sluit 19 nov 7:45"
//   wordt 18 nov. Alleen letterlijk bij de organisator gevonden datums; verlopen deadlines mogen weg.
//   De site toont alleen komende deadlines; ze komen ook in de agenda-feed (agenda.ics).
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
    deadlines: [
      { soort: "annuleren", datum: "2026-09-27", bron: "https://esraeurope.org/meeting/1st-esra-pocus-workshop/", gecontroleerd: "2026-09-26" }
    ],
    gecontroleerd: "2026-09-25"
  },
  "bapa-annual-2026": {
    kosten: "€125–€220 (aios/verpleegkundige lid t/m specialist niet-lid)",
    kostenBron: "https://www.bapanaesth.be/events/bapa-annual-scientific-meeting-21st-of-november-2026/",
    deadlines: [
      { soort: "registratie", datum: "2026-11-18", bron: "https://www.bapanaesth.be/events/bapa-annual-scientific-meeting-21st-of-november-2026/", gecontroleerd: "2026-09-26" }
    ],
    gecontroleerd: "2026-09-25"
  },
  "esra-instructor-course-2026": {
    kosten: "€875 (alleen voor ESRA-leden)",
    kostenBron: "https://esraeurope.org/meeting/7th-esra-instructor-course/",
    deadlines: [
      { soort: "annuleren", datum: "2026-10-08", bron: "https://esraeurope.org/meeting/7th-esra-instructor-course/", gecontroleerd: "2026-09-26" }
    ],
    gecontroleerd: "2026-09-25"
  },
  "pga-80-2026": {
    kosten: "Niet-lid arts $995 ($895 bij inschrijving vóór 30 sep) · resident $175–$225, zie bron",
    kostenBron: "https://www.pga.nyc/registration--session-fees.html",
    punten: "max. 39,25 AMA PRA Category 1",
    puntenBron: "https://www.pga.nyc/faqs.html",
    deadlines: [
      { soort: "early-bird", datum: "2026-09-29", bron: "https://www.pga.nyc/registration--session-fees.html", gecontroleerd: "2026-09-26" },
      { soort: "annuleren", datum: "2026-09-30", bron: "https://www.pga.nyc/registration--session-fees.html", gecontroleerd: "2026-09-26" }
    ],
    gecontroleerd: "2026-09-25"
  },
  "nysora-kitzb-hel-2027": {
    kosten: "€1.075 (early bird, inschrijven vóór 13 dec 2026) · daarna €1.175",
    kostenBron: "https://nysora.com/event/conferences/update-on-regional-anesthesia-and-pain-management-including-hands-on-scanning-practice/",
    deadlines: [
      { soort: "early-bird", datum: "2026-12-12", bron: "https://nysora.com/event/conferences/update-on-regional-anesthesia-and-pain-management-including-hands-on-scanning-practice/", gecontroleerd: "2026-09-26" }
    ],
    gecontroleerd: "2026-09-25"
  },
  "association-of-anaesthetists-winter-scientific-meeting-2027": {
    kosten: "Lid £220–£610 (online/fysiek, 1–2 dagen) · niet-lid £750–£1.025",
    kostenBron: "https://anaesthetists.org/Home/Education-events/Winter-Scientific-Meeting/How-to-book",
    deadlines: [
      { soort: "early-bird", datum: "2026-12-03", bron: "https://anaesthetists.org/Home/Education-events/Winter-Scientific-Meeting/How-to-book", gecontroleerd: "2026-09-26" },
      { soort: "annuleren", datum: "2026-12-15", bron: "https://anaesthetists.org/Home/Education-events/Winter-Scientific-Meeting/How-to-book", gecontroleerd: "2026-09-26" }
    ],
    gecontroleerd: "2026-09-25"
  },
  "nans-annual-2027": {
    puntenIndicatie: "2026: max. 23,5 AMA PRA Category 1",
    puntenBron: "https://www.nans.org/cmeaccreditation/",
    deadlines: [
      { soort: "early-bird", datum: "2026-10-27", bron: "https://www.nans.org/annual-meeting.html", gecontroleerd: "2026-09-26" }
    ],
    gecontroleerd: "2026-09-25"
  },
  "nysora-val-d-isere-2027": {
    kosten: "€1.075 (early bird, inschrijven vóór 8 jan 2027) · daarna €1.175",
    kostenBron: "https://nysora.com/event/conferences/anesthesia-review-conference-valdisere-2027/",
    deadlines: [
      { soort: "early-bird", datum: "2027-01-07", bron: "https://nysora.com/event/conferences/anesthesia-review-conference-valdisere-2027/", gecontroleerd: "2026-09-26" }
    ],
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
    deadlines: [
      { soort: "abstracts", datum: "2026-11-11", bron: "https://painconnect.org/", gecontroleerd: "2026-09-26" }
    ],
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
    deadlines: [
      { soort: "abstracts", datum: "2026-09-30", bron: "https://europeanpainfederation.eu/efic2027/", gecontroleerd: "2026-09-26" },
      { soort: "early-bird", datum: "2026-12-14", bron: "https://europeanpainfederation.eu/efic2027/", gecontroleerd: "2026-09-26" },
      { soort: "registratie", datum: "2027-03-22", bron: "https://europeanpainfederation.eu/efic2027/", gecontroleerd: "2026-09-26" }
    ],
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
  },
  "espa-congress-2026": {
    kosten: "€330–€880 (trainee t/m niet-lid, incl. btw) · verpleegkundige/student €180",
    kostenBron: "https://www.espacongress.com/registration/",
    gecontroleerd: "2026-09-25"
  },
  "esra-winter-week-conference-2027": {
    kostenIndicatie: "2026: €830–€1.160 (trainee-lid t/m niet-lid)",
    kostenBron: "https://esraeurope.org/meeting/20th-esra-winter-week-conference/",
    puntenIndicatie: "2026: 20 ECMEC (EACCME)",
    puntenBron: "https://esraeurope.org/meeting/20th-esra-winter-week-conference/",
    gecontroleerd: "2026-09-25"
  },
  "esra-pain-cadaver-workshop-2027": {
    kostenIndicatie: "2026: €630–€930 (combi met RA-workshop €1.055–€1.655)",
    kostenBron: "https://esraeurope.org/meeting/15th-esra-pain-cadaver-workshop/",
    puntenIndicatie: "2026: 9 ECMEC (EACCME)",
    puntenBron: "https://esraeurope.org/meeting/15th-esra-pain-cadaver-workshop/",
    gecontroleerd: "2026-09-25"
  },
  "esra-ra-cadaver-workshop-2027": {
    kostenIndicatie: "2026: €695–€995 (trainee-lid t/m niet-lid)",
    kostenBron: "https://esraeurope.org/meeting/39th-esra-ra-cadaver-workshop/",
    puntenIndicatie: "2026: 15,5 ECMEC (EACCME)",
    puntenBron: "https://esraeurope.org/meeting/39th-esra-ra-cadaver-workshop/",
    gecontroleerd: "2026-09-25"
  },
  "esra-residents-trainees-workshop-2027": {
    kostenIndicatie: "2026: €350 (trainee-lid) / €680 (lid)",
    kostenBron: "https://esraeurope.org/meeting/8th-esra-residents-trainees-workshop/",
    puntenIndicatie: "2026: 14 ECMEC (EACCME)",
    puntenBron: "https://esraeurope.org/meeting/8th-esra-residents-trainees-workshop/",
    gecontroleerd: "2026-09-25"
  },
  "asra-regional-2027": {
    kostenIndicatie: "2026: lid $940–$1.175, niet-lid $1.440–$1.745 (fysiek); livestream $150–$475",
    kostenBron: "https://asra.com/events-education/past-events/past-ra-acute-pain-medicine-meetings/51st-annual-regional-anesthesiology-and-acute-pain-medicine-meeting/register",
    puntenIndicatie: "2026: max. 21,75 AMA PRA Category 1",
    puntenBron: "https://asra.com/events-education/past-events/past-ra-acute-pain-medicine-meetings/51st-annual-regional-anesthesiology-and-acute-pain-medicine-meeting/cme-cpd",
    gecontroleerd: "2026-09-25"
  },
  "esra-congress-2027": {
    puntenIndicatie: "2026: max. 20,5 ECMEC (EACCME)",
    puntenBron: "https://esracongress.com/cme-accreditation/",
    gecontroleerd: "2026-09-25"
  },
  "nva-anesthesiologendagen-2028": {
    kostenIndicatie: "2026: lid €435 (hele congres) / €320 (1 dag); aios €305 / €240",
    kostenBron: "https://www.anesthesiologie.nl/agenda/anesthesiologendagen-2026/",
    gecontroleerd: "2026-09-25"
  },
  "euroanaesthesia-2027": {
    deadlines: [
      { soort: "abstracts", datum: "2026-12-05", bron: "https://euroanaesthesia.org/2027/abstracts/", gecontroleerd: "2026-09-26" }
    ]
  }
};
