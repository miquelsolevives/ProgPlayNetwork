import pandas as pd
import numpy as np # numerical python package
from progplaynetwork import pitch as ppn_pitch
from scipy.spatial import ConvexHull

column_basics= ['timestamp', 'period', 'type', 'pass_outcome', 'pass_type', 'dribble_outcome',
         'player', 'origin_zone', 'pass_recipient', 'dest_zone', 'height_prog', 'possession', 'orig_x', 'orig_y',
         'is_tracked', 'opp_def_type', 'block_rupture_play', 'play_pattern']

def get_event(idx):
    """ get Dataframe row instead of the Series row (for bettter vis) """
    sel= match_events[match_events.id==match_events.iloc[idx].id] [column_basics]
    return sel


def get_formation( team_dict):
    """ """
    return team_dict['formation']


def get_match_lineup( team, lineups):
    """ """
    team_lineup= lineups[ lineups.team==team]['tactics'].iloc[0]
    formation= team_lineup['formation']
    lineup= pd.DataFrame.from_dict( team_lineup['lineup'])
    players= {}
    for i in range(len(lineup)):
        key = lineup.player[i]['name']
        val_num = lineup.jersey_number[i]
        val_pos = lineup.position[i]['name']
        players[key] = [val_num, val_pos]
    
    return formation, players

    
def get_match_players( dict_home, dict_away, subs, team_home):
    """  """
    lineup_dict_home= pd.DataFrame.from_dict(dict_home['lineup'])
    lineup_dict_away= pd.DataFrame.from_dict(dict_away['lineup'])
    home_players= {}
    away_players= {}
    home_GK= ''
    away_GK= ''
    
    """ LineUp: """
    for i in range(len(lineup_dict_home)):
        key_h = lineup_dict_home.player[i]['name']
        key_a = lineup_dict_away.player[i]['name']
        val_h = lineup_dict_home.jersey_number[i]
        val_a = lineup_dict_away.jersey_number[i]
        home_players[key_h] = str(val_h)
        away_players[key_a] = str(val_a)
        if lineup_dict_home.position[i]['id'] == 1:
            home_GK= key_h
        if lineup_dict_away.position[i]['id'] == 1:
            away_GK= key_a

    """ from the bank """
    for idx, row in subs.iterrows():
        if row['team']==team_home:
            home_players[row['substitution_replacement']] = 'subs'+str(len(home_players)-10)
        else:
            away_players[row['substitution_replacement']] = 'subs'+str(len(away_players)-10)

    return home_players, away_players, home_GK, away_GK


def get_tracking( pass_frame, att_team=True):
    """  """
    if att_team: 
        teammates= pass_frame[pass_frame.teammate]
    else:
        teammates= pass_frame[pass_frame.teammate == False]
    team_pos, team_x, team_y, team_gk = [], [], [], []
    for idx, pl in teammates.iterrows():
        # print(pl)
        if pl.keeper:
            team_gk.append( pl.location[0] )
            team_gk.append( pl.location[1] )
        else:
            team_x.append( pl.location[0] )
            team_y.append( pl.location[1] )
            team_pos.append( pl.location )
    
    return team_pos, team_x, team_y, team_gk


def get_inverse_tracking( pass_frame, att_team=True):
    """  """
    if att_team: 
        teammates= pass_frame[pass_frame.teammate]
    else:
        teammates= pass_frame[pass_frame.teammate == False]
    team_pos, team_x, team_y, team_gk = [], [], [], []
    for idx, pl in teammates.iterrows():
        # print(pl)
        if pl.keeper:
            team_gk.append( 120-pl.location[0] )
            team_gk.append( 80-pl.location[1] )
        else:
            team_x.append( 120-pl.location[0] )
            team_y.append( 80-pl.location[1] )
            team_pos.append( [120-pl.location[0], 80-pl.location[1]] )
    
    return team_pos, team_x, team_y, team_gk


