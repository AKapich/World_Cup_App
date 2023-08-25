import streamlit as st
from auxiliary import match_dict, matches
from change_charts import create_plot

st.set_page_config(
        page_title="World Cup 2022 Analysis",
        page_icon="⚽",
        #layout="wide"
    )
st.title("World Cup 2022 Analysis")

# dropdown for choosing the match
st.sidebar.title("Select Match")
selected_match = st.sidebar.selectbox("Match:", match_dict.keys(), index=9)
match_id = match_dict[selected_match]
home_team = selected_match.split(' - ')[0]
away_team = selected_match.split(' - ')[1]
competition_stage = matches[matches['match_id']==match_id].iloc[0]['competition_stage']

# choose chart type
selected_chart = st.sidebar.radio("Select Chart Type",
                                   ["Overview", "Individual Pass Map", "Passing Network",
                                    "Shot Map", 'xG Flow', 'Individual Convex Hull',
                                    "Team Convex Hull", "Voronoi Diagram", 'Progressive Passes',
                                    "Passing Sonars", "Team Expected Threat"])

match_data = matches[matches['match_id']==match_id].iloc[0]
st.write(f"### {home_team} {match_data['home_score']}:{match_data['away_score']} {away_team}")

create_plot(selected_chart, match_id, home_team, away_team, competition_stage)

st.image( open('C:/Users/Aleks/WorldCup_Appsb_icon.png', 'rb'), caption='Your Image', use_column_width=True)

# Run the cmd command
# import subprocess
# subprocess.run('streamlit run c:/Users/Aleks/WorldCup_App/app.py', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
