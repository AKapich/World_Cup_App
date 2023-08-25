from statsbombpy import sb

from mplsoccer.pitch import Pitch, VerticalPitch
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

from matplotlib.lines import Line2D
from scipy.spatial import ConvexHull
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

from auxiliary import country_colors, annotation_fix_dict



def passes_heatmap(matchid, player, home_team, away_team, competition_stage):
    # Passes from the particular match
    passes = sb.events(match_id=matchid, split=True, flatten_attrs=False)["passes"]
    # Of the particular player
    passes_player = passes[passes.player==player]
    passes_player.index = range(len(passes_player))

    fig ,ax = plt.subplots(figsize=(13, 8),constrained_layout=False, tight_layout=True)
    fig.set_facecolor('#55647d')
    ax.patch.set_facecolor('#55647d')
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#55647d', line_color='#c7d5cc')
    #Draw the pitch on the ax figure
    pitch.draw(ax=ax)

    passes_player[['start_x', 'start_y']] = pd.DataFrame(passes_player['location'].tolist(),
                                                        index=passes_player.index)

    for i in range(len(passes_player)):
        plt.plot((passes_player["start_x"][i], passes_player["pass"][i]['end_location'][0]),
                (passes_player["start_y"][i], passes_player["pass"][i]['end_location'][1]),
                color='#d9ca2b')
        plt.scatter(passes_player["location"][i][0], passes_player["location"][i][1],
                    color='#d9ca2b', marker='H')
        
    #Heatmap
    kde = sns.kdeplot(
            x=passes_player["start_x"],
            y=passes_player["start_y"],
            fill = True,
            shade_lowest=False,
            alpha=.45,
            n_levels=10,
            cmap = 'magma'
    )
    plt.xlim(0,120)
    plt.ylim(80,0)
    plt.title(f'{player}: Pass Map\n{home_team} vs {away_team}\nWorld Cup 2022 {competition_stage}',
            color='white', size=20,  fontweight="bold", family="monospace")
#     fig.text(.5, .0001, "Data source: StatsBomb. Created by @AKapich",
#             fontstyle='italic', fontsize=12, fontfamily='Monospace', color='w', ha='center')
    
    return fig


def shot_map(match_id, home_team, away_team, competition_stage):

        outcome_dict = {
        "Blocked":"s",
        "Goal" : "*",
        "Off T": "X",
        "Post": "P",
        "Saved":"o",
        "Wayward":"v",
        "Saved Off T":"h",
        "Saved to Post":"p"
        }

        fig,ax = plt.subplots(figsize=(6, 9.75),constrained_layout=False, tight_layout=True)
        fig.set_facecolor('#55647d')
        ax.patch.set_facecolor('#55647d')
        # vertical pitch!
        pitch = VerticalPitch(pitch_type='statsbomb', pitch_color='#55647d', line_color='#c7d5cc')
        pitch.draw(ax=ax)

        shots = sb.events(match_id=match_id, split=True, flatten_attrs=False)["shots"]

        shots[['start_x', 'start_y']] = pd.DataFrame(shots['location'].tolist(), index=shots.index)
        shots.index = range(len(shots))

        for i in range(len(shots)):
                if shots.iloc[i].team==home_team:
                        plt.scatter(shots["start_y"][i], shots["start_x"][i],
                                color=country_colors[home_team],
                                edgecolors='black',
                                marker=outcome_dict[shots["shot"][i]["outcome"]["name"]],
                                s=120)
                else:
                        # vertical pitch, therefore y and coords exchanged
                        plt.scatter(80-shots["start_y"][i], 120-shots["start_x"][i],
                                color=country_colors[away_team],
                                edgecolors='black',
                                marker=outcome_dict[shots["shot"][i]["outcome"]["name"]],
                                s=120)   

        legend_elements=[Line2D([], [], marker='s', linestyle='None', markersize=10, label='Blocked'),
                        Line2D([], [], marker='*', linestyle='None', markersize=10, label='Goal'),
                        Line2D([], [], marker='X', linestyle='None', markersize=10, label='Off Target'),
                        Line2D([], [], marker='P', linestyle='None', markersize=10, label='Post'),
                        Line2D([], [], marker='v', linestyle='None', markersize=10, label='Wayward'),
                        Line2D([], [], marker='o', linestyle='None', markersize=10, label='Saved'),
                        Line2D([], [], marker='h', linestyle='None', markersize=10, label='Saved Off Target'),
                        Line2D([], [], marker='p', linestyle='None', markersize=10, label='Saved To Post')]
        plt.legend(handles=legend_elements, loc='center left')
        plt.text(51, 62, home_team, fontsize = 20, color=country_colors[home_team])
        plt.text(51, 55, away_team, fontsize = 20, color=country_colors[away_team])

        plt.title(f'Shot Map: {home_team} vs {away_team}\nWorld Cup 2022 {competition_stage}',
                color='white', size=20,  fontweight="bold", family="monospace")
        # fig.text(.5, .01, "Data source: StatsBomb. Created by @AKapich",
        #         fontstyle='italic', fontsize=12, fontfamily='Monospace', color='w', ha='center')
        return fig


