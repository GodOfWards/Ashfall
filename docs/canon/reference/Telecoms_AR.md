# Phones and internet when the power fails (#494)

Real-world facts, not canon until a decision adopts them (`../Ashfall_Canon.md`
records what's decided). See `README.md` for the status labels. Researched
2026-10-06 for #494: #479 has survivors stay indoors until the grid fails on
day 21, and whether phones and the internet work through that phase, and for
how long after it, bears on #480 (the writing) and #478 (radios). Carriers,
makers and regulators are named only as sources; none appears in the game.

**What no source gives:** an Argentine carrier's battery or fuel figure for a
named site, any site near Lima, or Cospli's telephone plant. The ranges below
come from carriers' public statements, regulators' rules and other countries'
blackouts.

## Mobile sites: batteries, then generators where there are any

- **The 2019 blackout: Argentine carriers claimed up to 12 hours.
  Secondary.** On 16 June 2019, the day of the blackout (`Grid_AR.md`),
  carriers told Infobae their 3G and 4G antennas ran on "generadores
  eléctricos y 'alimentación de back-up'", with "autonomía de hasta 12
  horas". One carrier said it was "reforzando sitios críticos para dar
  continuidad a la prestación por varias horas".
  [Infobae, 2019-06-16](https://www.infobae.com/sociedad/2019/06/16/pueden-dejar-de-funcionar-los-celulares-por-el-apagon/),
  [Infobae (D. Jaimovich), 2019-06-16](https://www.infobae.com/america/tecno/2019/06/16/apagon-como-funcionan-las-redes-de-telefonia-movil-y-por-que-no-nos-quedamos-sin-senal/),
  read 2026-10-06. La Nación, the same day, had the three carriers giving
  "varias horas" of backup, by UPS batteries and fuel generators, "some up to
  4 hours"
  ([La Nación, 2019-06-16](https://www.lanacion.com.ar/tecnologia/agenda-vida-digital-nid2258073/),
  read 2026-10-06; the 4 hours is the fetch's summary, not read verbatim).
  - **Reading, not fact:** "up to" 12 hours is a ceiling the carriers put
    forward on the day, not a typical site.
- **2013 to 2018: a rule required 24 hours at every mobile site. Confirmed.**
  After the La Plata flood of 2 April 2013, the Secretaría de Comunicaciones'
  **Resolución 1/2013** (5 April 2013) required mobile carriers to keep the
  service running "incluso en situaciones de emergencia o catástrofe", with
  at most one hour's interruption, and to have "en cada uno de los sitios que
  conforman su infraestructura de red sistemas de respaldo de energía con
  autonomía mínima de VEINTICUATRO (24) horas" (art. 2 a). It covered mobile
  only, not fixed lines.
  [Texto original](https://www.argentina.gob.ar/normativa/nacional/norma-210241/texto),
  read 2026-10-06. During the flood itself, the provincial Defensor del
  Pueblo recorded "numerosos reclamos" over one carrier's mobile service in
  La Plata "antes, durante y después del temporal"
  ([Resolución 31/13](https://www.defensorba.org.ar/pdfs/resoluciones/Resolucion-31-13.pdf),
  14 June 2013, read 2026-10-06).
- **Since November 2018: backup required, no hours named. Confirmed.**
  Resolución 51/2018 of the Secretaría de Gobierno de Modernización
  (published 6 November 2018) repealed 1/2013 and approved a Reglamento
  Nacional de Contingencia for mobile carriers. It asks for "sistemas
  alternativos de suministro de energía estratégicamente distribuidos ... con
  autonomía para garantizar el servicio durante una eventual emergencia o
  desastre", network redundancy, and transportable units (radio bases,
  generators) to move into an affected area. It sets **no number of hours**
  and covers mobile only. ENACOM was to issue a contingency plan within 90
  days.
  [Status](https://www.argentina.gob.ar/normativa/nacional/norma-210241),
  [text](https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-51-2018-316087/texto),
  read 2026-10-06. Whether ENACOM issued that plan, and what it says:
  **unconfirmed**.
- **Elsewhere, for scale. Secondary unless marked.**
  - **Spain and Portugal, 28 April 2025.** The power went at 12:33 local
    time and was out about ten hours in Portugal; Spain was back by the next
    day. Base-station batteries were quoted at **2 to 8 hours** (Infobae
    España, 2025-04-29; INESC TEC for Portugal, 2025-05-13). Mobile service
    was at its worst at **18:00 UTC, about 7½ hours after the cut**, with
    "50–100% of users offline as batteries ran out" in many areas (Ookla, via
    Broadband Breakfast, 2025-08-21). One Portuguese carrier that had put
    "at least six hours" behind most sites kept much of its network up; one
    with almost none lost service for more than 90 % of its subscribers for
    over 24 hours. Spain's government put the share of its sites that already
    had four hours of backup at about 30 % (El Español, 2025-12-02), and then
    required four hours of mobile coverage for 75–85 % of the population,
    12 hours for intermediate centres and 24 hours for the most critical.
    [Infobae España](https://www.infobae.com/espana/2025/04/29/asi-afecta-un-apagon-a-las-comunicaciones-por-que-se-cayo-la-red-movil-con-el-corte-de-luz/),
    [INESC TEC](https://inesctec.substack.com/p/the-blackout-that-left-millions-unreachable),
    [Broadband Breakfast](https://broadbandbreakfast.com/iberian-blackout-highlights-gaps-in-telecom-network-resiliency/),
    [Light Reading, 2025-04-29](https://www.lightreading.com/security/spanish-and-portuguese-networks-hit-hard-by-power-outage),
    [El Español](https://www.elespanol.com/invertia/observatorios/digital/20251202/gobierno-obliga-telecos-garantizar-servicio-horas-apagon-cifra-coste-millones/1003744038363_0.html),
    all read 2026-10-06.
  - **The United States after Hurricane Katrina. Confirmed.** The FCC's
    Katrina panel found the industry "generally been diligent in deploying
    backup batteries and generators and ensuring that these systems have one
    to two days of fuel or charge", but not everywhere, and some "did not
    function during the crisis" for want of testing; "generators are
    typically designed to keep base stations operating for 24 to 48 hours".
    Carriers kept "permanent generators at all of the switches and critical
    cell sites" and portable ones to recharge the rest. The FCC then required
    **8 hours at cell sites and 24 hours in central offices** (later
    withdrawn).
    [Federal Register 72:196, 2007-10-11, pp. 57879 ff.](https://www.govinfo.gov/content/pkg/FR-2007-10-11/pdf/E7-20061.pdf),
    read 2026-10-06.

## The core and transport behind a site

- **A site on battery is useless if its switch or backhaul is down.
  Confirmed.** The Katrina panel: "the majority of the adverse effects and
  outages encountered by wireless providers were due to a lack of commercial
  power or a lack of transport connectivity to the wireless switch", and
  carriers named "security for their personnel, access and fuel as the most
  pressing needs". Federal Register, above.
- **Data centres and switching centres: generators, with fuel measured in
  hours to days. Confirmed for the standard.** The Uptime Institute's Tier
  Standard requires **at least 12 hours** of fuel on site at full load, for
  every Tier.
  [Uptime Institute Journal, 2014-06-18](https://journal.uptimeinstitute.com/fuel-system-design-reliability/),
  read 2026-10-06. Fibre transport also has powered repeater and node sites
  along the way (Infobae España, above; secondary).
- **No source gives the fuel autonomy of a carrier's switching centre or data
  centre in Zárate, Campana or Buenos Aires: unconfirmed.** What would
  confirm it: a carrier's sustainability or network report, or a data-centre
  operator's spec sheet.

## Fixed lines in Lima

- **A copper phone line is powered from the exchange. Confirmed.** The FCC:
  traditional landline customers are "guaranteed backup power during power
  outages"; a corded phone on copper needs no mains, while "with the advent of
  cordless phones the only time the consumer worried about backup batteries
  was for their cordless phone". Losing copper loses "Central Office
  provisioning of line power". The line works as long as the exchange's own
  batteries or generator do.
  [FCC 15-98, 2015-08-07, ¶¶ 14–15](https://docs.fcc.gov/public/attachments/FCC-15-98A1.pdf),
  read 2026-10-06.
- **A fibre line needs mains at the house. Confirmed.** Fibre service needs
  the optical network terminal at the house to be powered; without a battery
  unit it stops when the house's power does. The FCC took **8 hours** of
  battery at the house as the US norm, some carriers offering up to 24
  (FCC 15-98, ¶ 32). Whether Argentine fibre customers get any battery:
  **unconfirmed**; none is mentioned on CEZ's pages.
- **CEZ's fibre: point to point, run from Zárate. Secondary.** CEZ launched
  "Fibra Hogar" on 6 August 2020: fibre to the home, "el único prestador en
  Zárate que llega directamente al hogar en lo que se denomina punto a
  punto", its "base técnica" at the cooperative's seat on Av. Antártida
  Argentina in Zárate. It planned to extend to Lima and Escalada; by 2023 it
  reached "más de 30 zonas", with television over IP added.
  [CEZ, 2020-08](https://cezarate.com/2020/08/nuevo-servicio-de-internet-fibra-hogar/),
  [Nuestra Revista](https://nuestrarevista.com.ar/fibra-optica-cooperativa-en-zarate/),
  read 2026-10-06. Whether it had reached Lima's streets by February 2025, and
  the headend's backup power: **unconfirmed**.
  - **Reading, not fact:** a Lima subscriber's service needs three things
    powered: the house's terminal, the headend in Zárate, and CEZ's upstream
    link.
- **Cospli's telephone and internet: plant unconfirmed.** Its numbers are on
  Lima's 03487-48 exchange (480000, 480100, 480142; `Lima.md` for the
  cooperative). Whether it runs its own exchange, resells another carrier's
  lines, or serves internet over copper, fibre or radio is not found. What
  would confirm it: ENACOM's register of licensees, Cospli itself, or Tom.

## Under load

- **The 2019 blackout: no general failure, some congestion. Secondary.**
  ENACOM's head said phone and internet "funcionaron con normalidad"; traffic
  moved from fixed to mobile, with possible "cortes parciales o dificultades
  por saturación del tráfico"; one carrier reported intermittency, the other
  two no critical outages. No figures for users affected. The blackout was
  restored within about 13 hours, so most sites' batteries were never run
  down. Infobae (Jaimovich), above.
- **The 2020 lockdown: more traffic, no saturation. Secondary.** Traffic
  through the 30 regional exchange points rose **35 %** over February's
  average (more than 780 Gbps), per CABASE
  ([El Economista, 2020-05-15](https://eleconomista.com.ar/sociedad-redes/durante-cuarentena-trafico-internet-aumento-35-n34136));
  in the first week fixed traffic rose 27–38 %, mobile data 8–14 %, mobile
  voice up to 22 %, WhatsApp peaking at +180 % during the president's
  announcement, and an analyst said the networks were "responding well"
  ([Infobae, 2020-03-25](https://www.infobae.com/economia/2020/03/25/coronavirus-e-internet-cuanto-aumento-la-demanda-de-datos-desde-que-comenzo-el-periodo-de-aislacion/)).
  Both read 2026-10-06.
- **Under a blackout, load and batteries compound. Secondary.** In Iberia,
  speeds fell as sites dropped and their traffic moved to the survivors
  (Light Reading, above).

## Lost to wind and water, not power: Bahía Blanca

- **On 16 December 2023 and 7 March 2025 mobile service went at once.
  Secondary.** After the December 2023 windstorm, "la electricidad, los
  servicios de telefonía y las conexiones de internet colapsaron"
  ([DIB](https://dib.com.ar/adn-bonaerense/tragico-atardecer-dos-anos-del-temporal-viento-que-arraso-bahia-blanca-n49481));
  after the March 2025 flood "el 100% de los usuarios quedaron incomunicados",
  and the council ordered carriers to keep backup power
  ([La Nueva Radio Suárez](https://www.lanuevaradiosuarez.com.ar/region/exigen-a-empresas-de-telefonia-e-internet-que-no-corten-el-servicio-en-un-temporal-en-bahia-blanca-75296.html)).
  People looked for signal as much as for a charge
  ([Diario Popular, 2025-03-09](https://www.diariopopular.com.ar/general/cargar-el-celular-una-odisea-los-habitantes-bahia-blanca-despues-del-temporal-n832498)).
  All read 2026-10-06. Physical damage, not a clean loss of power, so a weak
  check for Lima.

## What sets the range, for Lima after day 21

**Derived, unconfirmed:** a reading of the sources above, not a measurement.

- **While the grid is up (days 1–21):** mobile sites, the fixed network and
  CEZ's fibre are on mains. Nothing above says they fail for lack of staff;
  sites are unattended by design. Faults would go unrepaired. How long a
  network runs with nobody fixing it is not found: **unconfirmed**.
- **Mobile, after the grid fails:**
  - sites on batteries alone: **about 2 to 8 hours**, the first dropping
    within a couple of hours (Iberia's 2–8 h; worst at about 7½ h);
  - the best-kept sites, or carriers' "up to 12 hours" (2019);
  - sites with a generator: **about 1 to 2 days**, until the tank runs dry
    with nobody refuelling (Katrina's "one to two days of fuel or charge",
    "24 to 48 hours");
  - and only while the switch and backhaul behind them stay up: their
    generators hold **12 hours at least** (the Tier minimum), likely more,
    then also need a fuel truck.
  - What sets it: battery size and age, whether a site has a generator, its
    tank, the load from survivors' phones, and whether the core and transport
    are still powered.
- **A copper landline with a corded phone:** as long as the exchange's
  batteries and generator last, on the same order as a switch's. A cordless
  phone dies with the house's power.
- **CEZ's fibre:** dies with the house's power unless the terminal has a
  battery (hours), and in any case with the headend in Zárate.
- **A phone in a pocket:** its own battery, "far more than 8 hours" of
  standby (FCC 15-98, ¶ 28); it keeps what's stored on it after the network
  is gone.
