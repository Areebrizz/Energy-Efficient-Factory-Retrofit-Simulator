# Factory Energy Retrofit Simulator

🏭⚡ Factory Energy Retrofit Simulator — Professional Industrial Energy Audit & Simulation Tool

A Streamlit app that performs a rapid engineering-level audit of factory motor and lighting systems, estimates energy and cost savings from motor upgrades, VFD installation, and LED lighting retrofits, and produces prioritized retrofit recommendations with simple financial projections.

---

## Key Features

- Interactive facility configuration (factory type, operating hours, energy costs, carbon factor).
- Motor systems audit:
  - Inventory input for multiple motors (rating, quantity, load factor, efficiency class, VFD applicability).
  - IE class efficiency curves and upgrade analysis to IE4.
  - VFD savings estimation and simple payback calculations.
- Lighting systems audit:
  - Current lighting configuration and LED retrofit proposal.
  - Annual energy and cost comparisons by technology.
- Simulation results:
  - Annual energy and cost savings, CO₂ reduction.
  - Detailed tables and interactive Plotly visualizations (upgrade economics, VFD payback, 10-year projection).
  - Exportable CSV reports (summary and detailed analysis).
- Prioritized recommendations and a simple implementation roadmap.
- Clean, professional UI with custom styling.

---

## Quick Start

Prerequisites
- Python 3.8+ (3.9+ recommended)
- git (optional)

1. Clone the repository (if applicable)
   ```
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```

2. Install dependencies
   Create a virtual environment (recommended) and install:
   ```
   python -m venv .venv
   source .venv/bin/activate    # macOS / Linux
   .venv\Scripts\activate       # Windows

   pip install -r requirements.txt
   ```
   If you don't have a `requirements.txt`, install the main packages:
   ```
   pip install streamlit pandas numpy plotly
   ```

3. Run the app
   ```
   streamlit run app.py
   ```
   (If the main file has a different name, use that filename instead.)

---

## Recommended Requirements (example `requirements.txt`)

```
streamlit>=1.0
pandas
numpy
plotly
```

Add any additional packages you use in the project.

---

## Usage & Workflow

1. Open the sidebar and configure:
   - Factory Type (Textile, Automotive, Food Processing, etc.)
   - Operating days, shifts, hours per shift
   - Electricity cost and demand charge
   - CO₂ emission factor and analysis period
2. Fill in Motor Inventory (ratings, quantities, load factors, IE classes).
3. Configure Lighting (number of fixtures, wattage, operating hours) and propose LED wattage.
4. Click "Run Energy Retrofit Simulation" to compute:
   - Motor upgrade and VFD savings and paybacks
   - Lighting retrofit savings and payback
   - Aggregate energy & cost savings and CO₂ reduction
5. Review the optimized recommendations and download CSV reports.

---

## Engineering Models (brief)

- Motor efficiency uses static efficiency curves for IE1–IE4 at representative load points (25%, 50%, 75%, 100%) with linear interpolation between points.
- Motor upgrade evaluation compares current input energy to an IE4-equivalent input to estimate savings.
- VFD savings modeled with a heuristic savings curve that depends on motor load factor (typical variable-torque savings).
- Lighting energy computed as fixtures × wattage × operating hours (kWh).
- Financials are simple: energy savings × electricity cost, simple upfront cost assumptions (e.g., $/kW for motors and VFDs, LED cost per unit + install multiplier). Payback = investment / annual savings.

---

## Assumptions & Limitations

- Estimates are high-level and intended for screening-level audits. Real site conditions (power factor, duty cycles, control strategies, part-load performance, installation costs, incentives) will influence actual savings.
- Motor cost and VFD cost assumptions are simplified constants—replace these with site quotes for accurate economics.
- CO₂ factor is user-specified; use your regional grid emission factor for better accuracy.
- The app does not model demand charge reductions in detail (peak shaving/load shifting) beyond energy and simple demand-cost inputs.
- No warranty: results are indicative only. Always validate with on-site measurements and detailed engineering.

---

## Customization & Extension Ideas

- Add inverter efficiency and harmonic impacts to VFD modeling.
- Include demand charge / peak load modeling and load profile inputs (hourly).
- Add an equipment database and import/export of inventories (CSV/Excel).
- Replace cost heuristics with a configurable cost database and regional pricing.
- Integrate incentives and rebate calculators.
- Add more technologies (compressed air systems, HVAC, heat recovery, process-specific measures).

---

## File Map (typical)

- app.py — main Streamlit application (where the provided code resides)
- README.md — this file
- requirements.txt — Python dependencies
- assets/ — optional images, icons, and static files
- data/ — optional sample inventories or config CSVs

---

## Example Screens / Tabs

- "Motor Systems" — inventory, efficiency tables, VFD guidance.
- "Lighting Systems" — current vs LED, technology comparison and metrics.
- "Simulation Results" — detailed tables, charts, projections, CO₂.
- "Recommendations" — prioritized list, roadmap, CSV downloads.

---

## Contributing

Contributions are welcome. Suggested workflow:
1. Fork the repo
2. Create a feature branch
3. Open a pull request with a clear description and tests/examples where applicable

Please follow standard Python best practices and include any new dependencies in `requirements.txt`.

---

## Author & Contact

Made by Areeb Rizwan — Mechanical Engineer  
Website: https://www.areebrizwan.com  
LinkedIn: https://www.linkedin.com/in/areebrizwan

If you found this tool useful or want enhancements, feel free to reach out.

---

## License

Add a license file (e.g., MIT) to the repository if you intend to make the project open-source. Example:

```
MIT License
Copyright (c) 2026 Areeb Rizwan
```

---

## Changelog (high level)
- v2.1 — Improved UI styling, motor & lighting models, VFD heuristics, CSV downloads, recommendations engine.

---

Disclaimer: This README summarizes the app and usage. The app provides engineering estimates; verify results with in-situ measurements and supplier quotes before investment decisions.
