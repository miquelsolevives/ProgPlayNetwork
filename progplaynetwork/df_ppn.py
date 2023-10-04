from progplaynetwork import statsbomb as ppn_sb
import math

""" INIT & COOKING NEW NEEDED ATRIBUTES """

def set_ppn_params_1( match_events, match_frames):
    """ """
    match_events['origin_zone']= 0
    match_events['dest_zone']= None
    match_events['opp_block_height']= 0
    match_events['opp_def_type']= None
    match_events['num_pl_tracked'] = match_events.apply( lambda row: ppn_sb.get_num_players_tracked( row.id, match_frames ), axis=1 )
    match_events['is_tracked'] = match_events.apply( lambda row: row.num_pl_tracked>0, axis=1 )

    match_events['related_reception_id']= match_events.apply( lambda row: ppn_sb.get_reception_id( row.related_events,
                                                                                                   row.type, match_events)
                                                              , axis=1 )
    match_events['orig_x'] = match_events.apply( lambda row: row.location[0]
                                                if ((row.type == 'Pass') | (row.type == 'Carry') | (row.type == 'Shot')
                                                    | (row.type == 'Dispossessed') | (row.type == 'Miscontrol')
                                                    | (row.type == 'Dribble') | (row.type == 'Foul Won'))
                                                else None, axis=1)
    match_events['orig_y'] = match_events.apply( lambda row: row.location[1]
                                                if ((row.type == 'Pass') | (row.type == 'Carry') | (row.type == 'Shot')
                                                    | (row.type == 'Dispossessed') | (row.type == 'Miscontrol')
                                                    | (row.type == 'Dribble') | (row.type == 'Foul Won'))
                                                else None, axis=1)

    match_events['dest_x'] = match_events.apply( lambda row: row.pass_end_location[0]
                                                 if row.type == 'Pass' else None, axis=1)
    match_events['dest_y'] = match_events.apply( lambda row: row.pass_end_location[1]
                                                 if row.type == 'Pass' else None, axis=1)
    match_events['dest_x'] = match_events.apply( lambda row: row.carry_end_location[0]
                                                 if row.type == 'Carry' else row.dest_x, axis=1)
    match_events['dest_y'] = match_events.apply( lambda row: row.carry_end_location[1]
                                                 if row.type == 'Carry' else row.dest_y, axis=1)

    match_events['height_prog'] = match_events.apply( lambda row: row.dest_x - row.orig_x
                                                      if (row.type == 'Pass') | (row.type == 'Carry') else None, axis=1)
    match_events['carry_length'] = match_events.apply( lambda row: math.dist( [row.orig_x, row.orig_y],
                                                                              [row.dest_x, row.dest_y] )
                                                       if row.type == 'Carry' else None, axis=1)
    
    
def get_receiver_zone( related_reception_id, match_events):
    """ """
    df_recep = match_events[match_events.id == related_reception_id]
    if len(df_recep):
        unic_row = df_recep.iloc[0]
        return unic_row.origin_zone


def get_receiver_block_height( related_reception_id, match_events):
    """ """
    df_recep = match_events[match_events.id == related_reception_id]
    if len(df_recep):
        unic_row = df_recep.iloc[0]
        return unic_row.opp_block_height


def is_block_rupture( opp_def_type, related_reception_id, match_events):
    """ """
    df_recep = match_events[match_events.id == related_reception_id]
    if len(df_recep):
        unic_row = df_recep.iloc[0]
        return True if opp_def_type == "Retrieved block" and unic_row.opp_def_type == "Broken block" else False


