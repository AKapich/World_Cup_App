import streamlit as st
import pandas as pd
from statsbombpy import sb
import viz
from auxiliary import matches


def overview(match_id, home_team, away_team, competition_stage):
        match_data = matches[matches['match_id']==match_id].iloc[0]
        st.write(f"Stage: {match_data['competition_stage']}")
        st.write(f"Stadium: {match_data['stadium']}")
        st.write(f"Referee: {match_data['referee']}")
        st.write(f"Manager of {home_team}: {match_data['home_managers']}")
        st.write(f"Manager of {away_team}: {match_data['away_managers']}")
        st.markdown('---')
        # Lineups 
        from auxiliary import get_starting_XI
        home_lineup = get_starting_XI(match_id, home_team)
        away_lineup = get_starting_XI(match_id, away_team)
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"{home_team} - Starting XI")
            st.write(home_lineup.head(11), index=False)
        with col2:
            st.write(f"{away_team} - Starting XI")
            st.write(away_lineup.head(11), index=False)


def ipm(match_id, home_team, away_team, competition_stage):
        players_h = list(set(sb.events(match_id=match_id, split=True, flatten_attrs=False)["passes"].query(f"team=='{home_team}'")["player"]))
        players_a = list(set(sb.events(match_id=match_id, split=True, flatten_attrs=False)["passes"].query(f"team=='{away_team}'")["player"]))
        # First passmap
        selected_player_1 = st.selectbox(f"Player: {home_team}", players_h)
        st.subheader("Passmap")
        st.pyplot(viz.passes_heatmap(match_id, selected_player_1, home_team, away_team, competition_stage))
        # Second passmap
        selected_player_2 = st.selectbox(f"Player: {away_team}", players_a)
        st.subheader("Passmap")
        st.pyplot(viz.passes_heatmap(match_id, selected_player_2, home_team, away_team, competition_stage))


def pn(match_id, home_team, away_team, competition_stage):
        # First network
        st.subheader(f"{home_team}: Passing Network")
        st.pyplot(viz.passing_network(match_id, home_team, home_team, away_team, competition_stage))
        # Second network
        st.subheader(f"{away_team}: Passing Network")
        st.pyplot(viz.passing_network(match_id, away_team, home_team, away_team, competition_stage))


def sm(match_id, home_team, away_team, competition_stage):
        # Shot map
        st.subheader("Shot map")
        st.pyplot(viz.shot_map(match_id, home_team, away_team, competition_stage))


def xgf(match_id, home_team, away_team, competition_stage):
        st.subheader('xG Flow')
        st.pyplot(viz.xG_flow(match_id, home_team, away_team, competition_stage))


def ich(match_id, home_team, away_team, competition_stage):
        st.write('''Every point represents one action. Actions within the range of the convex hull took place less
            than 1.5 standard deviations away from the mean position of the selected player''')
        events = sb.events(match_id=match_id)
        # we need to filter out players who have less than 4 actions, it would be impossible to create convex hull
        # it could have been solved inside viz.py in the function, where just the actions would be plotted without the convex hull
        players_h = events[pd.isna(events["location"])==False][events['team']==home_team]['player'].value_counts()
        players_h = list(players_h[players_h>=4].index)
        players_a = events[pd.isna(events["location"])==False][events['team']==away_team]['player'].value_counts()
        players_a = list(players_a[players_a>=4].index)

        # First convex hull
        selected_player_1 = st.selectbox(f"Player: {home_team}", players_h)
        st.subheader("Convex Hull of actions")
        st.pyplot(viz.single_convex_hull(match_id, selected_player_1, home_team, home_team, away_team, competition_stage))
        # Second convex hull
        selected_player_2 = st.selectbox(f"Player: {away_team}", players_a)
        st.subheader("Convex Hull of actions")
        st.pyplot(viz.single_convex_hull(match_id, selected_player_2, away_team, home_team, away_team, competition_stage))


def tch(match_id, home_team, away_team, competition_stage):
        st.subheader(f"{home_team}: Convex Hull of actions")
        st.pyplot(viz.team_convex_hull(match_id, home_team, home_team, away_team, competition_stage))
        st.subheader(f"{away_team}: Convex Hull of actions")
        st.pyplot(viz.team_convex_hull(match_id, away_team, home_team, away_team, competition_stage))


def vd(match_id, home_team, away_team, competition_stage):
        st.subheader('Voronoi Diagram')
        st.pyplot(viz.voronoi(match_id, home_team, away_team, competition_stage))


def pp(match_id, home_team, away_team, competition_stage):
        players_h = list(set(sb.events(match_id=match_id, split=True, flatten_attrs=False)["passes"].query(f"team=='{home_team}'")["player"]))
        players_a = list(set(sb.events(match_id=match_id, split=True, flatten_attrs=False)["passes"].query(f"team=='{away_team}'")["player"]))
        # First passmap
        selected_player_1 = st.selectbox(f"Player: {home_team}", players_h)
        st.subheader("Progressive passes")
        st.pyplot(viz.progressive_passes(match_id, selected_player_1, home_team, home_team, away_team, competition_stage))
        # Second passmap
        selected_player_2 = st.selectbox(f"Player: {away_team}", players_a)
        st.subheader("Passmap")
        st.pyplot(viz.progressive_passes(match_id, selected_player_2, away_team, home_team, away_team, competition_stage))


def ps(match_id, home_team, away_team, competition_stage):
        st.write('''*The darker the sonar, the more passes the player attempted in the direction.
                 Length of the sonar indicates the average pass length for the given direction.*''')
        st.subheader("Passing sonars")
        st.pyplot(viz.passing_sonars(match_id, home_team, home_team, away_team, competition_stage))
        st.subheader("Passing sonars")
        st.pyplot(viz.passing_sonars(match_id, away_team, home_team, away_team, competition_stage))


def tet(match_id, home_team, away_team, competition_stage):
       st.subheader('Expected Threat')
       selected_team = st.selectbox('Team', [home_team, away_team])
       st.pyplot(viz.expected_threat(match_id, selected_team, home_team, away_team, competition_stage))


def ph(match_id, home_team, away_team, competition_stage):
       st.subheader('Pressure Heatmap')
       st.pyplot(viz.pressure_heatmap(match_id, home_team, home_team, away_team, competition_stage))
       st.subheader('Pressure Heatmap')
       st.pyplot(viz.pressure_heatmap(match_id, away_team, home_team, away_team, competition_stage))


fun_dict = {
        'Overview': overview,
        'Individual Pass Map': ipm,
        'Passing Network': pn,
        'Shot Map': sm,
        'xG Flow': xgf,
        'Individual Convex Hull': ich,
        'Team Convex Hull': tch,
        'Voronoi Diagram': vd,
        'Progressive Passes': pp,
        'Passing Sonars': ps,
        'Team Expected Threat': tet,
        'Pressure Heatmap': ph
    }

def create_plot(selected_chart, match_id, home_team, away_team, competition_stage):
    current_fun = fun_dict[selected_chart]
    current_fun(match_id, home_team, away_team, competition_stage)
    