def passing_network(match_id, team, home_team, away_team, competition_stage):
        passes = sb.events(match_id=match_id, split=True, flatten_attrs=False)["passes"]
        passes = passes[passes.team==team]
        passes.index = range(len(passes))

        # We filter out only successful passes
        passes["recipient"] = [passes["pass"][i]["recipient"]["name"]
                        if list(passes.iloc[i]["pass"].keys())[0]=="recipient"
                        else None
                        for i in range(len(passes))]
        passes = passes[passes["recipient"]!=None]

        # Chart may be created for the time until the first substitution
        events = sb.events(match_id=match_id)
        subs = events[pd.isna(events["substitution_outcome"])==False]
        min_threshold = min(subs["minute"])
        sec_threshold = min(subs["second"])
        
        passes = passes[(passes["minute"]<min_threshold) |
                        ((passes["minute"]==min_threshold) & (passes["second"]<sec_threshold))]

        passes["x"] = [location[0] for location in passes["location"]]
        passes["y"] = [location[1] for location in passes["location"]]
        average_location = passes.groupby('player').agg({'x': ['mean'], 'y': ['mean','count']})
        average_location.columns = ['x', 'y', 'count']

        passes_between = passes.groupby(['player', 'recipient']).id.count().reset_index()
        
        passes_between = passes_between.rename(columns={'id': 'pass_count'})

        # 'average_location' index is in fact 'player' column, therefore below right_index=True (we merge by it)
        
        passes_between = passes_between.merge(average_location,
                                        left_on="player", right_index=True)
        passes_between = passes_between.merge(average_location,
                                        left_on='recipient', right_index=True, suffixes=('','_end'))
        # setting a threshold for minimum 2 passes between players to be noted on the chart
        passes_between = passes_between.loc[(passes_between['pass_count']>1)]

        fig ,ax = plt.subplots(figsize=(13, 8),constrained_layout=False, tight_layout=True)
        fig.set_facecolor('#55647d')
        ax.patch.set_facecolor('#55647d')
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#55647d', line_color='#c7d5cc')
        pitch.draw(ax=ax)

        arrows = pitch.arrows(passes_between.x, passes_between.y,
                        passes_between.x_end, passes_between.y_end,
                        color='black',
                        alpha=pd.to_numeric(passes_between["pass_count"], downcast="float")/max(passes_between["pass_count"]),
                        ax=ax)
        nodes = pitch.scatter(average_location.x, average_location.y,
                        s = pd.to_numeric(average_location["count"], downcast="float")*25,
                        #alpha = pd.to_numeric(average_location["count"], downcast="float")/max(average_location["count"]),
                        color=country_colors[team], edgecolors='black',
                        ax=ax)

        for index, row in average_location.iterrows():
                if row.name.split(" ")[-1] not in annotation_fix_dict.keys():
                        if team not in ['Spain', 'Mexico']:
                                annotation_text = row.name.split(" ")[-1] 
                        else:
                                annotation_text = row.name.split(" ")[-2] 
                                if annotation_text in annotation_fix_dict.keys():
                                        annotation_text = annotation_fix_dict[annotation_text]
                else:
                        annotation_text = annotation_fix_dict[row.name.split(" ")[-1]]
                
                pitch.annotate(annotation_text, xy=(row.x, row.y+3),
                                c='white', va='center', ha='center',
                                size=10, fontweight='bold',
                                ax=ax)

        ax.set_title(f"{home_team} vs {away_team}, World Cup {competition_stage} | Until First Sub",
                fontsize=18, color="w", fontfamily="Monospace", fontweight='bold', pad=-8)
       
        return fig
                