def is_progression_pass(orig_zone, dest_zone, height_prog,
                        ev_type, pass_length, carry_length):
    """ What should we paint? """

    if orig_zone == 1: return dest_zone > 1
    if (orig_zone == 2 or orig_zone == 3) and dest_zone == 6:
        if height_prog < -10: return False
        if height_prog > 5 or pass_length > 10 or carry_length > 10:
            return True
        else:
            return False
    if orig_zone == 2: return dest_zone > 6
    if orig_zone == 3: return dest_zone > 6
    if orig_zone == 6 and (dest_zone == 2 or dest_zone == 3):
        if height_prog < 5: return False
        if ev_type == 'Carry' and carry_length < 10:
            return False
        else:
            return True
    if orig_zone == 6 and dest_zone == 6:
        if height_prog > 7:
            return True
        else:
            return False
    if orig_zone == 6: return dest_zone > 6
    if orig_zone == 10:
        if dest_zone == 11 or dest_zone == 7 or dest_zone == 10:
            return height_prog > 5
        return dest_zone > 6 and dest_zone != 10
    if orig_zone == 7 or orig_zone == 11:
        if dest_zone == 10:
            length = carry_length if ev_type == 'Carry' else pass_length
            return (length + height_prog) / 2 > 7
        return dest_zone == 9 or dest_zone > 55
    if orig_zone == 77 or orig_zone == 111:
        return dest_zone == 99 or dest_zone == 9
    else:
        return False
    # if orig_zone==9: return False


def set_ppn_params_2( match_events, match_frames):
    """ """
    match_events['pass_recipient']= match_events.apply( lambda row: row.player
                                                       if (row.type=='Carry')
                                                       else row.pass_recipient, axis=1 )

    """ MERGING Passes with receptions to obtain destination zone! 
        The passes without receptions will have dest_zone=0 """

    match_events['dest_zone']= match_events.apply( lambda row: get_receiver_zone( row.related_reception_id, match_events)
                                                  if (((row.type=='Pass') | (row.type=='Carry')) & (row.is_tracked)
                                                      & (row.team==row.possession_team)) else None, axis=1 )
    match_events['dest_opp_block_height']= match_events.apply( lambda row: get_receiver_block_height( row.related_reception_id,
                                                                                                      match_events)
                                                  if (((row.type=='Pass') | (row.type=='Carry')) & (row.is_tracked)
                                                      & (row.team==row.possession_team)) else None, axis=1 )

    match_events['opp_block_height_prog'] = match_events.apply( lambda row: row.dest_opp_block_height - row.opp_block_height
                                                if (row.type == 'Pass') | (row.type == 'Carry') else None, axis=1)

    match_events['block_rupture_play']= match_events.apply( lambda row: is_block_rupture( row.opp_def_type,
                                                                                          row.related_reception_id,
                                                                                          match_events)
                                                  if (((row.type=='Pass') | (row.type=='Carry')) & (row.is_tracked)
                                                      & (row.team==row.possession_team)) else None, axis=1 )

    match_events['progression']= match_events.apply( lambda row: is_progression_pass( row.origin_zone, row.dest_zone,
                                                                                      row.height_prog, row.type,
                                                                                      row.pass_length, row.carry_length)
                                                    if (row.dest_zone>0 and row.pass_cross!=True)
                                                    else None, axis=1 )

def get_edge_events( match_events):
    """ Successful Full-Tracked plays without ABP against Medium/Low Block  """

    edge_events = match_events[(match_events.opp_def_type != 'High block') &
                               (match_events.dest_zone > 0) &  # Full-tracked (orig & dest)
                               (match_events.pass_outcome.isna()) &  # Successful
                               (match_events.pass_cross.isna()) &  # Not Cross
                               ((match_events.pass_type.isna()) |
                                (match_events.pass_type == 'Recovery') |
                                (match_events.pass_type == 'Interception'))  # Without ABP
                               ].copy()

    """ Treiem els carries dins de zona pq falseja el numero de intervencions """
    edge_events = edge_events[(edge_events.player != edge_events.pass_recipient)
                              | (edge_events.dest_zone != edge_events.origin_zone)]

    """ Aprofitem els carries dins d'una zona per millorar la ubicació del node """
    edge_events['x_avg'] = edge_events.apply(lambda row: (row.orig_x + row.dest_x) / 2
                                            if (row.pass_recipient == row.player and
                                                row.dest_zone == row.origin_zone)
                                            else row.dest_x, axis=1)
    edge_events['y_avg'] = edge_events.apply(lambda row: (row.orig_y + row.dest_y) / 2
                                            if (row.pass_recipient == row.player and
                                                row.dest_zone == row.origin_zone)
                                            else row.dest_y, axis=1)
    return edge_events


