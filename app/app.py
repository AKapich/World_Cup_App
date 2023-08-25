import streamlit as st
from auxiliary import match_dict, matches
from change_charts import create_plot
import os

os.chdir('C:/Users/Aleks/OneDrive/Dokumenty/GitHub/WorldCup_App/app')

st.set_page_config(
        page_title="World Cup 2022 Analytical Tool",
        #page_icon="⚽",
        page_icon='./qatar_icon.ico',
    )


st.title("World Cup 2022 Analytical Tool")
st.markdown("*Platform providing a handful of visualizations for every match of the last World Cup*")
st.markdown("---")

# World Cup Image
st.sidebar.image("./qatar_logo2.png")

# dropdown for choosing the match
st.sidebar.title("Select Match")
selected_match = st.sidebar.selectbox("Match:", match_dict.keys(), index=9)

match_id = match_dict[selected_match]
home_team = selected_match.split(' - ')[0]
away_team = selected_match.split(' - ')[1]
competition_stage = matches[matches['match_id']==match_id].iloc[0]['competition_stage']

# choose chart type
selected_chart = st.sidebar.radio("Select Chart Type",
                                   ["Overview", "Passing Network", "Passing Sonars", "Individual Pass Map",
                                    'Progressive Passes', 'xG Flow', "Shot Map", 'Individual Convex Hull',
                                    "Team Convex Hull", "Voronoi Diagram", "Team Expected Threat"]
                                    )

match_data = matches[matches['match_id']==match_id].iloc[0]
st.write(f"### {home_team} {match_data['home_score']}:{match_data['away_score']} {away_team}")
st.markdown('---')

create_plot(selected_chart, match_id, home_team, away_team, competition_stage)

st.markdown('---')
st.image('./sb_icon.png', caption='App made by Aleks Kapich. Data powered by StatsBomb', use_column_width=True)

# signature
st.sidebar.markdown('---')
col1, col2 = st.columns(2)
with col1:
    st.sidebar.markdown("App made by **Aleks Kapich**")
with col2:
    st.sidebar.write("[Twitter](https://twitter.com/AKapich)")
    st.sidebar.write("[GitHub](https://github.com/AKapich)")
    st.sidebar.write("[Buy Me a Coffee](https://www.buymeacoffee.com/akapich)")

# Run the cmd command
# import subprocess
# subprocess.run('streamlit run c:/Users/Aleks/OneDrive/Dokumenty/GitHub/WorldCup_App/app/app.py',
#  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