def xG_flow(match_id, home_team, away_team, competition_stage):
        shots = sb.events(match_id=match_id, split=True, flatten_attrs=False)["shots"]
        shots.index = range(len(shots))

        shots["xG"] = [shots["shot"][i]["statsbomb_xg"] for i in range(len(shots))]
        shots["outcome"] = [shots["shot"][i]["outcome"]["name"] for i in range(len(shots))]
        shots = shots[["minute", "second", "team", "player", "xG", "outcome"]]

        # a - away, h - home
        a_xG = [0]
        h_xG= [0]
        a_min = [0]
        h_min = [0]

        for i in range(len(shots)):
                if shots['team'][i]==away_team:
                        a_xG.append(shots['xG'][i])
                        a_min.append(shots['minute'][i])
                if shots['team'][i]==home_team:
                        h_xG.append(shots['xG'][i])
                        h_min.append(shots['minute'][i])
                
        def cumsum(the_list):
                return [sum(the_list[:i+1]) for i in range(len(the_list))]
        
        a_xG = cumsum(a_xG)
        h_xG = cumsum(h_xG)

        # make the plot finish at the end of an axis for both teams
        if(a_min[-1]>h_min[-1]):
                h_min.append(a_min[-1])
                h_xG.append(h_xG[-1])
        elif (h_min[-1]>a_min[-1]):
                a_min.append(h_min[-1])
                a_xG.append(a_xG[-1])

        a_xG_total = round(a_xG[-1], 2)
        h_xG_total = round(h_xG[-1], 2)

        mpl.rcParams['xtick.color'] = 'white'
        mpl.rcParams['ytick.color'] = 'white'

        fig, ax = plt.subplots(figsize = (10,5))
        fig.set_facecolor('#55647d')
        ax.patch.set_facecolor('#55647d')

        ax.step(x=a_min, y=a_xG, color=country_colors[away_team], where='post', linewidth=4)
        ax.step(x=h_min, y=h_xG, color=country_colors[home_team], where='post', linewidth=4)
        plt.xticks([0,15,30,45,60,75,90,105,120])
        plt.xlabel('Minute',fontname='Monospace',color='white',fontsize=16)
        plt.ylabel('xG',fontname='Monospace',color='white',fontsize=16)

        ax.grid(ls='dotted',lw=.5,color='lightgrey',axis='y',zorder=1)
        # remove the frame of the plot
        spines = ['top','bottom','left','right']
        for x in spines:
                if x in spines:
                        ax.spines[x].set_visible(False)
                
        ax.margins(x=0)
        plt.axhline(h_xG_total, color=country_colors[home_team], linestyle='--')
        plt.axhline(a_xG_total, color=country_colors[away_team], linestyle='--')
        h_text = str(h_xG_total)+' '+home_team
        a_text = str(a_xG_total)+' '+away_team
        plt.text(5, h_xG_total+0.05, h_text, fontsize = 10, color=country_colors[home_team])
        plt.text(5, a_xG_total+0.05, a_text, fontsize = 10, color=country_colors[away_team])

        ax.set_title(f"{home_team} vs {away_team}, World Cup {competition_stage}\nxG Flow",
                fontsize=18, color="w", fontfamily="Monospace", fontweight='bold', pad=-8)
        return fig