def get_pass_events( match_events):
    """ Subconjunto de edge events (sin conducciones) """
    passes = match_events[ (match_events.type=='Pass') &
                           (match_events.dest_zone>0) &            # Full-tracked (orig & dest)
                           (match_events.pass_outcome.isna()) &    # Successful
                           (match_events.pass_type.isna()) ]       # Without ABP
    return passes


def get_node_events( match_events):
    """ """
    node_events = match_events[ (  (match_events.origin_zone > 0) # Tracked
                                 & (match_events.opp_def_type != 'High block')
                                 & ((match_events.pass_type.isna()) |
                                    (match_events.pass_type=='Recovery') |
                                    (match_events.pass_type=='Interception') ) # Without ABP                             
                                 & ((match_events.type == 'Pass') |
                                    ((match_events.type == 'Carry') & (match_events.dest_zone > 0) 
                                      & (match_events.dest_zone != match_events.origin_zone)) |
                                    (match_events.type == 'Dispossessed') |
                                    (match_events.type == 'Miscontrol') |
                                    (match_events.type == 'Foul Won') |
                                    ((match_events.type == 'Shot') & (match_events.shot_type=='Open Play')) |
                                    ((match_events.type == 'Dribble') & (match_events.dribble_outcome=='Incomplete')))
                                )]
    return node_events


def get_losts( node_events):
    """ """
    losts= node_events[ (node_events.type=='Miscontrol') 
                       | (node_events.type=='Dispossessed') 
                       | (node_events.type=='Dribble') 
                       | ((node_events.type=='Pass') & (node_events.pass_cross.isna()) &
                          ((node_events.pass_outcome=='Out') |
                           (node_events.pass_outcome=='Incomplete') |
                           (node_events.pass_outcome=='Pass Offside')) )]
    return losts


def get_finalizations( node_events):
    """ """
    return node_events[ (node_events.type=='Shot') 
                      | (node_events.pass_cross==True)]


def get_recoveries( match_events):
    """ """
    return match_events[ (match_events.origin_zone > 0) # Tracked
                         & (match_events.opp_def_type != 'High block')
                         & (match_events.team == match_events.possession_team)
                         & ( ((match_events.type == 'Interception') & (match_events.interception_outcome== 'Won'))
                            | ((match_events.type == 'Duel') & (match_events.duel_outcome== 'Won'))
                            | (match_events.type == 'Ball Recovery') # After 'success in play'
                            | ((match_events.type == 'Pass') & (match_events.pass_outcome.isna()) &
                              ((match_events.pass_type == 'Recovery') | (match_events.pass_type == 'Interception')))
                           )
                        ]


def get_nodes( node_events):
    """ """
    nodes = node_events.groupby(['player', 'origin_zone', 'team', 'period']
                                ).agg({'player': ['count'], 'orig_x': ['mean'], 'orig_y': ['mean']})
    nodes.reset_index(inplace=True)
    nodes.columns = ['player', 'zone', 'team', 'period', 'pl_zone_sum', 'loc_avg_x', 'loc_avg_y']
    return nodes


def get_lost_nodes( losts):
    """ """
    lost_nodes = losts.groupby(['player', 'origin_zone', 'team', 'period']
                               ).agg({'team': ['count']})
    lost_nodes.reset_index(inplace=True)
    lost_nodes.columns = ['player', 'zone', 'team', 'period', 'losts']
    return lost_nodes


