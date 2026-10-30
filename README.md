# SportsPulse — IPL Performance & Strategy Intelligence

## 🚀 Live Demo

**Try SportsPulse here:** [Open Live Dashboard](https://sportspulse-6vqhbfnkve3pkxddue5kg3.streamlit.app/)

Explore historical IPL performance, player statistics, team analytics and match insights.

SportsPulse is a Streamlit-based cricket analytics dashboard built around historical Indian Premier League (IPL) ball-by-ball data.

## Features

- **Overview:** match/run/player/team KPIs, runs by season, team wins and leading run scorers.
- **Player analytics:** batting runs, strike rate, boundaries, wicket-takers and bowling economy.
- **Team analytics:** wins, win percentage and runs scored by team.
- **Match insights:** venue activity, toss decision patterns and match results.
- **Player comparison:** compare two batters across runs, strike rate, fours, sixes and matches.
- **Filters:** select seasons, teams and venues.

## Tech stack

- Python
- Streamlit
- Pandas
- Plotly
- Requests

## Dataset and first run

The app retrieves the IPL JSON archive from **Cricsheet** on first launch and converts it into local CSV cache files in `data/processed/`. An internet connection is required for the first run. Later runs use the cached CSVs.

Dataset source: https://cricsheet.org/downloads/

Cricsheet provides historical match data and ball-by-ball deliveries. The coverage shown in the app is based on the archive available at runtime. This project is not a live-score service.

Please read and follow Cricsheet's current terms and attribution requirements before redistributing the data or using the project commercially: https://cricsheet.org/terms_and_conditions/

## Run locally (Windows PowerShell)

1. Extract the ZIP.
2. Open PowerShell in the extracted `SportsPulse` folder.
3. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

4. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

5. Start the dashboard:

```powershell
python -m streamlit run app.py
```

The first launch downloads the Cricsheet IPL archive and builds the local cache. Allow a little time for this step.

## Deploy on Streamlit Community Cloud

1. Create a new GitHub repository named `SportsPulse`.
2. Upload the contents of this project folder (not the outer ZIP).
3. Open https://share.streamlit.io/ and choose **New app**.
4. Select the repository, branch `main`, and `app.py`.
5. Deploy. The first deployment downloads and processes the source data.

## Important methodology notes

- Runs by team use total runs from each delivery.
- Batter strike rate uses balls faced (wides are excluded).
- Bowler runs conceded exclude byes, leg-byes and penalty runs; wides and no-balls are charged to the bowler.
- Bowling economy uses legal deliveries divided by six.
- Wicket totals in this starter dashboard count all recorded dismissal events. For specialist bowling analysis, exclude run-outs, retired hurt, obstructing the field and other dismissals not credited to the bowler.
- Filters affect the full dashboard.

## Project structure

```text
SportsPulse/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── data/
    └── README.md
```

## Limitations

This is a descriptive historical analytics project. It does not provide live scores, betting advice, player predictions or guaranteed performance forecasts. Some metrics are simplified for an educational dashboard and should be interpreted with the methodology notes above.