def single_convex_hull(match_id, player, team, home_team, away_team, competition_stage):
        events = sb.events(match_id=match_id)

        # single player
        fig ,ax = plt.subplots(figsize=(13, 8),constrained_layout=False, tight_layout=True)
        fig.set_facecolor('#55647d')
        ax.patch.set_facecolor('#55647d')
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#55647d', line_color='#c7d5cc')
        pitch.draw(ax=ax)

        events = events[pd.isna(events["location"])==False]
        events['x'] = [location[0] for location in events.loc[:,"location"]]
        events['y'] = [location[1] for location in events.loc[:,"location"]]
        player_events = events[events["player"]==player]
        before_filter = player_events

        # eliminate points that lay over 1.5 standard deviations away from the mean coords
        # zscore tells how many standard deviations away the value is from the mean
        player_events = player_events[np.abs(stats.zscore(player_events[['x','y']])) < 1.5]
        # where the zscore is greater than 1.5 values are set to NaN
        player_events = player_events[['x','y']][(pd.isna(player_events['x'])==False)&(pd.isna(player_events['y'])==False)]
        points = player_events[['x','y']].values

        plt.scatter(before_filter.x, before_filter.y, color=country_colors[team])
        plt.scatter(player_events.x, player_events.y, color='yellow')
        # create a convex hull
        hull = ConvexHull(player_events[['x','y']])
        for i in hull.simplices:
                plt.plot(points[i, 0], points[i, 1], country_colors[team])
                plt.fill(points[hull.vertices,0], points[hull.vertices,1], c=country_colors[team], alpha=0.03)

        ax.set_title(f"{home_team} vs {away_team}, World Cup {competition_stage}\nConvex Hull of {player} actions",
                fontsize=18, color="w", fontfamily="Monospace", fontweight='bold', pad=-8)

        return fig


def team_convex_hull(match_id, team, home_team, away_team, competition_stage):
        events = sb.events(match_id=match_id)
        events = events[events["team"]==team]
        players = events[pd.isna(events["player"])==False]["player"].unique()
        starters = players[:11] # first eleven

        events = events[pd.isna(events["location"])==False]
        events['x'] = [location[0] for location in events.loc[:,"location"]]
        events['y'] = [location[1] for location in events.loc[:,"location"]]

        # for every starter
        fig ,ax = plt.subplots(figsize=(13, 8),constrained_layout=False, tight_layout=True)
        fig.set_facecolor('#55647d')
        ax.patch.set_facecolor('#55647d')
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#55647d', line_color='#c7d5cc')
        pitch.draw(ax=ax)

        colours = ['#eb4034', '#ebdb34', '#98eb34', '#34eb77', '#be9cd9', '#5797e6',
                   '#262729', '#de34eb', '#eb346b', '#34ebcc', '#dbd5d5']
        colourdict = dict(zip(starters, colours))

        for player in starters:
                tempdf = events[events["player"]==player]
                # threshold of 0.75 sd
                tempdf = tempdf[np.abs(stats.zscore(tempdf[['x','y']])) < 0.75]
                
                tempdf = tempdf[['x','y']][(pd.isna(tempdf['x'])==False)&(pd.isna(tempdf['y'])==False)]
                points = tempdf[['x','y']].values
                
                pitch.annotate(player, xy=(np.mean(tempdf.x), np.mean(tempdf.y)),
                                c=colourdict[player], va='center', ha='center',
                                size=10, fontweight='bold',
                                ax=ax)
        
                try:
                        hull = ConvexHull(tempdf[['x','y']])
                except:
                        pass

                try:
                        for i in hull.simplices:
                                plt.plot(points[i, 0], points[i, 1], colourdict[player])
                                plt.fill(points[hull.vertices,0], points[hull.vertices,1], c=colourdict[player], alpha=0.03)
                except:
                        pass

        ax.set_title(f"{home_team} vs {away_team}, World Cup {competition_stage}\nConvex Hulls of actions",
                fontsize=18, color="w", fontfamily="Monospace", fontweight='bold', pad=-8)
        
        return fig


