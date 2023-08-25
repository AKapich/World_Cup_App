from statsbombpy  import sb
import pandas as pd
import numpy as np

# Data from World Cup 2022
matches = sb.matches(competition_id=43, season_id=106)
match_dict = {home+' - '+away: match_id
                 for match_id, home, away
                 in zip(matches['match_id'], matches['home_team'], matches['away_team'])}

country_colors = {
    "Poland": "#DC143C",
    "Denmark": "#C60C30",
    "Cameroon": "#007A5E",
    "Japan": "#BC002D",
    "Uruguay": "#0038A8",
    "Argentina": "#75AADB",
    "Iran": "#FFFFFF",
    "Morocco": "#FF0000",
    "Portugal": "#006400",
    "Germany": "#000000",
    "Ecuador": "#e3bc04",
    "France": "#0055A4",
    "Canada": "#FF0000",
    "Netherlands": "#E77E02",
    "Belgium": "#FFD700",
    "Australia": "#eda726",
    "Spain": "#C60C30",
    "Ghana": "#006400",
    "Tunisia": "#E70013",
    "Qatar": "#8B0000",
    "South Korea": "#003478",
    "Croatia": "#FF0000",
    "Senegal": "#048f7c",
    "Saudi Arabia": "#006400",
    "United States": "#B22222",
    "Wales": "#FFD700",
    "Brazil": "#009638",
    "Costa Rica": "#0E2F44",
    "England": "#002366",
    "Mexico": "#006847",
    "Serbia": "#DC143C",
    "Switzerland": "#FF0000"
}

def get_starting_XI(match_id, team):
    events = sb.events(match_id=match_id)
    events = events[events["team"]==team]
    players = events[pd.isna(events["player"])==False]["player"].unique()
    eleven = players[:11] # first eleven

    lineups = sb.lineups(match_id)
    lineup = lineups[team][lineups[team]['player_name'].isin(list(set(eleven)))][['player_name', 'jersey_number']].sort_values('jersey_number')
    lineup.columns = ['Player', 'Number']
    lineup.index = lineup['Number']
    return lineup['Player']

annotation_fix_dict = {
    'Cuccittini': 'Messi',
    'Lucero': 'Molina',
    'Lottin': 'Mbappé',
    'Júnior': 'Vinícius',
    'Junior': 'Neymar',
    'Corrêa': 'Marquinhos',
    'Andrade': 'Richarlison',
    'Belloli': 'Raphinha',
    'Casimiro': 'Casemiro',
    'Lima': 'Paquetá',
    'Tavares': 'Fabinho',
    'Nascimento': 'Bremer',
    'Moraes': 'Ederson',
    'Becker': 'Alisson',
    'Goes': 'Rodrygo',
    'Aveiro': 'Ronaldo',
    'Teixeira': 'Dalot',
    'Sequeira': 'Félix',
    'Leal': 'Godín',
    'Susperreguy': 'Viña',
    'Colmán': 'Bentancur',
    'Dipetta': 'Valverde',
    'Nión': 'Coates',
    'i': 'Busquets',
    'Páez': 'Gavi',
    'Merodio': "Koke",
    'Arthuer': 'Williams',
    'Willemsen': 'Asensio',
    'Mendibil': 'Simón',
    'Carvajal': 'Olmo',
    'Cascante': 'Rodri',
    'Burgos': 'Busquets',
    'Gavira': 'Gavi',
    'Tanco': 'Azpilicueta'
}
