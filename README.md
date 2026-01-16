# 100% Renewable Electricity System – System Planning (PyPSA)

Dieses Projekt untersucht Szenarien für ein **100% erneuerbares Stromsystem** in **[Land/Region einsetzen]** mithilfe eines **PyPSA-Systemplanungsmodells**.  
Ziel ist es, ein kosteneffizientes Energiesystem zu modellieren, das den Strombedarf regional abdeckt und verschiedene Ausbauoptionen (Erzeugung, Netze, Speicher) berücksichtigt.

> Kurs: *Data Science for Energy System Modelling (WT 2025/2026)*  
> Assignment 4 – Group Assignment on System Planning

---

## Projektziele (Scope)

### 1) Regionale Modellierung
- Aufteilung von **[Land]** in **mindestens 5 Regionen** auf Basis des **GADM-Datensatzes**
- Bestimmung eines **repräsentativen Punkts** pro Region (z. B. Centroid)
- Falls nicht landlocked: Extraktion der **Exclusive Economic Zone (EEZ)**

### 2) Erneuerbare Potenziale (Solar, Onshore-, Offshore-Wind)
Wir berechnen installierbare Potenziale und zugehörige **Kapazitätsfaktoren** pro Region:

**Land Eligibility Analyse** (Ausschlussflächen), u. a.:
- Mindestabstände zu Flughäfen, Straßen und Siedlungen
- Schutzgebiete ausschließen
- Höhenlimit (onshore)
- Offshore: Mindestabstand zur Küste + maximale Wassertiefe

**Weather & Capacity Factors**
- ERA5 Wetterdaten via **atlite Cutout**
- Kapazitätsfaktor-Zeitreihen (p_max_pu) pro Region und Technologie

Annahmen:
- Wind-Turbinen: `Vestas_V112_3MW` (Onshore), `NREL_ReferenceTurbine_5MW_offshore` (Offshore)
- Solar Panel: `CdTe` (optimale Neigung nach Breitengrad)
- Deployment Density: **3 MW/km²**

### 3) PyPSA Optimierungsmodell (System Planning)
Wir erstellen ein PyPSA-Netzwerk, das die **jährlichen Gesamtsystemkosten minimiert**.

Im Modell enthalten:
- **Buses** pro Region (mind. 5)
- **Last-Zeitreihen** (GEGIS / OPSD wenn EU)
- Bestehende **konventionelle Kraftwerke** (ohne Wind & Solar), regional aggregiert
- Optionale Erweiterung von:
  - Solar, Onshore, Offshore (mit Potenzialgrenzen `p_nom_max`)
  - **Übertragungsleitungen** als bidirektionale Links zwischen benachbarten Regionen  
    (Kosten: 700 €/MW/km, Länge = 1.5 × Luftlinie)
  - **Batteriespeicher** (E/P Ratio: 2h, 4h, 6h)
  - **Wasserstoffspeicher** (E/P Ratio: 168h, 336h, 672h)

Kosten & Parameter:
- Technologieannahmen aus **PyPSA/technology-data**
- Annuity-Berechnung mit **Discount Rate 7%**
- Marginal Costs: Fuel + VOM  
- Capital Costs: annualisierte Investition + FOM

### 4) Szenarien & Untersuchungen
Wir vergleichen mindestens zwei Modellläufe:

1. **Baseline / No CO₂ Limit**
2. **100% CO₂ Reduktion (0 Emissionen)**

Zusätzlich führen wir **mindestens eine Sensitivitätsanalyse** im 0-CO₂-Fall durch, z. B.:
- Grid Expansion Limits / Autarkie
- Technologie-Kosten-Variation (z. B. Solar / Wind / Batterie / Grid)
- Potenzial-Reduktion (Solar/Wind)
- Wetterjahr-Vergleich (mehr Aufwand)

---

## Deliverables
Dieses Repository enthält die vollständigen Projektergebnisse:

- **10–12 Minuten Präsentation**
- **Slide Deck + Supplementary Slides**
- **Code zur Datenaufbereitung & Modellierung**
- (Optional) zusätzliche Plots / Tabellen für die Auswertung

---

## Erwartete Outputs / Visualisierungen
Beispiele für relevante Ergebnisplots:
- Gesamtsystemkosten und Aufteilung nach Technologien
- Installierte Kapazitäten (pro Region & Technologie)
- Strommix / Erzeugungsprofile (z. B. typische Woche)
- Curtailment Rate
- Storage Filling Levels über das Jahr
- Price Duration Curves & regionale Durchschnittspreise
- CO₂ Shadow Price (bei Constraint-Run)

---

## Repository Struktur (Vorschlag)
```text
.
├─ data/
│  ├─ raw/                # heruntergeladene Rohdaten (pro Land)
│  ├─ processed/          # vorbereitete & bereinigte Daten
│  └─ cutouts/            # atlite ERA5 cutouts
│
├─ notebooks/             # exploration / plots / debugging
├─ src/
│  ├─ preprocessing/      # Shapes, land eligibility, CF-Berechnung
│  ├─ model/              # PyPSA network building
│  ├─ scenarios/          # runs: baseline, co2-free, sensitivities
│  └─ plotting/           # Ergebnisplots und Export
│
├─ results/
│  ├─ figures/
│  ├─ tables/
│  └─ networks/           # exportierte PyPSA networks (optional)
│
├─ slides/                # final slides + supplementary slides
├─ requirements.txt
└─ README.md