def voronoi(match_id, home_team, away_team, competition_stage):
        df = sb.events(match_id=match_id)

        subs = df[pd.isna(df["substitution_outcome"])==False]
        min_threshold = min(subs["minute"])
        sec_threshold = min(subs["second"])
        df = df[(df["minute"]<min_threshold) | ((df["minute"]==min_threshold) & (df["second"]<sec_threshold))]
        df = df[pd.isna(df["location"])==False]
        df["x"] = [location[0] for location in df["location"]]
        df["y"] = [location[1] for location in df["location"]]
        # average location
        df = df.groupby(['player', 'team']).agg({'x': ['mean'], 'y': ['mean']})
        df.columns = ['x', 'y']
        df=df.reset_index()
        # the column responsible for voronoi division must be boolean
        df['team_id'] = df['team']==home_team

        # reverse the coords of one team
        for i in range(len(df)):
                if not (df['team_id'][i]):
                        df['x'][i] = 120-df['x'][i]
                        df['y'][i] = 80-df['y'][i]

        fig ,ax = plt.subplots(figsize=(13, 8),constrained_layout=False, tight_layout=True)
        fig.set_facecolor('#55647d')
        ax.patch.set_facecolor('#55647d')
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#55647d', line_color='#c7d5cc')
        pitch.draw(ax=ax)

        pitch.voronoi(df.x, df.y, df.team)
        team1,team2 = pitch.voronoi(df.x, df.y, df.team_id)

        t1 = pitch.polygon(team1, ax=ax, fc=country_colors[home_team], ec='white', lw=3, alpha=0.2)
        t2 = pitch.polygon(team2, ax=ax, fc=country_colors[away_team], ec='white', lw=3, alpha=0.2)

        # Plot players
        for i in range(len(df['x'])):
                if df['team'][i]==home_team:
                        pitch.scatter(df['x'][i],df['y'][i],ax=ax,color=country_colors[home_team])
                        
                if df['team'][i]==away_team:
                        pitch.scatter(df['x'][i],df['y'][i],ax=ax,color=country_colors[away_team])
                        
                
                if df['player'][i].split(" ")[-1] not in annotation_fix_dict.keys():
                        if df['team'][i] not in ['Spain', 'Mexico']:
                                annotation_text = df['player'][i].split(" ")[-1]
                        else:
                                annotation_text = df['player'][i].split(" ")[-2]
                                if annotation_text in annotation_fix_dict.keys():
                                        annotation_text = annotation_fix_dict[annotation_text]
                else:
                        annotation_text = annotation_fix_dict[df['player'][i].split(" ")[-1]]
                        
                pitch.annotate(annotation_text, xy=(df['x'][i], df['y'][i]+2),
                                c='black', va='center', ha='center',
                                size=10, fontweight='bold',
                                ax=ax)

        ax.set_title(f"{home_team} vs {away_team}, World Cup {competition_stage}\nVoronoi diagram (until 1st sub)",
                fontsize=18, color="w", fontfamily="Monospace", fontweight='bold', pad=-8)

        return fig


def progressive_passes(match_id, player, team, home_team, away_team, competition_stage):
        passes = sb.events(match_id=match_id, split=True, flatten_attrs=False)["passes"]
        df = passes[passes.team==team]
        df = df[df.player==player]
        df.index = range(len(df))

        df[['start_x', 'start_y']] = pd.DataFrame(df['location'].tolist(), index=df.index)
        df["end_x"] = [df["pass"][i]['end_location'][0] for i in range(len(df))]
        df["end_y"] = [df["pass"][i]['end_location'][1] for i in range(len(df))]
        df['beginning'] = np.sqrt(np.square(120-df['start_x'])+np.square(80-df['start_y']))
        df['end'] = np.sqrt(np.square(120-df['end_x'])+np.square(80-df['end_y']))
        # according to definiton pass is progressive if it brings the ball closer to the goal by at least 25%
        df['progressive'] = df['end'] < 0.75*df['beginning']

        fig ,ax = plt.subplots(figsize=(13, 8),constrained_layout=False, tight_layout=True)
        fig.set_facecolor('#55647d')
        ax.patch.set_facecolor('#55647d')
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#55647d', line_color='#c7d5cc')
        pitch.draw(ax=ax)

        df = df[df['progressive']==True]
        df.index = range(len(df))
        pitch.lines(xstart=df["start_x"], ystart=df["start_y"], xend=df["end_x"], yend=df["end_y"],
                ax=ax, comet=True, color=country_colors[team])

        ax.set_title(f"{home_team} vs {away_team}, World Cup {competition_stage}\n{player} progressive passes",
                fontsize=18, color="w", fontfamily="Monospace", fontweight='bold', pad=-8)

        return fig


