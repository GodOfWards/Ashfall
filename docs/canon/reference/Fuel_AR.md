# Fuel, bottled gas and generators in Argentina (#287)

Researched 2026-09-28 for #287, which blocks #239 (petrol), #245 (generators)
and the stove's gas side. This replaces `Fuel_and_Generators.md` (the US
record) as the target for the game. The game's era is **February 2025**: a
rule that changed after that is marked as such. Stations in and around Lima
are in `Lima.md` ("Landmarks from listings", "Utilities in Lima and the
region"); connecting a generator to a house is #323. See `README.md` for the
status labels.

**Decided (Tom):**
- Lima has no gas network: it's all garrafas (2026-09-27, first-hand;
  `Lima.md`).
- **Generators and vehicles in the game are designed for nafta Súper**
  (2026-09-28). Premium isn't needed for anything.

## Nafta and gasoil

- **Grades.** Resolution SE 1283/2006, art. 2, names naftas grade 1, 2 and 3
  and gasoils grade 1, 2 and 3. **Primary**
  ([InfoLEG](https://servicios.infoleg.gob.ar/infolegInternet/anexos/115000-119999/119840/texact.htm)).
  Its specification annex is an image. The current annex is from **Res. SE
  79/2026** (2026-03-27). **Primary**
  ([annex PDF via Ecofield](https://www.ecofield.net/Legales/Combustibles/res79-26_SE-anexo.pdf);
  [government news](https://www.argentina.gob.ar/noticias/el-gobierno-nacional-adecuo-la-norma-de-calidad-de-naftas-para-amortiguar-el-impacto-del)):

  | | Grade 2, **Súper** | Grade 3, **Premium** |
  |---|---|---|
  | RON, minimum | 93 (2026) | 97 |
  | MON, minimum | 83 | 85 |
  | Sulfur, maximum | 50 mg/kg | 10 mg/kg |
  | Oxygen, maximum | 5.6 % | 5.6 % |
  | Bioethanol | up to 15 % | up to 15 % |

  **In the game's era Súper was RON ≥ 95.** Res. 79/2026 loosened the
  standard "para amortiguar el impacto del precio del crudo". The 95 figure is
  secondary (trade and press guides); the pre-2026 annex wasn't read.
- **Gasoil:** grade 3 has at most 10 mg/kg sulfur. Grade 2 has more: 350 mg/kg
  in the 2026 annex (primary).
- **Mandatory blends: Ley 27.640 (2021), in force until 2030-12-31.**
  - **12 % bioethanol in nafta:** 6 % from sugarcane and 6 % from corn, the
    rest open.
  - **Biodiesel in gasoil:** 5 % by the law's text, 7.5 % in practice.

  IPAAT, a provincial agency's summary
  ([link](https://www.ipaat.gov.ar/nota/311/marco-regulatorio-de-biocombustibles)),
  and the press. Secondary for the law, whose Boletín Oficial page returned
  503. Res. 79/2026 allows up to 15 % bioethanol voluntarily. A bill raising
  the mandatory cut to 15 % passed the Senate in September 2026, after the
  era.
- **Shelf life.** Secondary: trade press and retailers. This agrees with the
  US record's 3–6 months for E10.
  - **In a sealed can:** nafta starts to degrade after **3–6 months**, and
    shouldn't be kept past about 6. Premium lasts a little longer, up to about
    9 months. A stabiliser extends it to 1–3 years.
  - **In a station's buried tank:** "un año es un tiempo prudencial para que
    los combustibles mantengan sus propiedades". Mariano Santillán, former
    director of inspections at the Secretaría de Energía,
    [Surtidores](https://surtidores.com.ar/ventas-en-baja-cuanto-tiempo-puede-aguantar-la-nafta-y-el-gasoil-almacenados-en-el-tanque-de-una-estacion-de-servicio/),
    2024-01-17.
  - **Why:** the bioethanol picks up water and the light fractions evaporate.
    Gasoil's biodiesel **turns gummy after about 3 months** and attracts
    bacteria.

## Stations and cans

- **Station pumps need power.** In the July 2025 AMBA blackout, one of the few
  stations still dispensing stopped when its own power went, leaving queues.
  Secondary
  ([Infobae](https://www.infobae.com/sociedad/2025/07/03/sin-luz-y-sin-gnc-en-el-amba-se-registraron-cortes-del-suministro-electrico-y-largas-filas-para-cargar-gasoil/)).
  A station with its own generator keeps selling. **Whether Lima's has one is
  unconfirmed.**
- **Cans: the national rule is Resolution 195/97.** Secondary (Santillán,
  [Surtidores](https://surtidores.com.ar/que-requisitos-se-exigen-para-la-venta-y-transporte-de-combustibles-en-pequenos-recipientes/)).
  - Containers must be compatible with the fuel: UN **3H1**, a plastic or
    metal can with a screw cap.
  - A station fills **up to 60 L per sale**.
  - A private person may carry about **333 kg (≈ 400 L)** without special
    permits.
  - Some municipalities (in Patagonia) ban filling unapproved containers.

## Bottled gas (garrafas)

- **What's in them.** YPF Gas, **primary** ([gas.ypf.com](https://gas.ypf.com/)):
  - **butano comercial** in **10, 12 and 15 kg garrafas**: mostly butane, with
    up to 50 % propane acceptable;
  - **propano comercial**, at least 96 % propane, in **30 and 45 kg
    cylinders**, and in bulk tanks (*chanchas*).

  Other distributors describe the 10 kg as butane with about 20 % propane
  (secondary). Spain's energy ministry defines commercial butane as ≥ 80 % C4
  and commercial propane as ≥ 80 % C3 (primary for Spain).
- **It doesn't go off.** YPF Gas calls LPG **"imperecedero"**: butane and
  propane both keep indefinitely in a sealed bottle, unlike nafta. **Primary**
  (YPF Gas).
- **The difference that matters is cold.** At atmospheric pressure **butane
  boils at −0.5 °C and propane at −42.2 °C**
  ([MITECO](https://www.miteco.gob.es/en/energia/hidrocarburos-nuevos-combustibles/glp.html),
  primary for Spain). Near or below 0 °C a butane garrafa barely vaporises, so
  its flame weakens or dies; a propane cylinder keeps working. Derived from
  the boiling points; relevant to #58 (weather).
- **Energy:** commercial butane gives **10,700–11,800 kcal/kg** and propane
  **10,800–11,900 kcal/kg**; butane's gross value is **≈ 11,870 kcal/kg**.
  Secondary, from a Spanish distributor and search summaries.
- **Burner ratings** (ENARGAS, the national gas regulator), **primary**
  ([ENARGAS](https://www.enargas.gob.ar/secciones/eficiencia-energetica/consumo-artefactos.php)):
  - hob burners: small 1,000, medium 1,400, large 1,800 kcal/h;
  - oven 3,000 kcal/h;
  - calefón (instant water heater) 15,000–24,000 kcal/h;
  - gas heaters 2,500–10,000 kcal/h.
- **How long a garrafa lasts:**
  - **Per burner, derived:** on butane (≈ 11,870 kcal/kg) the hob burners use
    **≈ 0.08, 0.12 and 0.15 kg/h**, and the oven **≈ 0.25 kg/h**.
  - **Flat out, derived:** four burners and the oven at full draw about
    0.72 kg/h, so a 10 kg garrafa lasts **about 14 hours**.
  - **In everyday use** (retail guides, secondary; both agree with the
    derivation):
    - a 10 kg garrafa on cooking alone lasts **about a month**: about
      **25 days** for a four-burner cooker used 60 minutes a day;
    - with a gas heater running several hours a day, as little as
      **10 days**.
- **Regulator:** cookers are set for LPG at **280 mm water column** and
  natural gas at 180 mm (Domec cooker manual, primary; `Electrical_AR.md`). A
  garrafa connects through a regulator to 280 mm.
- **The subsidy: Programa Hogar** (Decreto 470/2015, in force 2015-04-01)
  subsidises low-income households **in areas without a gas network**, on
  garrafas of 10, 12 and 15 kg. **Primary**
  ([Argentina.gob.ar](https://www.argentina.gob.ar/normativa/nacional/245444/texto)).
  Lima, with no network, is in scope. Maximum prices along the chain were
  **removed in August 2024** (press, secondary).
- **Where garrafas are sold in Lima: unconfirmed**, perhaps a *depósito de
  garrafas* or an almacén. Tom, first-hand, or #288.

## Portable generators

- **Honda EU22i** (inverter). **Primary**
  ([Honda Argentina](https://pf.honda.com.ar/producto/EU22i)):
  - **1.8 kVA rated, 2.2 kVA maximum, 220 V, 50 Hz**, plus 12 V 8 A DC;
  - **3.6 L tank, 0.88 L/h** at full speed;
  - **8.1 h** with eco throttle, 3.2 h at full;
  - 57 dB(A), 21 kg, manual start.
- **Lüsqtoff LG2500** (a budget open-frame model sold widely). Secondary, from
  retailers
  ([Narcisi](https://www.jcnarcisi.com.ar/productos/generador-lusqtoff-2500-watts-lg2500/)):
  - **2.0 kVA rated, 2.2 kVA maximum, 220 V ~ 50 Hz**, a 4-stroke 6.2 hp
    engine;
  - **tank 12–15 L** (listings differ), **about 10 h** autonomy;
  - 33 kg, manual start, nafta.
- **So a household portable is about 2 kVA at 220 V, or 9 A continuous.**
  That's enough for the fridge, lights and the pump, but not the 2,000 W
  water heater together with them.
- **The sockets are unconfirmed.** Neither page lists them. IRAM 2071 10 A
  (2P+T) is likely, or Schuko on imports.

## Not yet researched

- The sockets on Argentine portable generators.
- Whether Lima's station (D.A.P.S.A., `Lima.md`) has a generator.
- Where garrafas are sold in Lima.
- The pre-2026 fuel annex (Súper's RON 95 in the era), and the gasoil grades'
  full specifications.
- Connecting a generator to a house: #323.