def set_EPS_params( match_events, match_frames):
    """ """
    for idx, ev in match_events[(match_events.is_tracked) & (match_events.team == match_events.possession_team) &
                                ((match_events.type == 'Carry') | (match_events.type == 'Pass') |
                                 (match_events.type == 'Ball Receipt*') | (match_events.type == 'Shot') |
                                 (match_events.type == 'Dispossessed') | (match_events.type == 'Miscontrol') |
                                 (match_events.type == 'Ball Recovery') | (match_events.type == 'Foul Won') |
                                 (match_events.type == 'Interception') | (match_events.type == 'Dribble'))
                               ].iterrows():

        ev_frame = match_frames[match_frames.id == ev.id]
        #         opp_pos, opp_x, opp_y, opp_gk = get_tracking( ev_frame, False )
        if (ev.type == 'Foul Won' or ev.type == 'Dispossessed' or
                (ev.type == 'Dribble' and ev.dribble_outcome == 'Incomplete')):
            team_pos, team_x, team_y, team_gk = get_inverse_tracking(ev_frame, True)
            opp_pos, opp_x, opp_y, opp_gk = get_inverse_tracking(ev_frame, False)
        else:
            team_pos, team_x, team_y, team_gk = get_tracking(ev_frame, True)
            opp_pos, opp_x, opp_y, opp_gk = get_tracking(ev_frame, False)

        if len(opp_x) == 0:
            zone = 9 if opp_gk else 1
            match_events.loc[idx, 'origin_zone'] = zone
            continue  # It doesn't make sense to eval it tactically

        mean_posX = np.mean(opp_x)
        mean_posY = np.mean(opp_y)
        last_def_Xpos = np.max(opp_x)
        match_events.loc[idx, 'opp_block_height'] = mean_posX

        if mean_posX < 50:
            def_type = "High block"
        elif (mean_posX < 60) and (len(opp_x) > 7) and (last_def_Xpos < 70):
            def_type = "High block"
        elif (mean_posX > ppn_pitch.frontal_box_line_x) & (last_def_Xpos > 108):
            def_type = "Broken block"
        else:
            def_type = "Retrieved block"
        match_events.loc[idx, 'opp_def_type'] = def_type

        # print(ev.timestamp, ev.type, ev.player, mean_posX, def_type)

        if len(opp_x) > 2:  # We need 3 opponents minimum to set the convex hull
            hull = ConvexHull(opp_pos)
            match_events.loc[idx, 'origin_zone'] = ppn_pitch.get_player_zone( ev.location, hull, opp_pos, mean_posY,
                                                                              mean_posX, def_type, last_def_Xpos)
        else:
            if (mean_posX < 60) or (ev.location[0] < 60):
                match_events.loc[idx, 'origin_zone'] = 1
#                 print("Event con menos de 3 defensas: ", idx, " - Mean pos= ", mean_posX, ev.location[0])


def set_recovery_zones( match_events):
    """ set origin_zone (through following carry) for those recoveries that have not tracking """
    recov= match_events[ ((match_events.type == 'Duel') & (match_events.duel_outcome== 'Won')
                          | (match_events.type == 'Interception') & (match_events.interception_outcome== 'Won')
                         ) & (match_events.team == match_events.possession_team)]
    display( recov.origin_zone)
    for idx, ev in recov.iterrows():
        print( match_events['origin_zone'][idx], end="")
        match_events['origin_zone'][idx]= match_events[ (match_events.timestamp == ev.timestamp)
                                                            & (match_events.type == 'Carry')
                                                      ].origin_zone
        print( match_events['origin_zone'][idx])

def set_recovery_zones_2( match_events):
    """ set origin_zone (through following carry) for those recoveries that have not tracking """
    for idx, ev in match_events[ ((match_events.type == 'Duel') & (match_events.duel_outcome== 'Won')
                                  | (match_events.type == 'Interception') & (match_events.interception_outcome== 'Won')
                                 ) & (match_events.team == match_events.possession_team)
                               ].iterrows():
        match_events.loc[idx, 'origin_zone']= match_events[ (match_events.timestamp == ev.timestamp)
                                                            & (match_events.type == 'Carry')
                                                          ].iloc[0].origin_zone
        

def get_reception_id( related_ev, type_ev, match_events):
    """ """
    if isinstance(related_ev, (list, tuple, np.ndarray)):
        foul_id = None
        for ev_id in related_ev:
            ev_df = match_events[match_events.id == ev_id]
            if len(ev_df):
                unic_row = ev_df.iloc[0]
                if (type_ev == 'Pass') & (unic_row.type == 'Ball Receipt*'):
                    return ev_id
                elif (type_ev == 'Carry'):
                    if (not unic_row.is_tracked): continue
                    if (unic_row.type == 'Pass' or
                            unic_row.type == 'Shot' or
                            unic_row.type == 'Dribble' or
                            unic_row.type == 'Dispossessed' or
                            unic_row.type == 'Miscontrol'):
                        return ev_id
                    """ Due to a mistake in Stats Bomb in fouls with 'ley de la ventaja' 
                        we wait for next event related to the carry """
                    if unic_row.type == 'Foul Won':
                        # Got the reverse of the tracked frame on foul won events
                        foul_id = ev_id
        return foul_id


def get_num_players_tracked( ev_id, match_frames):
    """ Number of players tracked in the event """
    return len(match_frames[match_frames.id == ev_id])


def get_tracked_perc( match_events):
    """ Percentage of tracked events given by Stats Bomb """
    total_tracked= len( match_events[ ((match_events.type=='Pass') | (match_events.type=='Carry')) & match_events.is_tracked])
    total= len( match_events[ ((match_events.type=='Pass') | (match_events.type=='Carry'))] )
    tracked_perc= total_tracked * 100 / total
    return tracked_perc