def passing_sonars(match_id, team, home_team, away_team, competition_stage):
        # passing sonars
        passes = sb.events(match_id=match_id, split=True, flatten_attrs=False)["passes"]
        df = passes[passes['team']==team]
        df = df[['pass', 'player']]
        df.index = range(len(df))
        df['angle'] = [df['pass'][i]['angle'] for i in range(len(df))]
        df['length'] = [df['pass'][i]['length'] for i in range(len(df))]

        # we divide into 20 bins
        df['angle_bin'] = pd.cut(df['angle'], bins=np.linspace(-np.pi,np.pi,21),
                                labels=False, include_lowest=True)

        pass_sonar = df.groupby(["player", "angle_bin"], as_index=False)
        pass_sonar = pass_sonar.agg({"length": "mean"})
        # count occurances of passes in particular bins
        counter  = df.groupby(['player', 'angle_bin']).size().to_frame(name = 'amount').reset_index()
        pass_sonar = pd.concat([pass_sonar, counter["amount"]], axis=1)

        # average location of players
        passes["x"] = [location[0] for location in passes["location"]]
        passes["y"] = [location[1] for location in passes["location"]]
        passes = passes[passes['team']==team]
        average_location = passes.groupby('player').agg({'x': ['mean'], 'y': ['mean']})
        average_location.columns = ['x', 'y']

        pass_sonar = pass_sonar.merge(average_location, left_on="player", right_index=True)

        lineups = sb.lineups(match_id=match_id)[team]
        lineups['starter'] = [lineups['positions'][i][0]['start_reason']=='Starting XI'
                        if lineups['positions'][i]!=[]
                        else None
                        for i in range(len(lineups))]
        lineups = lineups[lineups["starter"]==True]
        # we need the starting lineups
        startingXI = list(lineups.player_name)
        pass_sonar = pass_sonar[pass_sonar['player'].isin(startingXI)]
        pass_sonar

        #the pitch
        fig ,ax = plt.subplots(figsize=(13, 8),constrained_layout=False, tight_layout=True)
        fig.set_facecolor('#55647d')
        ax.patch.set_facecolor('#55647d')
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#55647d', line_color='#c7d5cc')
        pitch.draw(ax=ax)

        #drawing sonars
        import matplotlib.patches as pat
        for player in startingXI:
                # _ is the index of the row
                for _, row in pass_sonar[pass_sonar.player == player].iterrows():
                        #Start degree of direction 1
                        theta_left_start = 180

                        #Color coding by distance
                        color = "darkred"
                        if row.amount < 3:
                                color = "gold"
                        elif row.amount < 5:
                                color = "darkorange"
                        #Calculate degree in matplotlib figure
                        theta_left = theta_left_start - (360 / 20) * (row.angle_bin)
                        theta_right = theta_left - (360 / 20)
                        
                        pass_wedge = pat.Wedge(
                        center=(row.x, row.y),
                        r=row.length*0.16,
                        theta1=theta_right,
                        theta2=theta_left,
                        facecolor=color,
                        edgecolor="black",
                        alpha=0.6
                        )
                        ax.add_patch(pass_wedge)

        for index, row in average_location.iterrows():
                if row.name in startingXI:
                        if row.name.split(" ")[-1] not in annotation_fix_dict.keys():
                                if team not in ['Spain', 'Mexico']:
                                        annotation_text = row.name.split(" ")[-1] 
                                else:
                                        annotation_text = row.name.split(" ")[-2] 
                                        if annotation_text in annotation_fix_dict.keys():
                                                annotation_text = annotation_fix_dict[annotation_text]
                        else:
                                annotation_text = annotation_fix_dict[row.name.split(" ")[-1]]

                        pitch.annotate(annotation_text, xy=(row.x, row.y+4.5),
                                c='white', va='center', ha='center',
                                size=9, fontweight='bold',
                                ax=ax)

        ax.set_title(f"{home_team} vs {away_team}, World Cup {competition_stage}\n{team} passing sonars (starting XI)",
                fontsize=18, color="w", fontfamily="Monospace", fontweight='bold', pad=-8)

        return fig


