# Electricity in Argentina: dwellings, boards and breakers (#286)

Researched 2026-09-28 for #286, which blocks #289 (re-basing the power system
on Argentina). This replaces `Electrical.md` (the US record: NEC, UL 489,
GFCI) as the target for the game. Lima's distributor, the Cooperativa de
Electricidad de Zárate (CEZ), is in `Lima.md`, "Utilities in Lima and the
region".

**Who regulates what.** Lima is in Buenos Aires province, outside the ENRE's
area (EDENOR, EDESUR, EDELAP). CEZ is regulated by the **OCEBA** (Organismo de
Control de Energía Eléctrica de la Provincia de Buenos Aires). Inside the
house, the rules are the AEA's *Reglamentación para la ejecución de
instalaciones eléctricas en inmuebles* (AEA 90364), which the OCEBA's rules
and the ENRE's both point to.

## Sources

- **AEA 90364-7-770, Edición 2017** (first edition 2017, ISBN
  978-987-1975-38-9): *viviendas unifamiliares hasta 63 A*. **Primary**: the
  standard itself, in the courtesy copy the AEA gave Córdoba's regulator
  (ERSeP), read through the Wayback Machine's copy of 2025-10-16 (the live
  URL returned 403):
  [ersep.cba.gov.ar](https://ersep.cba.gov.ar/wp-content/uploads/2021/05/AEA-90364-7-770_ERSep.pdf),
  [archived](https://web.archive.org/web/20251016162122/https://ersep.cba.gov.ar/wp-content/uploads/2021/05/AEA-90364-7-770_ERSep.pdf).
- **OCEBA, Reglamento de Acometidas, Tarifa 1 (Pequeñas Demandas)**, the
  annex to OCEBA Resolución 92: **primary**, from the OCEBA's own site
  ([page](https://oceba.gba.gov.ar/nueva_web/s.php?i=12),
  [PDF](https://oceba.gba.gov.ar/nueva_web/PDFS/acometidas/Resolucion0092Anexo.pdf)).
  Its year, 2008, is from the normas.gba.gob.ar listing (secondary).
- **OCEBA, Subanexo D, Normas de calidad del servicio público y sanciones**
  (the concession contracts' quality annex): **primary**,
  [PDF](https://oceba.gba.gov.ar/nueva_web/PDFS/concesiones/SUBANEXO_D.pdf).
- **ENRE, Reglamento para la conexión de nuevos suministros domiciliarios**
  (2022 edition; Res. ENRE 225/2011 per the ENRE's own file name for the
  earlier annex, secondary): **primary**, but for the ENRE's area,
  not Lima's. It's cited where it agrees with the AEA.
  [PDF](https://www.argentina.gob.ar/sites/default/files/2018/03/reglamentoconexionnuevossuministros_edicion2022.pdf.pdf).
- **ABB, *Comparison of tripping characteristics for miniature
  circuit-breakers*** (2CDC400002D0201): the maker's table of IEC/EN 60898-1
  characteristics. **Secondary** for the standard (IEC 60898-1 itself is
  paywalled), primary for ABB.
  [PDF](https://library.e.abb.com/public/114371fcc8e0456096db42d614bead67/2CDC400002D0201_view.pdf).
- **Enel, Especificación LATAM E-BT-004 Rev. 02** (2014-08-28),
  *Interruptores termomagnéticos*, Table 12, quoting IEC 60898-1 §9.10:
  **secondary** for the standard. Enel owns Edesur (Buenos Aires).
  [PDF](https://www.eneldistribuicao.com.br/rj/documentos/E-BT-004_R-02.pdf).
- **Schneider Electric Argentina** product pages (Easy9 2P, 4.5 kA, curve C):
  primary for what one maker sells in Argentina.
  [6 A](https://www.se.com/ar/es/product/EZ9F34206/interruptor-termomagn%C3%A9tico-easy9-2p-6a-45ka-curva-c/),
  [10 A](https://www.se.com/ar/es/product/EZ9F34210/interruptor-termomagn%C3%A9tico-easy9-2p-10a-45ka-curva-c/),
  [16 A](https://www.se.com/ar/es/product/EZ9F34216/interruptor-termomagn%C3%A9tico-easy9-2p-16a-45ka-curva-c/),
  [32 A](https://www.se.com/ar/es/product/EZ9F34232/interruptor-termomagn%C3%A9tico-easy9-2p-32a-45ka-curva-c/).
  Listed through search results, 2026-09-28; the pages weren't opened.

## Supply

- **220/380 V a.c., 50 Hz ± 1 Hz.** AEA 770 §770.4.2 gives "220/380 Vca
  (230/400 Vca)": 220 V between a phase and neutral, 380 V between phases.
  The OCEBA's service-connection rules scope themselves to "380/220 V".
  **Confirmed.**
- **Tolerance at the supply point (OCEBA Subanexo D):** ±7.0 % high voltage,
  ±8.0 % medium, ±8.0 % low voltage; up to 12.0 % in rural areas. These are
  the limits beyond which the distributor is sanctioned, for the stage the
  annex defines. **Confirmed.**
- **Single-phase or three-phase:** a house is normally single-phase. AEA 770
  §770.8.3.3 recommends asking for a three-phase supply when the total load
  exceeds **7 kVA or 32 A**. The OCEBA's Tarifa 1 covers demands under
  **10 kW**. **Confirmed.**
- **The dwelling rule's scope:** AEA 770 covers houses whose main breaker is
  at most **63 A**, with a prospective short-circuit current of at most 10 kA
  at the origin (§770.1). Above that is AEA 90364-7-771.

## The meter and the boards

- **The meter is on the property line** (OCEBA Acometidas T1, §§1–5): on the
  *línea municipal*, reachable from the street 24 hours a day. When the house
  is set back from the line, the meter goes in a **brick pillar**
  (*pilar de mampostería*) or a precast concrete pillar at the front. When
  the façade is on the line, it goes on the façade. The meter box is
  insulating, IP 43, with a clear polycarbonate lid, mounted between 0.80 m
  and 1.80 m high. **Confirmed.**
- **The main board (*tablero principal*) is next to it:**
  - no more than **1 m** from the meter box (OCEBA); AEA 770 §770.16.3.1
    allows up to 2 m, "dentro de la propiedad";
  - IP 54, insulating (class II, double insulation);
  - it carries a **bipolar thermal-magnetic breaker** switching the neutral
    with the phase, **at most 32 A** for a Tarifa 1 supply (OCEBA).
  **Confirmed.** So in a house with a front pillar, the main switch is
  outdoors at the gate, in its own box beside the meter.
- **Inside, a distribution board (*tablero seccional*):** fed from the main
  board, "en lugares de fácil localización dentro de la vivienda"
  (§770.16.3.2). One per inhabited floor is suggested. It is never in a
  bathroom, inside furniture, under a counter or in a hard-to-reach recess.
  It has 0.9 m of clear space in front and at least 200 lx of light
  (§770.16.2). Levers sit between 0.40 m and 2 m high. It keeps 20 % spare
  space in 18 mm modules (§770.16.4). **Confirmed.**
- **Every board carries the "riesgo eléctrico" symbol** (IRAM 10005-1), at
  least 40 mm high, on its front (§770.16.2.1). **Confirmed.**

## Circuits (AEA 770 §770.6.6, Table 770.6.I)

All confirmed. Every circuit is single-phase and at least two-wire.

| Code | Name | Max protection | Max outlets | What it feeds |
|---|---|---|---|---|
| **IUG** | *Iluminación de uso general* | **16 A** | 15 | Lights, fans and extractors, or other loads ≤ 10 A, fixed or on 10 A 2P+T sockets (IRAM 2071) |
| **TUG** | *Tomacorrientes de uso general* | **20 A** | 15 | 10 A 2P+T sockets (IRAM 2071), loads ≤ 10 A each |
| **TUE** | *Tomacorrientes de uso especial* | **32 A** | 15 | Loads over 10 A: 20 A 2P+T sockets (IRAM 2071), or 16 A IEC 60309 |
| *specific* | MBTF, APM, ATE, MBTS, ACU, IUE, ITE, OCE… | per AEA 90364-7-771 | — | Dedicated loads (ACU is a dedicated single load, such as an air conditioner) |

- **Fixed appliances in kitchens and laundries** (§770.7.1 i) include
  fridges, freezers, extractor hoods, dishwashers, electric cookers, and
  "cocinas, anafes y hornos a gas que requieran alimentación eléctrica"
  (a gas cooker with electric ignition). They get dedicated socket modules
  (Table 770.7.III).
- Ceiling fans and extractors can go on a lighting circuit (§770.7.1 c).
- A *toilette* (a bathroom without a bath or shower) can have its socket on
  the lighting circuit (§770.7.1 k).

## Grado de electrificación: how many circuits (AEA 770 §770.7.3–770.7.4)

All confirmed. The area counts the covered area plus half the semi-covered
area (a covered gallery, for example).

| Grado | Area | Minimum circuits | Variants |
|---|---|---|---|
| **Mínimo** | up to 60 m² | 2 | 1 IUG + 1 TUG |
| **Medio** | over 60 up to 130 m² | 3 | 2 IUG + 1 TUG, or 1 IUG + 2 TUG |
| **Elevado** | over 130 up to 200 m² | 5 | 2 IUG + 3 TUG, or 3 IUG + 2 TUG |
| **Superior** | over 200 m² | 6 | as Elevado, plus one of free choice |

- **Demand (Table 770.8.I):**
  - an IUG circuit counts 2/3 of 60 VA per outlet;
  - an IUG with derived sockets counts 2,200 VA;
  - a TUG counts **2,200 VA**;
  - a TUE counts **3,300 VA**.
- **Simultaneity (Table 770.8.II):** 1 for 2 circuits, 0.8 for 3, 0.7 for 5,
  0.6 for 6.
- **Minimum outlets per room (Table 770.7.III):** for example, a living or
  dining room at *Medio* has one lighting outlet per 18 m² (at least one) and
  one socket per 6 m² (at least two). A kitchen has lighting plus socket
  modules for its fixed appliances. The table didn't extract cleanly from the
  PDF: re-read it before a pass depends on a specific room's count.
- **The standard's own worked example** (Annex 770-B, a *Mínimo* home's
  distribution board): a **30 mA, 2 × 40 A** residual-current device at its
  head, then **B 2 × 10 A (IUG)** and **B 2 × 16 A (TUG)**. The *Medio*,
  three-phase example has three 16 A circuits. **Confirmed**, as an example
  only.

## Breakers (*interruptores termomagnéticos*)

- **Only IEC 60898-1 breakers are allowed** for circuit protection
  (§770.16.5.2). They must be lockable open and switch **both poles**: in a
  single-phase house every circuit breaker is **bipolar**, and single-pole
  breakers are not allowed. Fuses are forbidden in the main board (ENRE
  §3.9, for its area). **Confirmed.**
- **The main board's head device is a breaker of at most 63 A**
  (§770.16.5.3), and at most **32 A** on a Tarifa 1 supply in Buenos Aires
  province (OCEBA). **Confirmed.**
- **Trip characteristics, IEC 60898-1** (ABB's table, and Enel E-BT-004
  Table 12 quoting §9.10; **secondary**), at a 30 °C reference, the same for
  curves B, C and D:

  | Current | Time | Result |
  |---|---|---|
  | 1.13 × In | ≥ 1 h (In ≤ 63 A) | no trip (conventional non-tripping current) |
  | 1.45 × In | < 1 h (In ≤ 63 A), just after the 1.13 × In test | trip (conventional tripping current) |
  | 2.55 × In | 1 s < t < 60 s (In ≤ 32 A); 1 s < t < 120 s (In > 32 A) | trip |

  The instantaneous (magnetic) band, as a multiple of In: at its low end the
  breaker may still take the thermal time; at its high end it trips in under
  0.1 s.

  | Curve | Band | At the low end | At the high end |
  |---|---|---|---|
  | **B** | 3–5 × In | 0.1–45 s (In ≤ 32 A), 0.1–90 s (> 32 A) | < 0.1 s |
  | **C** | 5–10 × In | 0.1–15 s (≤ 32 A), 0.1–30 s (> 32 A) | < 0.1 s |
  | **D** | 10–20 × In | 0.1–4 s (≤ 32 A), 0.1–8 s (> 32 A) | < 0.1 s |

  ABB adds that above 30 °C the thermal currents fall by about 6 % per 10 K.
- **Ratings on the Argentine market:** Schneider's Easy9 2P curve C line in
  Argentina lists 6, 10, 16, 20, 25, 32 and 40 A (secondary: search results).
  IEC 60898-1's preferred values are said to be 6, 8, 10, 13, 16, 20, 25,
  32, 40, 50, 63, 80, 100 and 125 A (secondary; the standard wasn't read).
  **Unconfirmed as a complete list**. AEA 770's examples use 10, 16 and 40 A,
  and the circuit maxima are 16, 20 and 32 A.
- **Curve in homes:** the AEA's example uses curve **B** for IUG and TUG. The
  retail 2P lines seen are curve **C**. Which is more common in Lima's homes
  is unconfirmed.

## Residual-current devices (*interruptor diferencial*, colloquially *disyuntor*)

- **Every terminal circuit is protected by a residual-current device of
  In ≤ 30 mA, non-delayed** ("instantánea"), as complementary protection
  against direct contact (§770.14.2.3). It is not a replacement for the
  other protections. **Confirmed.**
- IEC 61008 (without overcurrent protection) or IEC 61009 (with it). The
  usual type in dwellings is **type AC**. **Confirmed.**
- Between boards, where needed, up to **300 mA**, preferably selective
  (marked "S") (§770.14.3). **Confirmed.**
- **One RCD may cover several circuits** (§770.16.5.4, note 1), or each
  circuit may have its own. At a distribution board, the RCD can be the head
  device itself. **Confirmed.**
- With 30 mA RCDs, an earth resistance of **≤ 40 Ω** counts as protection
  against indirect contact, keeping the touch voltage under **24 V**
  (§770.14.3; ENRE's "tensión de seguridad" is also 24 V a.c.). The earthing
  system is **TT**. **Confirmed.**
- The ENRE requires a ≤ 30 mA RCD in the main board for its area (§3.8).
- An AFDD (arc-fault detector) is recommended, not required (§770.16.5.4).

## What a shock does, and what the RCD changes (#247, 2026-09-28)

- **Effects by current and time (IEC TS 60479-1, as quoted by the EMF-Portal
  of RWTH Aachen; secondary).** For a.c. at 15–100 Hz, current path from the
  left hand to both feet:
  - **AC-1**, up to 0.5 mA: perception possible, usually no startle.
  - **AC-2**: perception and involuntary contractions, mostly no harm. Its
    upper curve is the **let-go threshold**: about **5 mA** for currents
    flowing more than 6 s, rising to about **200 mA** for 10 ms. Above it, a
    gripping hand may not be able to let go.
  - **AC-3**: strong contractions, reversible disturbances of the heart,
    mostly no organ damage.
  - **AC-4**: cardiac or breathing arrest possible. Ventricular fibrillation
    probability rises to about 5 % (curve c2), then 50 % (c3), then above.
  - "Already small currents of about **40 mA** may lead to ventricular
    fibrillation and therefore to the death of an individual if the current
    flow through the human body is longer than **2 seconds**."
  [EMF-Portal](https://www.emf-portal.org/en/cms/page/home/more/electrical-injuries/background-information-for-limit-values).
- **How fast a 30 mA RCD cuts it (IEC 61008-1, general type; secondary):**
  within **300 ms** at 1 × IΔn (30 mA), **150 ms** at 2 × (60 mA), and
  **40 ms** at 5 × (150 mA). It must not trip at 0.5 × IΔn. Hager (a maker)
  confirms 40 ms at 5 × IΔn under BS EN 61008-1 A2017, and 300 ms at
  1 × IΔn as the accepted figure.
  [Hager](https://hager.com/uk/support/regulations-18th-edition/updated-rccb-testing),
  [Stoklink summary](https://stoklink.com/blogs/technical/rcd-trip-time-iec-61008-testing).
- **What it doesn't cover (AEA 770 §770.14.2.3, primary):** the RCD is
  complementary protection only. It "no evita los accidentes provocados por
  contacto simultáneo de dos partes conductoras activas de potenciales
  diferentes": a body across phase and neutral carries current that returns
  on the neutral, so there's no residual current for the RCD to see.
- **So, in short:** a phase-to-earth shock on a circuit behind a working
  30 mA RCD is cut in tens to hundreds of milliseconds, before the ~2 s that
  small currents need to cause fibrillation. With no RCD, or across phase
  and neutral, or upstream of the RCD, it lasts until the player lets go or
  the breaker trips, and a breaker trips on overcurrent, not on the tens of
  milliamps that kill.

## Sockets, plugs and wire colours

- **Sockets: 2P+T, 10 A or 20 A, IRAM 2071** (AEA 770 §770.6.6). The
  matching plugs are IRAM 2073 (two-pole with earth, 10 A and 20 A), as
  `Lima.md` already notes (secondary). A socket outlet box holds
  two sockets (50 × 100 mm box) or four (100 × 100 mm).
- **Wire colours** (OCEBA Acometidas T1, quoting the AEA): **neutral light
  blue** (*celeste*), phase R **brown**, S **black**, T **red**. A
  single-phase installation's phase is preferably brown. The protective
  earth is green-and-yellow (AEA practice; not read here). **Confirmed**
  except the earth.

## Old installations (#311, 2026-09-28)

**Which homes have them in the game** is a game rule, not a sourced fact
(Tom, 2026-09-28). A building whose site stop is on a paved or gravel street
has a modern installation, as above. One on a dirt street has an old board.

**What an old board is, from what could be found:**

- **Porcelain plug fuses (*tapones*) and a bipolar cut-off switch**, in a
  small box. Argentine electricians' forums describe "un tablero principal
  antiguo de fusibles (tapones) y llave de corte bipolar", in a box of
  about **16 × 22 cm** with short wires inside. The advice when replacing
  one is to have the distributor pull the fuse ahead of the meter, because
  working it live is dangerous. **Secondary** (YoReparo threads, read
  through search summaries; the pages block automated readers).
- **Fuses still turn up in Zárate.** When a customer claims damages, the
  CEZ inspects the installation's protections, "por ejemplo llave de corte,
  llave térmica, **fusible**, disyuntor diferencial, guarda motor". A claim
  is refused when the installation lacks protections or has irregularities.
  **Primary**, the CEZ's own page:
  [Reclamos por artefactos dañados](https://cezarate.com/reclamos-por-artefactos-danados/),
  read 2026-09-28.
- **Circuits doubled up on fuses.** A 2024 forum thread describes an old
  three-phase board where each fuse base had three different circuits' wires
  hanging from it, "none properly protected". Secondary, one case
  ([Foro Electricidad](https://www.foroelectricidad.net/threads/reenplazar-tapones-ceramicos-y-consulta-calor-en-cables.5282/)).
- **No residual-current device.** The AEA's 1987 regulation is said to have
  required the *interruptor diferencial* (secondary, search summary). A
  maker's trade article says RCDs were adopted selectively in Argentina from
  about **1970** (Steck, *Ingeniería Eléctrica* 327, December 2017,
  [link](https://www.editores-srl.com.ar/revistas/ie/327/steck_disyuntor_diferencial);
  secondary). Neither date is confirmed from the AEA itself.
- **No retrofit law in Buenos Aires province found.** A 2022 talk by the
  AEA's second vice-president lists the laws that make the AEA rules
  compulsory: Decreto 351/79 (workplaces), Res. ENRE 207/95 (replaced by
  269/12), SICyM 92/98, and provincial laws in **Salta (7469/07), Santa Cruz
  (3247/12), Córdoba (10281/15), Catamarca (5551/18)** and the CABA building
  code (Ley 6100/2019). Buenos Aires province isn't among them. So an old
  house in Lima faces no rule that forces an upgrade, except the OCEBA's
  rules when a **new** supply is connected. Secondary for the absence (it
  isn't proof there's none)
  ([Manili, UTN-FRSC, 2022-08-22](https://www.frsc.utn.edu.ar/web/wp-content/uploads/2022/10/Presentacion-FRSC.pdf)).
- **No earth conductor** in very old houses: trade and retail guides say so.
  Secondary, general.
- **Sockets take three flat pins (*tres patas planas*: 2P+T, IRAM 2071) in
  most of Argentina, old homes included** (Tom, first-hand, 2026-09-28). Round two-pin sockets (type C)
  survive in some old buildings but are rare (El Destape, 2024, secondary).
  Whether an old home's earth pin is actually earthed is **unconfirmed**:
  the guides above suggest that often it isn't.
- **The fuse ratings** of an old board, and whether the meter sits in a
  pillar or on the façade in old Lima homes, are **unconfirmed**.

## Appliances as sold in Argentina (#311, 2026-09-28)

All read 2026-09-28. Makers are named here as sources; game text never names
them.

**What a Lima home has (Tom, first-hand, 2026-09-28):**
- **Water is heated by an electric tank heater** (*termotanque eléctrico*).
- **An electric pump lifts water to the roof tank.** It's common.
- **No bathroom extractor fan**, usually: a window instead.
- **No smoke alarm**: rare in homes. No provincial requirement for homes was
  found either. Buenos Aires province relies on each partido's building code
  (search summary, secondary).

**Fridge-freezer:**
- **Energy:** Patrick's cyclic fridge-freezers (models 135/136/141/151: 264,
  300, 359 and 389 L, class A, R134a, climate class T) use **310, 326, 356
  and 419 kWh a year**. **Primary** (the maker's manual,
  [PDF](https://www.canigo.com.ar/wp-content/uploads/manual-de-uso-heladera-Patrick-HPK136.pdf)).
  That averages **35–48 W** over the year (derived: kWh ÷ 8,760 h).
  Edesur's list of no-frost models gives 260–420 kWh a year (secondary,
  [Edesur](https://www.edesur.com.ar/novedades/4224/)).
- **Nameplate current:** a Vondom fridge (388 L) is **0.75 A** and its
  freezer (304 L) **1.0 A**, at 220–240 V, 50 Hz. The freezer's defrost heater
  is **160 W**. **Primary** for Vondom (the maker's store,
  [page](https://vondom.com.ar/products/heladera-freezer-inverter-no-frost-acero-inoxidable-695-l)).
- **Starting current:** Embraco's R600a household compressors for
  200–220 V, 50 Hz (LBP) have a **locked-rotor current of 3.7–8.2 A**:
  EMI30CNP 3.70, EMI40CNP 4.50, EMU40CLP 7.33, EGAS80CLP 7.90, EMYE70CLP
  8.20. **Primary** for Embraco (Asia-Pacific catalogue,
  [PDF](https://www.embraco.com/download/product/embraco-catalog-apa_compressed.pdf)).
  Which compressors Argentine fridges carry is **unconfirmed**.
- **From the manuals (primary, Patrick and Drean):**
  - the fridge wants **220 V / 50 Hz, 198–242 V**, and a voltage stabiliser of
    at least 1,000 W where the supply strays outside that;
  - it gets **its own socket**, with **no extension cords, multi-plugs or
    adapters**, and an earthed three-flat-pin plug;
  - after unplugging, **wait at least 10 minutes** before plugging it back in.

  [Drean PDF](https://blog.drean.com.ar/wp-content/uploads/2022/05/Manual-Heladera-No-frost-Drean.pdf).

**Lighting:**
- **Incandescent lamps for general household use have been banned from
  import and sale since 2010-12-31** (Ley 26.473), and halogen lamps since
  2019-12-31 (Ley 27.492). Secondary
  ([Argentina Ambiental](https://argentinambiental.com/legislacion/nacional/ley-27492-prohibicion-importacion-comercializacion-lamparas-incandescentes-halogenas/)).
  The Boletín Oficial page returned 503.
- **An E27 LED bulb of 12 W gives about 840 lm, standing in for a 60 W
  incandescent.** 9 W and 12 W, 220 V bulbs are common on the market.
  Secondary (retailers:
  [Kaiser LED](https://www.kaiserled.com.ar/producto/tabla-de-equivalencias-led/)).
- **A fridge or oven lamp is at most 15 W**, E14 or screw-fit, 220 V (Drean
  and Longvie manuals, primary).

**Gas cooker and extractor hood** (Longvie, *Manual de Características y
Especificaciones de Productos*, undated, a trade catalogue;
**primary** for Longvie,
[PDF](https://d26lpennugtm8s.cloudfront.net/stores/089/303/rte/MANUAL%20Y%20ESPECIFICACIONES%20LONGVIE.pdf)):
- **Cookers have electronic spark ignition:** "encendido instantáneo
  electrónico 'a una mano' en hornallas y horno", with ceramic spark plugs,
  and an oven lamp at 220 V. Longvie's standard-line 12331B has "encendido
  electrónico independiente" and is multigas (natural or bottled)
  ([longvie.com](https://www.longvie.com/Front/showProduct/171), primary).
  AEA 770 lists "cocinas… a gas que requieran alimentación eléctrica" among
  the fixed kitchen appliances (above).
- **The ignition's own draw is unconfirmed.** No nameplate for it was found.
- **Extractor hoods: 130–250 W maximum** across Longvie's range (for example
  200 W for a 90 cm island hood with two motors and three speeds, and 130 W
  for a 60–90 cm hood with halogen lights).

**Water pump (to the roof tank)** (0.5 hp peripheral pumps, sold for lifting
water to a tank, all at 220 V; secondary, retail listings):
- Rowa RW-PR60: **0.37 kW, 2.7 A**, 33 m head
  ([CER América](https://www.cer.com.ar/shop/0019-0033-bomba-periferica-rowa-modelo-rw-pr60-05-hp-eleva-33-mts-220v-15127));
- Motorarg QB60: **1.7 A**; Czerweny QB60-L1: 0.37 kW (search summaries).
- **Starting current: unconfirmed.**

**Electric water heater:**
- Rheem's 85 L wall heater TEC085RH has a **2,000 W element**. **Primary**
  ([Rheem](https://www.rheem.com.ar/Termotanques/Residenciales/Electricos/Performance/TEC085RH)).
- Rheem's electric range runs **1,500–3,000 W**, with about 85 L/h recovery
  for the TEC085RH (search summary, secondary). Señorial sells an 80 L,
  **1,500 W** model (TESZ-95, retail listing, secondary).

**Extension cords (for #244):**
- **Cord cable is "tipo taller"** to IRAM NM 247-5 (it replaced IRAM 2158):
  extra-flexible class 5 copper, PVC sheathed, "no apto para aparatos de
  calefacción". **Current for a single cable in air** (Argenplas CAT-TT2,
  2021; **primary** for the maker,
  [PDF](http://www.argenplas.net/wp-content/uploads/2021/11/Tipo-Taller-IRAM-NM-247-5_web.pdf)):

  | Cable | Current |
  |---|---|
  | 3 × 0.75 mm² | 7 A |
  | 3 × 1 mm² | 10 A |
  | 3 × 1.5 mm² | 17 A |
  | 3 × 2.5 mm² | 22 A |
  | 3 × 4 mm² | 30 A |

- **Cords as sold:** 3 × 1 mm² or 3 × 1.5 mm², **10, 15, 20 or 30 m**, with
  a 10 A plug and socket (2P+T, IRAM 2073 / IRAM 2063). One 15 m, 3 × 1.5 mm²
  cord is rated 10 A working, 14 A maximum. Secondary (retail listings,
  through search summaries).

## Not yet researched

- **CEZ's own connection rules**, if it publishes any beyond the OCEBA's.
- **The home's real board:** Tom's first-hand knowledge of the Barrio Atucha
  row houses (#305).
- **Starting currents** of the pump, and of the compressors Argentine fridges
  actually carry.
- **A gas cooker's ignition draw.**
