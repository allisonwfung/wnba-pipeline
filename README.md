# 🏀 WNBA Analytics Pipeline

**Live App:** [wnba-shot-charts.streamlit.app](https://allisonwfung-wnba-pipeline-app-hjzvqw.streamlit.app/)

An end-to-end data pipeline and interactive analytics app for the 2026 WNBA season, built with Python and updated daily via automated data collection.

---

## What It Does

- **Interactive shot charts** — select any WNBA player and visualize where they score from using hex bin density maps overlaid on a to-scale basketball court
- **Made shots vs all attempts** — toggle between scoring plays only or all field goal attempts
- **Daily updates** — new game data is automatically pulled from the ESPN API every morning via GitHub Actions

---

## Tech Stack

- **Python**: Data pipeline, analysis, visualization
- **ESPN API**: Play-by-play data source
- **Pandas**: Data cleaning and transformation 
- **Matplotlib**: Shot chart visualization
- **Streamlit**: Interactive web app
- **GitHub Actions**: Automated daily data updates

---

## Project Structure

```
wnba-pipeline/
├── app.py              
├── espn_scraper.py     
├── wnba_data.csv       
├── requirements.txt   
└── .github/
    └── workflows/      
```

---

## Running Locally

```bash
git clone https://github.com/allisonwfung/wnba-pipeline
cd wnba-pipeline
pip install -r requirements.txt
streamlit run app.py
```

To manually update the dataset:
```bash
python espn_scraper.py
```
---

## Data Source
- Play-by-play data sourced from the ESPN WNBA API

---

## Credits
- Basketball court drawing adapted from [Savvas Tjortjoglou](http://savvastjortjoglou.com/nba-shot-sharts.html)
