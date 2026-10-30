from pathlib import Path
from io import BytesIO
import json
import re
import zipfile
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="SportsPulse | IPL Analytics", page_icon="🏏", layout="wide")

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
CACHE_DIR = DATA_DIR / "processed"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
BALL_FILE = CACHE_DIR / "deliveries.csv"
MATCH_FILE = CACHE_DIR / "matches.csv"
CRICSHEET_URL = "https://cricsheet.org/downloads/ipl_json.zip"

# ------------------------- Visual system -------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800;900&family=DM+Sans:wght@400;500;600;700;800&display=swap');
:root{--bg:#0b1110;--panel:#141d1a;--panel2:#1a2621;--line:#293a32;--lime:#c5f467;--muted:#9aaba1;--white:#f3f6ef;}
.stApp,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--white);font-family:'DM Sans',sans-serif;}
[data-testid="stHeader"]{background:transparent;}
.block-container{max-width:1500px;padding:1.2rem 2rem 3rem;}
h1,h2,h3,h4,p,label{color:var(--white);}
h1,h2,h3{font-family:'Barlow Condensed',sans-serif;letter-spacing:.2px;}
/* Sports broadcast identity */
.score-topline{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line);padding:0 0 15px;margin-bottom:22px;}
.score-brand{display:flex;align-items:center;gap:12px;}
.score-emblem{width:43px;height:43px;border-radius:50%;display:grid;place-items:center;background:var(--lime);color:#111b12;font-size:21px;font-weight:900;}
.score-wordmark{font:900 1.55rem 'Barlow Condensed';letter-spacing:1.3px;color:#f5f8f1;}
.score-wordmark span{color:var(--lime);}
.score-descriptor{font-size:.61rem;letter-spacing:2px;color:#8da095;font-weight:800;}
.live-tag{border:1px solid #465b43;border-radius:4px;padding:7px 11px;color:var(--lime);font-size:.65rem;font-weight:800;letter-spacing:1.3px;}
/* Pitch-inspired hero panel */
.match-hero{position:relative;overflow:hidden;background:linear-gradient(110deg,#172820,#203b2a 58%,#293f27);border:1px solid #38513a;border-radius:5px;padding:28px 30px;margin-bottom:18px;}
.match-hero:after{content:"";position:absolute;right:11%;top:-95px;width:310px;height:310px;border:1px solid #c5f46725;border-radius:50%;box-shadow:0 0 0 35px #c5f4670b,0 0 0 70px #c5f46708;}
.hero-kicker{color:var(--lime);font-size:.66rem;font-weight:800;letter-spacing:2.2px;}
.match-hero h1{font:900 clamp(2.5rem,5vw,4.1rem)/.98 'Barlow Condensed';color:#f5f8ef;margin:12px 0 8px;text-transform:uppercase;letter-spacing:.5px;}
.match-hero p{color:#b7c8b8;margin:0;max-width:650px;font-size:.9rem;}
.hero-season{position:absolute;right:30px;bottom:25px;text-align:right;z-index:1;}
.hero-season small{display:block;color:#a8bba9;font-size:.61rem;font-weight:800;letter-spacing:1.8px;}
.hero-season strong{color:var(--lime);font:800 1.6rem 'Barlow Condensed';}
/* Filters in a dark left rail */
section[data-testid="stSidebar"]{background:#101916;border-right:1px solid var(--line);}
section[data-testid="stSidebar"] *{color:#e8eee5;}
section[data-testid="stSidebar"] h2{font:800 1.4rem 'Barlow Condensed';letter-spacing:1px;}
section[data-testid="stSidebar"] [data-testid="stMultiSelect"]>div,
section[data-testid="stSidebar"] [data-testid="stSelectbox"]>div{background:#1a2621;border-color:#3a4b40;}
[data-testid="stSidebar"] .stMarkdown p{color:#9aaba1;font-size:.78rem;}
/* Scoreboard metrics */
.metric-strip{font-size:.63rem;font-weight:800;letter-spacing:2px;color:var(--lime);margin:20px 0 9px;}
div[data-testid="stMetric"]{background:linear-gradient(145deg,#17221d,#111a16)!important;border:1px solid #2b3c32!important;border-radius:4px!important;padding:15px 17px!important;min-height:106px;box-shadow:none!important;}
div[data-testid="stMetric"] label,div[data-testid="stMetric"] label *{color:#9aaba1!important;font-size:.7rem!important;font-weight:800!important;letter-spacing:1px;}
div[data-testid="stMetricValue"],div[data-testid="stMetricValue"] *{color:var(--lime)!important;font:800 1.8rem 'Barlow Condensed'!important;}
div[data-testid="stMetricDelta"]{color:#9aaba1!important;}
/* Match-centre navigation */
div[data-testid="stTabs"]{margin-top:20px;}
div[data-testid="stTabs"] button{color:#9aaba1!important;font-size:.77rem;font-weight:800;letter-spacing:.6px;padding:12px 15px;border-bottom:2px solid transparent;}
div[data-testid="stTabs"] button[aria-selected="true"]{color:var(--lime)!important;border-bottom:2px solid var(--lime)!important;}
div[data-testid="stTabs"] [data-baseweb="tab-highlight"]{background:var(--lime)!important;}
/* Dark chart and table surfaces */
[data-testid="stPlotlyChart"],[data-testid="stDataFrame"]{background:#131c18;border:1px solid #293a32;border-radius:5px;padding:7px;box-shadow:none;}
[data-testid="stDataFrame"] *{color:#e8eee5;}
.section-kicker{color:var(--lime);font-size:.65rem;font-weight:800;letter-spacing:2px;text-transform:uppercase;margin:7px 0 12px;}
.info-note{background:#17251d;border-left:3px solid var(--lime);padding:12px 15px;color:#b8c8b9;font-size:.8rem;margin:15px 0;border-radius:2px;}
div[data-testid="stSelectbox"] label,div[data-testid="stMultiSelect"] label{color:#c7d3c8!important;font-size:.76rem;font-weight:800;}
.stButton>button,.stDownloadButton>button{background:var(--lime);color:#142016;border:0;border-radius:3px;font-weight:900;}
.stButton>button:hover,.stDownloadButton>button:hover{background:#d6ff82;color:#142016;}
hr{border-color:var(--line)!important;}
@media(max-width:800px){.block-container{padding:1rem}.hero-season{position:static;text-align:left;margin-top:18px}.score-descriptor{display:none}.match-hero{padding:22px}}
</style>
""", unsafe_allow_html=True)


# ------------------------- Data ingestion -------------------------
def parse_cricsheet_zip(content: bytes):
    balls, matches = [], []
    with zipfile.ZipFile(BytesIO(content)) as archive:
        names = [n for n in archive.namelist() if n.lower().endswith(".json")]
        for name in names:
            try:
                raw = json.loads(archive.read(name))
                info = raw.get("info", {})
                teams = info.get("teams", [])
                dates = info.get("dates", [])
                season = info.get("season", "")
                match_id = Path(name).stem
                outcome = info.get("outcome", {})
                winner = outcome.get("winner", "")
                toss = info.get("toss", {})
                venue = info.get("venue", "Unknown")
                city = info.get("city", "Unknown")
                match_type = info.get("match_type", "T20")
                match_record = {
                    "match_id": match_id, "season": str(season),
                    "date": str(dates[0]) if dates else "",
                    "venue": venue, "city": city,
                    "team1": teams[0] if len(teams)>0 else "Unknown",
                    "team2": teams[1] if len(teams)>1 else "Unknown",
                    "winner": winner or "No result",
                    "toss_winner": toss.get("winner", "Unknown"),
                    "toss_decision": toss.get("decision", "Unknown"),
                    "player_of_match": (info.get("player_of_match") or ["Unknown"])[0],
                    "match_type": match_type,
                    "event": info.get("event", {}).get("name", "Indian Premier League")
                }
                matches.append(match_record)
                for innings_no, innings in enumerate(raw.get("innings", []), start=1):
                    batting_team = innings.get("team", "Unknown")
                    overs = innings.get("overs", [])
                    for over in overs:
                        over_no = int(over.get("over", 0))
                        for delivery_no, delivery in enumerate(over.get("deliveries", []), start=1):
                            batter = delivery.get("batter", "Unknown")
                            bowler = delivery.get("bowler", "Unknown")
                            non_striker = delivery.get("non_striker", "Unknown")
                            runs = delivery.get("runs", {})
                            extras = delivery.get("extras", {})
                            wickets = delivery.get("wickets", [])
                            total = int(runs.get("total", 0))
                            batter_runs = int(runs.get("batter", 0))
                            extras_runs = int(runs.get("extras", 0))
                            legal = not ("wides" in extras or "noballs" in extras)
                            balls_faced = "wides" not in extras
                            bowler_runs = total - int(extras.get("byes", 0)) - int(extras.get("legbyes", 0)) - int(extras.get("penalty", 0))
                            wicket_types = [w.get("kind", "") for w in wickets]
                            dismissed = [w.get("player_out", "") for w in wickets]
                            balls.append({
                                "match_id":match_id, "season":str(season), "date":str(dates[0]) if dates else "",
                                "venue":venue, "city":city, "innings":innings_no, "over":over_no,
                                "ball_in_over":delivery_no, "batting_team":batting_team,
                                "bowling_team": next((t for t in teams if t != batting_team), "Unknown"),
                                "batter":batter, "bowler":bowler, "non_striker":non_striker,
                                "batter_runs":batter_runs, "total_runs":total, "bowler_runs":bowler_runs,
                                "extras":extras_runs, "is_legal":legal, "balls_faced":balls_faced,
                                "is_wicket":len(wickets)>0,
                                "wicket_types":", ".join(wicket_types),
                                "player_dismissed":", ".join(dismissed),
                                "is_four":batter_runs==4 and not runs.get("non_boundary",False),
                                "is_six":batter_runs==6 and not runs.get("non_boundary",False)
                            })
            except Exception:
                continue
    return pd.DataFrame(balls), pd.DataFrame(matches)

@st.cache_data(show_spinner=False)
def load_data():
    if BALL_FILE.exists() and MATCH_FILE.exists():
        return pd.read_csv(BALL_FILE), pd.read_csv(MATCH_FILE)
    st.info("First-time setup: downloading the historical IPL dataset from Cricsheet. This may take a moment.")
    response = requests.get(CRICSHEET_URL, timeout=90)
    response.raise_for_status()
    balls, matches = parse_cricsheet_zip(response.content)
    if balls.empty or matches.empty:
        raise ValueError("The downloaded archive did not contain readable IPL match data.")
    balls.to_csv(BALL_FILE, index=False)
    matches.to_csv(MATCH_FILE, index=False)
    return balls, matches

@st.cache_data(show_spinner="Loading IPL data...")
def get_data():
    return load_data()

try:
    deliveries, matches = get_data()
except Exception as exc:
    st.error("SportsPulse could not load the Cricsheet dataset.")
    st.write("Check your internet connection and try again. You can also download the IPL JSON archive from Cricsheet and place it in the project data folder as `ipl_json.zip`.")
    st.code(str(exc))
    st.stop()

# ------------------------- Derived analytics -------------------------
px.defaults.template = "plotly_dark"
for col in ["batter_runs","total_runs","extras","over","innings"]:
    deliveries[col] = pd.to_numeric(deliveries[col], errors="coerce").fillna(0)
deliveries["is_legal"] = deliveries["is_legal"].astype(bool)
deliveries["is_wicket"] = deliveries["is_wicket"].astype(bool)
deliveries["is_four"] = deliveries["is_four"].astype(bool)
deliveries["is_six"] = deliveries["is_six"].astype(bool)
matches["season"] = matches["season"].astype(str)
def season_start_year(value):
    """Extract the starting calendar year from labels such as 2020/21 or 2025."""
    match = re.search(r"(\\d{4})", str(value))
    return int(match.group(1)) if match else 9999

seasons = sorted(
    matches["season"].dropna().astype(str).unique().tolist(),
    key=lambda value: (season_start_year(value), value)
)
teams = sorted(set(matches["team1"].dropna()) | set(matches["team2"].dropna()))

st.markdown("""
<div class="score-topline">
 <div class="score-brand">
  <div class="score-emblem">SP</div>
  <div><div class="score-wordmark">SPORTS<span>PULSE</span></div><div class="score-descriptor">THE IPL DATA ROOM</div></div>
 </div>
 <div class="live-tag">● HISTORICAL MATCH CENTRE</div>
</div>
<div class="match-hero">
 <div class="hero-kicker">INDIAN PREMIER LEAGUE / PERFORMANCE INTELLIGENCE</div>
 <h1>THE NUMBERS<br>BEHIND THE GAME.</h1>
 <p>Break down every season, batter, bowler and team. Explore the patterns that shape IPL cricket.</p>
 <div class="hero-season"><small>ARCHIVE COVERAGE</small><strong>{} — {}</strong></div>
</div>
""".format(seasons[0] if seasons else "—", seasons[-1] if seasons else "—"), unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## MATCH FILTERS")
    st.caption("Narrow the archive to the seasons and teams you want to inspect.")
    selected_seasons = st.multiselect("SEASON", seasons, default=seasons[-5:] if len(seasons)>5 else seasons)
    selected_teams = st.multiselect("TEAMS", teams, default=[])
    selected_venues = st.multiselect("VENUES", sorted(matches["venue"].dropna().unique()), default=[])
    st.markdown("---")
    st.caption("SOURCE: CRICSHEET IPL BALL-BY-BALL ARCHIVE")


filtered_matches = matches[matches["season"].isin(selected_seasons)].copy()
if selected_teams:
    filtered_matches = filtered_matches[filtered_matches["team1"].isin(selected_teams) | filtered_matches["team2"].isin(selected_teams)]
if selected_venues:
    filtered_matches = filtered_matches[filtered_matches["venue"].isin(selected_venues)]
valid_ids = set(filtered_matches["match_id"].astype(str))
filtered = deliveries[deliveries["match_id"].astype(str).isin(valid_ids)].copy()

match_count = len(filtered_matches)
run_count = int(filtered["total_runs"].sum())
player_count = filtered["batter"].nunique()
team_count = len(set(filtered_matches["team1"]) | set(filtered_matches["team2"])) if match_count else 0
win_count = int((filtered_matches["winner"] != "No result").sum())

st.markdown('<div class="metric-strip">LEAGUE SNAPSHOT / FILTERED DATA</div>', unsafe_allow_html=True)
k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("Matches", f"{match_count:,}")
k2.metric("Total runs", f"{run_count:,}")
k3.metric("Players", f"{player_count:,}")
k4.metric("Teams", f"{team_count:,}")
k5.metric("Decided matches", f"{win_count:,}")

st.markdown('<div class="info-note"><b>DATA FEED</b> &nbsp; Historical IPL match and ball-by-ball records sourced from Cricsheet. This is an analytics dashboard, not a live-score service.</div>', unsafe_allow_html=True)

overview, player_tab, team_tab, match_tab, compare_tab = st.tabs([
    "📊 Overview", "🏏 Player analytics", "🛡️ Team analytics", "📍 Match insights", "⚖️ Player comparison"
])

with overview:
    st.markdown('<div class="section-kicker">LEAGUE-WIDE PERFORMANCE</div>', unsafe_allow_html=True)
    left,right = st.columns([1.25,1], gap="large")
    with left:
        season_runs = filtered.groupby("season", as_index=False)["total_runs"].sum()
        season_runs["season_sort"] = pd.to_numeric(season_runs["season"], errors="coerce")
        season_runs = season_runs.sort_values("season_sort")
        fig = px.bar(season_runs, x="season", y="total_runs", title="Runs scored by season",
                     labels={"season":"Season","total_runs":"Runs"}, text_auto=".2s")
        fig.update_layout(height=340, margin=dict(l=10,r=10,t=55,b=10))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        wins = filtered_matches[filtered_matches["winner"]!="No result"]["winner"].value_counts().head(10).rename_axis("team").reset_index(name="wins")
        fig = px.pie(wins, names="team", values="wins", hole=.58, title="Most match wins in selection")
        fig.update_layout(height=340, margin=dict(l=10,r=10,t=55,b=10), legend=dict(orientation="h",y=-.15))
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### Highest run-scoring batters")
    bat = filtered.groupby("batter", as_index=False).agg(runs=("batter_runs","sum"), balls=("balls_faced","sum"), fours=("is_four","sum"), sixes=("is_six","sum"))
    bat["strike_rate"] = (bat["runs"] / bat["balls"].replace(0,pd.NA) * 100).round(2)
    st.dataframe(bat.sort_values("runs",ascending=False).head(10), use_container_width=True, hide_index=True)

with player_tab:
    st.markdown('<div class="section-kicker">BATTER & BOWLER PERFORMANCE</div>', unsafe_allow_html=True)
    bat = filtered.groupby("batter",as_index=False).agg(runs=("batter_runs","sum"), balls=("balls_faced","sum"), fours=("is_four","sum"), sixes=("is_six","sum"))
    bat["strike_rate"] = (bat["runs"] / bat["balls"].replace(0,pd.NA) * 100).round(2)
    bat = bat[bat["balls"]>=30].sort_values("runs",ascending=False)
    bowl = filtered.groupby("bowler",as_index=False).agg(runs_conceded=("bowler_runs","sum"), legal_balls=("is_legal","sum"), wickets=("is_wicket","sum"))
    bowl["overs"] = bowl["legal_balls"]/6
    bowl["economy"] = (bowl["runs_conceded"] / bowl["overs"].replace(0,pd.NA)).round(2)
    bowl = bowl[bowl["legal_balls"]>=60].sort_values("wickets",ascending=False)
    c1,c2=st.columns(2,gap="large")
    with c1:
        fig=px.bar(bat.head(12).sort_values("runs"),x="runs",y="batter",orientation="h",title="Top run scorers (minimum 30 balls)",color="runs",color_continuous_scale="Blues")
        fig.update_layout(height=440,coloraxis_showscale=False)
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(bat.head(15),use_container_width=True,hide_index=True)
    with c2:
        fig=px.bar(bowl.head(12).sort_values("wickets"),x="wickets",y="bowler",orientation="h",title="Leading wicket takers (minimum 10 overs)",color="wickets",color_continuous_scale="Teal")
        fig.update_layout(height=440,coloraxis_showscale=False)
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(bowl.head(15),use_container_width=True,hide_index=True)

with team_tab:
    st.markdown('<div class="section-kicker">TEAM RESULTS & SCORING</div>', unsafe_allow_html=True)
    team_rows=[]
    for team in sorted(set(filtered_matches["team1"])|set(filtered_matches["team2"])):
        played=filtered_matches[(filtered_matches["team1"]==team)|(filtered_matches["team2"]==team)]
        wins_team=int((played["winner"]==team).sum())
        team_rows.append({"team":team,"matches":len(played),"wins":wins_team,"win_pct":round(wins_team/len(played)*100,1) if len(played) else 0})
    team_stats=pd.DataFrame(team_rows).sort_values(["wins","win_pct"],ascending=False) if team_rows else pd.DataFrame()
    if team_stats.empty:
        st.info("No team records match the current filters. Adjust the season, team or venue selection.")
    else:
        c1,c2=st.columns(2,gap="large")
        with c1:
            fig=px.bar(team_stats.sort_values("wins"),x="wins",y="team",orientation="h",title="Most wins in selected seasons",color="wins",color_continuous_scale="Blues")
            fig.update_layout(height=420,coloraxis_showscale=False)
            st.plotly_chart(fig,use_container_width=True)
        with c2:
            team_runs=filtered.groupby("batting_team",as_index=False).agg(runs=("total_runs","sum"), innings=("match_id","nunique"))
            fig=px.bar(team_runs.sort_values("runs"),x="runs",y="batting_team",orientation="h",title="Total runs by batting team",color="runs",color_continuous_scale="Teal")
            fig.update_layout(height=420,coloraxis_showscale=False)
            st.plotly_chart(fig,use_container_width=True)
        st.dataframe(team_stats.rename(columns={"team":"Team","matches":"Matches","wins":"Wins","win_pct":"Win %"}),use_container_width=True,hide_index=True)

with match_tab:
    st.markdown('<div class="section-kicker">VENUES, TOSS & SCORING PATTERNS</div>', unsafe_allow_html=True)
    c1,c2=st.columns(2,gap="large")
    with c1:
        venue_counts=filtered_matches["venue"].value_counts().head(12).rename_axis("venue").reset_index(name="matches")
        fig=px.bar(venue_counts.sort_values("matches"),x="matches",y="venue",orientation="h",title="Most-used venues",color="matches",color_continuous_scale="Blues")
        fig.update_layout(height=430,coloraxis_showscale=False)
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        toss=filtered_matches[filtered_matches["toss_winner"]==filtered_matches["winner"]]
        toss_rate=len(toss)/len(filtered_matches[filtered_matches["winner"]!="No result"])*100 if len(filtered_matches[filtered_matches["winner"]!="No result"]) else 0
        st.metric("Toss winners who also won",f"{toss_rate:.1f}%")
        toss_decision=filtered_matches.groupby(["toss_decision","winner"],as_index=False).size()
        fig=px.histogram(filtered_matches,x="toss_decision",color="winner",title="Match winners by toss decision",barmode="group")
        fig.update_layout(height=350)
        st.plotly_chart(fig,use_container_width=True)
    st.markdown("#### Match results")
    st.dataframe(filtered_matches[["date","season","team1","team2","winner","venue","player_of_match"]].sort_values("date",ascending=False),use_container_width=True,hide_index=True)

with compare_tab:
    st.markdown('<div class="section-kicker">HEAD-TO-HEAD PLAYER COMPARISON</div>', unsafe_allow_html=True)
    player_names=sorted(filtered["batter"].dropna().unique())
    if len(player_names)>=2:
        a,b=st.columns(2)
        p1=a.selectbox("Player one",player_names,index=0)
        p2=b.selectbox("Player two",player_names,index=min(1,len(player_names)-1))
        def player_profile(name):
            d=filtered[filtered["batter"]==name]
            runs=int(d["batter_runs"].sum()); balls=int(d["is_legal"].sum())
            return {"Player":name,"Runs":runs,"Balls":balls,"Strike rate":round(runs/balls*100,2) if balls else 0,
                    "Fours":int(d["is_four"].sum()),"Sixes":int(d["is_six"].sum()),
                    "Matches":int(d["match_id"].nunique())}
        profiles=pd.DataFrame([player_profile(p1),player_profile(p2)])
        st.dataframe(profiles,use_container_width=True,hide_index=True)
        metric=st.selectbox("Compare metric",["Runs","Strike rate","Fours","Sixes","Matches"])
        fig=px.bar(profiles,x="Player",y=metric,color="Player",title=f"{metric} comparison")
        fig.update_layout(height=360,showlegend=False)
        st.plotly_chart(fig,use_container_width=True)
    else:
        st.info("Choose a wider season/team selection to compare players.")

st.caption("SportsPulse is an educational analytics project. Match outcomes and statistics are descriptive historical records, not predictions.")
