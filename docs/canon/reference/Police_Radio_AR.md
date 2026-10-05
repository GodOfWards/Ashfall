# Police radio: the Policía de la Provincia de Buenos Aires's network (#477)

Real-world facts, not canon until a decision adopts them (`../Ashfall_Canon.md`
records what's decided). See `README.md` for the status labels. Researched
2026-10-05 for #477: #476 is designing what the Comisaría Zárate 2's radio
lets the player do, with the three lattice masts on its lot (`Lima.md`,
"Comisaría Zárate 2") as the reason it reaches further than the
`portable_radio`. Brands appear here only where a source names them; none
appears in the game.

## The network as of the era: digital, trunked, encrypted

- **The force runs a digital trunked system to the P25 (APCO-25) standard.
  Confirmed.**
  - Encrypted (ADP and AES were bought); voice and data on the same radios;
    radios' and cars' GPS positions shown to the dispatch centre's operator
    on a map of each jurisdiction. Redundancy for the critical elements,
    automatic routing, and a digital microwave backbone shared by voice and
    data.
  - Its staff trained in March 2017 on the system's repeaters, dispatch
    consoles, and portable and mobile radios, as part of "la modernización
    del sistema de comunicaciones".
  - Policía de la Provincia de Buenos Aires, *gacetilla* 27-03-2017,
    ["Nuevo Sistema de Comunicaciones encriptado"](https://policia.mseg.gba.gov.ar/gacetilla_policial/Marzo17/27-03-17.html),
    read 2026-10-05. La Nación reported the purchase on 2016-09-19
    ([La Nación](https://www.lanacion.com.ar/seguridad/la-policia-de-buenos-aires-tendra-nuevos-equipos-de-comunicacion-nid1939229/),
    read 2026-10-05; secondary).
- **Still running in 2025. Confirmed.** The Ministerio de Seguridad called
  Licitación Pública 2/25 (PBAC 179-0179-LPU25) for the "Servicio de Soporte
  y Actualización Tecnológica del Sistema Digital de Comunicaciones P25":
  730 days, an official budget of ARS 16,022,307,070.56, bids opened
  19 May 2025. Boletín Oficial de la Provincia de Buenos Aires, 2025-04-29,
  read on the [eldial.com copy of the bulletin](https://www.eldial.com/nuevo/boletinBA/2025/BA250429.pdf),
  2026-10-05. The technical annex (sites, their power) is on PBAC and wasn't
  read.
- **Before it: the S.I.C. Confirmed.** The Sistema Integral de
  Comunicaciones, finished at the end of 1997: a 2,500 km microwave network
  with **98 repeater hops, 32 UHF sites, 30,000 fixed, mobile and portable
  radios**, 22 telephone exchanges and 13 supervision centres. Radio began on
  VHF in the 1950s, from the Unidades Regionales del Interior; the 1948
  network's masts ("soportes irradiantes") were 60 m tall. Superintendencia
  de Comunicaciones,
  [*Reseña*](https://policia.mseg.gba.gov.ar/superintendencia_comunicaciones/rese%C3%B1a.html),
  undated, read 2026-10-05.
- **Coverage, phase by phase. Secondary.** Migration began in 2005 with the
  conurbano's first ring; "en sucesivas etapas se consiguió cubrir todo el
  AMBA", then Mar del Plata, Pinamar and Villa Gesell. Phase V (2023) took
  in Bahía Blanca, where switching over "dio de baja la vieja capa de
  comunicación" after 27 years, with La Costa, General Lavalle (Ruta 11)
  and "San Nicolás (trazado de la ruta 9)" next.
  [La Nueva, 2023-07-29](https://www.lanueva.com/nota/2023-7-29-5-0-20-seguridad-los-beneficios-de-encriptar-la-frecuencia-policial),
  read 2026-10-05.
- **Whether Partido de Zárate, and Lima, had it by February 2025:
  unconfirmed.** No source names Zárate.
  - **Reading, not fact: it leans yes.** The Superintendencia files
    Zárate-Campana under Conurbano Norte (below); the AMBA was covered
    before 2023; and the 2023 phase ran along Ruta 9, past Zárate, to
    San Nicolás.
  - Lima is about 16 km from Zárate (`Lima.md`), at the edge of any
    metropolitan footprint, so a portable's street-level coverage there is
    the weakest link.
  - What would confirm it: the PBAC 2/25 technical annex, or a Zárate-area
    report of the switch-over.

## Who a comisaría talks to

- **911 dispatch. Confirmed.** The Superintendencia de Comunicaciones covers
  the whole province with **44 "Centros de Despacho de Emergencias
  Policiales 911"**, centralised on Radio Central, "cabecera de la Red
  Radioeléctrica Policial", under six zonal supervisions. **Zárate-Campana
  is one of them, under Conurbano Norte**, with Tigre, San Isidro, San
  Miguel, San Martín and Moreno.
  [*Supervisiones Zonales*](https://policia.mseg.gba.gov.ar/superintendencia_comunicaciones/zonales.html),
  undated, read 2026-10-05.
  - So a Lima comisaría's radio traffic would be dispatched from the
    Zárate-Campana centre. Where that centre sits: unconfirmed.
- **What radio the station itself has: unconfirmed.** No source describes a
  Lima comisaría's radio.
  - **Reading, not fact:** P25 systems put a desktop **control station** (a
    mobile radio on its own mains power supply, with an outside antenna) in
    a station that isn't a dispatch centre, and **consoles** only at the
    dispatch centres. That is how the federal tender below specifies them:
    120 control stations "en configuración de instalación sobre un
    escritorio y remota", with their own power supply, falling back to a
    preprogrammed conventional channel if the trunking's control channel is
    lost; consoles only at Zárate and Rosario. Whether the province does the
    same is unconfirmed.

## Band, and what other radios hear

- **UHF, around 406–418 MHz. Unconfirmed.** Hobby listeners, before
  encryption, logged the "Red de Comandos de la Policía Bonaerense" there:
  - **Zárate on 408.710 MHz** (listed in 2008, repeated in 2017); Pilar,
    the nearest other district listed, on 409.960 MHz;
  - repeaters' inputs 10 MHz above their outputs;
  - the ministry's La Plata channel, 409.135 MHz, "se escucha bien en todos
    lados por que tiene repetidoras por todos lados".
  - [escanerfrecuencias.es, thread 12807](http://escanerfrecuencias.es/FORO/viewtopic.php?f=77&t=12807)
    (posts 2008–2010) and
    [thread 37051](http://www.escanerfrecuencias.es/FORO/viewtopic.php?t=37051)
    (2017), read 2026-10-05. A hobby forum, not ENACOM: ENACOM's licence
    records would confirm it, and weren't found.
- **The analog channels went quiet in 2017. Unconfirmed.** In July 2017 a
  listener wrote that for some months no provincial 911 channel could be
  heard: "lo único que se escucha es como un motor encendido tipo fritura"
  (thread 37051). That is how an encrypted digital channel sounds on an
  analog receiver, and fits the 2017 roll-out.
- **An AM/FM radio hears none of it.** Broadcast FM is **88–108 MHz** and AM
  **535–1705 kHz** ([ENACOM, FM](https://www.enacom.gob.ar/fm_p565);
  [ENACOM, AM](https://www.enacom.gob.ar/am_p563); read 2026-10-05 through a
  search summary; secondary). The police are near 400 MHz and encrypted
  besides: even a scanner tuned there hears noise.
- **Others on the air near Lima.** The federal forces (Gendarmería,
  Prefectura, Policía Federal) run their own P25 network (below). Prefectura
  Zárate also works marine VHF, 156.625 and 156.800 MHz (channel 16)
  (thread 37051; unconfirmed).

## Reach, and the masts

- **A trunked repeater site's mast is around 96 m. Confirmed** as one
  tender's requirement. The national Ministerio de Seguridad's 2016 tender
  for the federal forces' P25 along **Ruta 9, Zárate–Rosario**, at 400 and
  800 MHz, sites at **Zárate (console), Paranacito, Baradero, San Pedro,
  San Nicolás and Rosario (console)**:
  - a guyed mast **at least 96 m** tall at each repeater site (an existing
    one at least 60 m), a shelter of at least 15 m² by 3 m high, two air
    conditioners;
  - coverage designed to TIA TSB-88 DAQ 3.0 for a car with a roof antenna,
    and for a portable at head height in the street.
  - Ministerio de Seguridad de la Nación, Compulsa Abreviada por Urgencia,
    EXP-SEG 5286/2016, *Pliego de Bases y Condiciones Particulares*,
    October 2016
    ([argentinacompra](http://onc-ftp1.argentinacompra.gov.ar/0347/000/050000502016000000/CNV-000689805001.doc),
    read 2026-10-05). It is the federal network, not the province's.
- **The Lima masts' height: unknown.** Street View shows "three tall lattice
  radio masts" (`Lima.md`); no height was measured.
  - **Reading, not fact:** three masts could carry a control station's
    antenna, older UHF or VHF antennas from the S.I.C. or before, and a
    microwave or data link; or one could be a repeater.
  - What would settle it: their height against the one-storey building in
    Street View, and whether any carries a dish (a microwave link makes the
    lot a network node).
- **Range: derived, unconfirmed.** The radio horizon between two antennas is
  about **4.12 × (√h₁ + √h₂) km**, heights in metres (the standard 4/3-earth
  formula).
  - A 30 m mast to a car antenna at 1.5 m: ~27 km. A 96 m site: ~45 km.
  - Lima to Zárate is about 16 km, so even a 20–30 m mast at the comisaría
    has Zárate inside its horizon across flat ground (`Atucha.md`, #462, on
    how flat it is).
  - Real coverage near 400 MHz is set by power, antennas, trees and
    buildings. The horizon is a ceiling, not a range.

## Power

- **A trunked repeater site, as specified. Confirmed** as the 2016 federal
  tender's requirement:
  - a **48 V battery bank for 4 hours** on modular rectifiers (N+1),
    "con independencia del grupo electrógeno";
  - a **standby generator with an automatic transfer switch**, running the
    whole site for **at least 24 hours at full load**;
  - an on-line double-conversion UPS of at least 10 kVA, **at least
    300 minutes** at full load;
  - dispatch consoles on an on-line UPS for **4 hours**.
  - Whether the province's sites are built the same: unconfirmed (the PBAC
    2/25 annex would say).
- **Derived, unconfirmed:** a site built that way keeps working for about a
  day after the grid goes, on its generator's fuel, then hours more on its
  batteries; longer only if someone refuels it.
- **The comisaría's own radio: not found.** A control station runs from a
  mains power supply. Whether a provincial comisaría has a battery or UPS
  behind it wasn't found; the reading in `Lima.md` (a radio base usually has
  batteries) is still a reading. No standby generator was found at the Lima
  station (`Lima.md`).
- **Portables. Confirmed** as the 2016 federal tender's requirement: at
  least **8 hours between charges** at a 5/5/90 duty cycle (5 % transmit,
  5 % receive, 90 % standby), **3 hours** to charge from empty, two
  batteries per radio.

## Not found

- ENACOM's licence records for the provincial police.
- The PBAC 2/25 technical annex: the province's site list and its sites'
  power.
- Anything specific to the Lima comisaría's radio, or its masts' height.

## For future searches

- `policia.mseg.gba.gov.ar` answers 403 to some fetchers; a plain browser
  user agent works.
- "Lima" with "Zárate" and "policía" returns Peru's PNP; add "Buenos Aires"
  or "Partido".