def expected_threat(match_id, team, home_team, away_team, competition_stage):
        # Import xT Grid 
        #xT = pd.read_csv("./xT_grid.csv", header=None)
        xT = pd.read_csv("https://raw.githubusercontent.com/AKapich/WorldCup_App/main/app/xT_Grid.csv", header=None)
        xT = np.array(xT)
        xT_rows, xT_cols = xT.shape # amount of grids = amount of bins

        # creating xT column
        df = sb.events(match_id=match_id, split=True, flatten_attrs=False)["passes"]
        df.index = range(len(df))
        df["start_x"] = [location[0] for location in df["location"]]
        df["start_y"] = [location[1] for location in df["location"]]
        df["end_x"] = [df["pass"][i]['end_location'][0] for i in range(len(df))]
        df["end_y"] = [df["pass"][i]['end_location'][1] for i in range(len(df))]
        df['start_x_bin'] = pd.cut(df['start_x'], bins=xT_cols, labels=False)
        df['start_y_bin'] = pd.cut(df['start_y'], bins=xT_rows, labels=False)
        df['end_x_bin'] = pd.cut(df['end_x'], bins=xT_cols, labels=False)
        df['end_y_bin'] = pd.cut(df['end_x'], bins=xT_rows, labels=False)
        df['start_zone_value'] = df[['start_x_bin', 'start_y_bin']].apply(lambda z: xT[z[1]][z[0]], axis=1)
        df['end_zone_value'] = df[['end_x_bin', 'end_y_bin']].apply(lambda z: xT[z[1]][z[0]], axis=1)
        df['xT'] = df['start_zone_value']-df['end_zone_value']

        # filter down to one team
        df = df[df['team']==team]
        dfxT = df.groupby('player').agg({'xT':'sum'})

        lineups = sb.lineups(match_id=match_id)[team]
        lineups['starter'] = [lineups['positions'][i][0]['start_reason']=='Starting XI'
                        if lineups['positions'][i]!=[]
                        else None
                        for i in range(len(lineups))]
        lineups = lineups[lineups["starter"]==True]
        # we need the starting lineups
        startingXI = list(lineups.player_name)

        passes = sb.events(match_id=match_id, split=True, flatten_attrs=False)["passes"]
        passes["x"] = [location[0] for location in passes["location"]]
        passes["y"] = [location[1] for location in passes["location"]]
        passes = passes[passes['team']==team]
        average_location = passes.groupby('player').agg({'x': ['mean'], 'y': ['mean']})
        average_location.columns = ['x', 'y']
        average_location

        df = dfxT.merge(average_location, left_on="player", right_index=True)

        fig,ax = plt.subplots(figsize=(4.5, 7.5),constrained_layout=False, tight_layout=True)
        fig.set_facecolor('#55647d')
        ax.patch.set_facecolor('#55647d')
        pitch = VerticalPitch(pitch_type='statsbomb', pitch_color='#55647d', line_color='#c7d5cc')
        pitch.draw(ax=ax)

        df = df[df.index.isin(startingXI)]
        norm = mpl.colors.Normalize(vmin=-0.4, vmax=0.4) # normalization to fix (boundaries)
        cmap = plt.cm.hot

        nodes = pitch.scatter(df.x, df.y,
                        s = 975,
                        color=cmap(norm(df.xT)),
                        marker='H',
                        edgecolors='black',
                        ax=ax)

        for index, row in df.iterrows():
                if row.name.split(" ")[-1] not in annotation_fix_dict.keys():
                        if team not in ['Spain', 'Mexico']:
                                        annotation_text = row.name.split(" ")[-1] 
                        else:
                                annotation_text = row.name.split(" ")[-2] 
                                if annotation_text in annotation_fix_dict.keys():
                                        annotation_text = annotation_fix_dict[annotation_text]
                else:
                        annotation_text = annotation_fix_dict[row.name.split(" ")[-1]]

                pitch.annotate(annotation_text, xy=(row.x-5.5, row.y),
                        c='white', va='center', ha='center',
                        size=7.5, fontweight='bold',
                        ax=ax)
                pitch.annotate(round(row.xT,2), xy=(row.x, row.y),
                        c='black', va='center', ha='center',
                        size=7.5, fontweight='bold',
                        ax=ax)
                
        ax.set_title(f"{home_team} vs {away_team}\nWorld Cup {competition_stage}\n{team} xT (starting XI)",
                fontsize=13.5, color="w", fontfamily="Monospace", fontweight='bold', pad=-8)
        
        return fig