def get_recov_nodes( recov):
    """ """
    recov_nodes = recov.groupby(['player', 'origin_zone', 'team', 'period']
                                     ).agg({'team': ['count']})
    recov_nodes.reset_index(inplace=True)
    recov_nodes.columns = ['player', 'zone', 'team', 'period', 'recov']
    return recov_nodes


def get_final_nodes( finaliz):
    """ """
    final_nodes = finaliz.groupby(['player', 'origin_zone', 'team', 'period']
                                 ).agg({'period': ['count']})
    final_nodes.reset_index(inplace=True)
    final_nodes.columns = ['player', 'zone', 'team', 'period', 'endings']
    return final_nodes


def get_edges( edge_events, nodes):
    """ We get the edges from events grouping it by 4 campos.
        After it we need to get the ubication of origin and destination from 'nodes'
    """
    edges = edge_events.groupby(['player', 'origin_zone', 'pass_recipient', 'dest_zone',
                                 'progression', 'team', 'period']
                                ).agg({'player': ['count']})  # Es podria posar qualsevol columna a 'count'
    edges.columns = ['edge_amount']
    edges.reset_index(inplace=True)
    edges.rename(columns={'player': 'orig_player', 'pass_recipient': 'dest_player'}, inplace=True)

    """ Anem a buscar la posició de origen i destinacio de la aresta a nodes (zona-jugador) """
    edges = edges.merge( nodes[['player', 'zone', 'period', 'loc_avg_x', 'loc_avg_y', 'pl_zone_sum']],
                         how='left', left_on=['dest_player', 'dest_zone', 'period'],
                         right_on=['player', 'zone', 'period'])
    edges.drop(columns=['player', 'zone'], inplace=True)
    edges.rename(columns={'loc_avg_x': 'dest_loc_x', 'loc_avg_y': 'dest_loc_y',
                          'pl_zone_sum': 'dest_node_size'}, inplace=True)

    edges = edges.merge( nodes[['player', 'zone', 'period', 'loc_avg_x', 'loc_avg_y', 'pl_zone_sum']],
                         how='left', left_on=['orig_player', 'origin_zone', 'period'],
                         right_on=['player', 'zone', 'period'])
    edges.drop(columns=['player', 'zone'], inplace=True)
    edges.rename(columns={'loc_avg_x': 'orig_loc_x', 'loc_avg_y': 'orig_loc_y',
                          'pl_zone_sum': 'orig_node_size'}, inplace=True)
    edges['width'] = 0
    return edges


def get_crosses( match_events, nodes):
    """ Same than edges """

    passes= get_pass_events( match_events)
    cross_events = passes[passes.pass_cross == True]
    crosses = cross_events.groupby(['player', 'origin_zone', 'pass_recipient', 'dest_zone', 'period', 'team']
                                   ).agg({'player': ['count']})
    crosses.columns = ['cross_amount']
    crosses.reset_index(inplace=True)
    crosses.rename(columns={'player': 'orig_player', 'pass_recipient': 'dest_player'}, inplace=True)

    crosses = crosses.merge( nodes[['player', 'zone', 'period', 'loc_avg_x', 'loc_avg_y']],
                             how='left', left_on=['dest_player', 'dest_zone', 'period'],
                             right_on=['player', 'zone', 'period'])
    crosses.drop(columns=['player', 'zone'], inplace=True)
    crosses.rename(columns={'loc_avg_x': 'dest_loc_x', 'loc_avg_y': 'dest_loc_y'}, inplace=True)

    crosses = crosses.merge( nodes[['player', 'zone', 'period', 'loc_avg_x', 'loc_avg_y']],
                             how='left', left_on=['orig_player', 'origin_zone', 'period'],
                             right_on=['player', 'zone', 'period'])
    crosses.drop(columns=['player', 'zone'], inplace=True)
    crosses.rename(columns={'loc_avg_x': 'orig_loc_x', 'loc_avg_y': 'orig_loc_y'}, inplace=True)
    return crosses