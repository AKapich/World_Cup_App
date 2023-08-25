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
    "Senegal": "#008000",
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

xT = np.array([[0.00638303, 0.00779616, 0.00844854, 0.00977659, 0.01126267,
        0.01248344, 0.01473596, 0.0174506 , 0.02122129, 0.02756312,
        0.03485072, 0.0379259 ],
       [0.00750072, 0.00878589, 0.00942382, 0.0105949 , 0.01214719,
        0.0138454 , 0.01611813, 0.01870347, 0.02401521, 0.02953272,
        0.04066992, 0.04647721],
       [0.0088799 , 0.00977745, 0.01001304, 0.01110462, 0.01269174,
        0.01429128, 0.01685596, 0.01935132, 0.0241224 , 0.02855202,
        0.05491138, 0.06442595],
       [0.00941056, 0.01082722, 0.01016549, 0.01132376, 0.01262646,
        0.01484598, 0.01689528, 0.0199707 , 0.02385149, 0.03511326,
        0.10805102, 0.25745362],
       [0.00941056, 0.01082722, 0.01016549, 0.01132376, 0.01262646,
        0.01484598, 0.01689528, 0.0199707 , 0.02385149, 0.03511326,
        0.10805102, 0.25745362],
       [0.0088799 , 0.00977745, 0.01001304, 0.01110462, 0.01269174,
        0.01429128, 0.01685596, 0.01935132, 0.0241224 , 0.02855202,
        0.05491138, 0.06442595],
       [0.00750072, 0.00878589, 0.00942382, 0.0105949 , 0.01214719,
        0.0138454 , 0.01611813, 0.01870347, 0.02401521, 0.02953272,
        0.04066992, 0.04647721],
       [0.00638303, 0.00779616, 0.00844854, 0.00977659, 0.01126267,
        0.01248344, 0.01473596, 0.0174506 , 0.02122129, 0.02756312,
        0.03485072, 0.0379259 ]])