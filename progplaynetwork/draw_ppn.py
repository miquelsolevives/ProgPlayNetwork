from . import df_ppn
from . import pitch
from progplaynetwork import pitch as ppn_pitch

def make_ppn( match_events, team_home, team_away, home_GK, away_GK):
    """ CONSTRUCCIO DE LA PASSING NETWORK """
    edge_events= df_ppn.get_edge_events( match_events)
    passes= df_ppn.get_pass_events( match_events)
    node_events= df_ppn.get_node_events( match_events)
    
    losts= df_ppn.get_losts( node_events)
    finals= df_ppn.get_finalizations( node_events)
    recovs= df_ppn.get_recoveries( match_events)
    
    nodes= df_ppn.get_nodes( node_events)
    lost_nodes= df_ppn.get_lost_nodes( losts)
    final_nodes= df_ppn.get_final_nodes( finals)
    recov_nodes= df_ppn.get_recov_nodes( recovs)

    home_mean = edge_events[ edge_events.team == team_home].groupby('team')['opp_block_height'].mean()
    away_mean = edge_events[ edge_events.team == team_away].groupby('team')['opp_block_height'].mean()
    pitch.zone_normalizing( team_home, 1, nodes, home_GK, home_mean)
    pitch.zone_normalizing( team_away, 1, nodes, away_GK, away_mean)
    pitch.zone_normalizing( team_home, 2, nodes, home_GK, home_mean)
    pitch.zone_normalizing( team_away, 2, nodes, away_GK, away_mean)

    edges= get_edges( edge_events, nodes)
    crosses= get_crosses( match_events, nodes)
    
def get_nodes_from_edges( edges):
    """ """
    """ Agafo els nodes de les arestes finals per després filtrar els q hem de pintar """
    orig_nodes = edges.groupby(['team', 'period', 'orig_player', 'origin_zone',
                                'orig_loc_x', 'orig_loc_y', 'orig_node_size']
                               ).agg({'edge_amount': ['sum']})
    orig_nodes.columns = ['edge_amount_sum']
    orig_nodes.reset_index( inplace=True)
    orig_nodes.rename( columns={'orig_player': 'player', 'origin_zone': 'zone',
                                'edge_amount_sum': 'progs'}, inplace=True)

    dest_nodes = edges.groupby(['team', 'period', 'dest_player', 'dest_zone',
                                'dest_loc_x', 'dest_loc_y', 'dest_node_size']
                               ).agg({'edge_amount': ['sum']})
    dest_nodes.columns = ['edge_amount_sum']
    dest_nodes.reset_index( inplace=True)
    dest_nodes.rename( columns={'dest_player': 'player', 'dest_zone': 'zone',
                                'edge_amount_sum': 'prog_receptions'}, inplace=True)

    return orig_nodes, dest_nodes

def get_cross_nodes( crosses):
    """ """
    orig_cross_nodes= crosses.groupby( ['team', 'period', 'orig_player', 'origin_zone', 'orig_loc_x', 'orig_loc_y']
                                       ).agg( {'cross_amount':['sum']} )
    orig_cross_nodes.columns= ['cross_amount_sum']
    orig_cross_nodes.reset_index(inplace=True)
    orig_cross_nodes.rename( columns= {'orig_player':'player', 'origin_zone':'zone'}, inplace=True)

    dest_cross_nodes= crosses.groupby( ['team', 'period', 'dest_player', 'dest_zone', 'dest_loc_x', 'dest_loc_y']
                                       ).agg( {'cross_amount':['sum']} )
    dest_cross_nodes.columns= ['cross_amount_sum']
    dest_cross_nodes.reset_index(inplace=True)
    dest_cross_nodes.rename( columns= {'dest_player':'player', 'dest_zone':'zone'}, inplace=True)

    return orig_cross_nodes, dest_cross_nodes


def draw_prog_play_network_2( team, period, ax, player):
    """ """
    
    """ filtering Team & Period Nodes """
    filtered_nodes= nodes[ (nodes.team==team) & (nodes.period==period) ].copy()
    filt_fin_nodes= vis_finaliz[ (vis_finaliz.team==team) & (vis_finaliz.period==period) ].copy()
    filt_lost_nodes= lost_nodes[ (lost_nodes.team==team) & (lost_nodes.period==period) ].copy()
    
    dest_nodes = dest_prog_nodes[ (dest_prog_nodes.team == team) & (dest_prog_nodes.period == period) ].copy()
    orig_nodes = orig_prog_nodes[ (orig_prog_nodes.team == team) & (orig_prog_nodes.period == period) ].copy()
    cross_recep_nodes = dest_cross_nodes[ (dest_cross_nodes.team == team) 
                                         & (dest_cross_nodes.period == period) ].copy()
    cross_orig_nodes = orig_cross_nodes[ (orig_cross_nodes.team == team) 
                                         & (orig_cross_nodes.period == period) ].copy()
  
    filtered_nodes.set_index( ['player', 'zone', 'period', 'team'], inplace=True)
    filt_lost_nodes.set_index( ['player', 'zone', 'period', 'team'], inplace=True)
    filt_fin_nodes.set_index( ['player', 'zone', 'period', 'team'], inplace=True)
    orig_nodes.set_index( ['player', 'zone', 'period', 'team'], inplace=True)
    dest_nodes.set_index( ['player', 'zone', 'period', 'team'], inplace=True)
    cross_recep_nodes.set_index( ['player', 'zone', 'period', 'team'], inplace=True)
    cross_orig_nodes.set_index( ['player', 'zone', 'period', 'team'], inplace=True)


#     display( filtered_nodes.head(1), 'filtered_nodes ^')
#     display( orig_nodes.head(1), 'orig_nodes ^')
#     display( dest_nodes.head(1), 'dest_nodes ^')
#     display( filt_fin_nodes.head(1), 'filt_fin_nodes ^', 'length:', len(filt_fin_nodes))
#     display( filt_lost_nodes.head(1), 'filt_lost_nodes ^', 'length:', len(filt_lost_nodes))

    """ Getting the nodes to paint from Prog Edges + Finalizations """
    # [[]] --> We don't need the columns, just the rows (index columns)
    drawn_nodes = dest_nodes[[]].merge( orig_nodes[[]], how='outer', 
                                        left_index=True, right_index=True)
                                        # Old way: on=['player', 'zone', 'team', 'period']
#     display( drawn_nodes.head(), 'drawn_nodes ^', 'length:', len(drawn_nodes))

    if VIS=='GLOBAL':
        drawn_nodes= filt_fin_nodes[[]].merge( drawn_nodes, how='outer', left_index=True, right_index=True)
        drawn_nodes= filtered_nodes[ filtered_nodes.pl_zone_sum > 4 
                                   ][[]].merge( drawn_nodes, how='outer', left_index=True, right_index=True)
    elif VIS=='BUILDUP':
        drawn_nodes= filtered_nodes[ (filtered_nodes.pl_zone_sum > 5)
                                   ][[]].merge( drawn_nodes, how='outer', left_index=True, right_index=True)
            
#     display( drawn_nodes.head(1), 'drawn_nodes after merge final nodes: ^', 'length:', len(drawn_nodes))
    drawn_nodes= cross_recep_nodes[['cross_amount_sum']].merge( drawn_nodes, how='outer', left_index=True, right_index=True )
    drawn_nodes.cross_amount_sum.fillna(0, inplace=True)
#     display( drawn_nodes.head(1), 'drawn_nodes after merge cross nodes: ^', 'length:', len(drawn_nodes))
    drawn_nodes= cross_orig_nodes[[]].merge( drawn_nodes, how='outer', left_index=True, right_index=True )

#     display( drawn_nodes.head(1), 'drawn_nodes after add big nodes without edges: ^', 'length:', len(drawn_nodes))
#     if VIS=='PLAYER':
#         if len(cross_orig_nodes) > 0:
#             drawn_nodes= cross_orig_nodes.merge( drawn_nodes, how='outer', 
#                                                  left_index=True, right_index=True )

    """ Getting the info to paint """
    drawn_nodes= filtered_nodes.merge( drawn_nodes, how='inner',
                                       left_index=True, right_index=True )
#     display( drawn_nodes.head(1), 'drawn_nodes after Filtered ^', 'length:', len(drawn_nodes))
#     if VIS=='BUILDUP':
    if VIS != 'GLOBAL':
        drawn_nodes= dest_nodes[['prog_receptions']].merge( drawn_nodes, how='right', left_index=True, right_index=True)
        drawn_nodes.prog_receptions.fillna(0, inplace=True)
    if VIS == 'PLAYER':
        drawn_nodes= orig_nodes[['progs']].merge( drawn_nodes, how='right', left_index=True, right_index=True)
        drawn_nodes.progs.fillna(0, inplace=True)
    
    node_losts= filt_lost_nodes.merge( drawn_nodes, how='inner', left_index=True, right_index=True)
    """ S'ha de fer de drawn enlloc de filtered pq no volem nodes només amb pèrdues """
#     display( node_losts.head(1), 'node_losts after merge drawn_nodes ^', 'length:', len(node_losts))
    
    node_progs= orig_nodes[['progs']].merge( filtered_nodes, how='inner', left_index=True, right_index=True)
#     display( node_progs.head(1), 'node_progs after merge filtered_nodes ^', 'length:', len(node_progs))
    
    if VIS=='GLOBAL':
        node_final= filt_fin_nodes.merge( filtered_nodes, how='left', left_index=True, right_index=True)
#         display( node_final.head(1), 'node_final after merge filtered_nodes ^', 'length:', len(node_final))
    else:
        node_final= filt_fin_nodes.merge( drawn_nodes, how='right', left_index=True, right_index=True)
#         display( node_final.head(1), 'node_final after merge drawn_nodes ^', 'length:', len(node_final))

    """ Merges to get the info of inferior node slice """
    node_progs= node_progs.merge( node_final[['endings']],
                                  how='left', left_index=True, right_index=True)
    node_progs['final_progs']= node_progs[ ['progs', 'endings']].sum(axis=1)

    node_losts= node_losts.merge( node_progs[['final_progs']],
                                  how='left', left_index=True, right_index=True)
    node_losts['final_losts']= node_losts[ ['losts', 'final_progs']].sum(axis=1)
        
    drawn_nodes.reset_index( inplace=True)
    node_losts.reset_index( inplace=True)
    node_progs.reset_index( inplace=True)
    node_final.reset_index( inplace=True)
        
    """ Node size definition """
    if VIS=='PLAYER':
        drawn_nodes['pl_zone_sum'] = drawn_nodes.apply( lambda row: row.pl_zone_sum 
                                                        if row.player == player 
                                                        else row.prog_receptions + row.progs, axis=1)
        node_losts['node_size'] = node_losts.apply( lambda row: NODE_SIZE * (row.final_losts**1.7) + MIN_NODE_SIZE
                                                    if (row.player == player) else 0, axis=1)
        node_progs['node_size'] = node_progs.apply( lambda row: NODE_SIZE * (row.final_progs**1.7) + MIN_NODE_SIZE
                                                    if (row.player == player) else 0, axis=1)
        node_final['node_size'] = node_final.apply( lambda row: NODE_SIZE * (row.endings**1.7) + MIN_NODE_SIZE
                                                    if (row.player == player) else 0, axis=1)
    elif VIS=='BUILDUP':
        drawn_nodes['pl_zone_sum'] = drawn_nodes.apply( lambda row: row.pl_zone_sum 
                                                        if row.zone == 1
                                                        else row.prog_receptions + row.cross_amount_sum, axis=1 )
        node_losts['node_size'] = node_losts.apply( lambda row: NODE_SIZE * (row.final_losts**1.7) + MIN_NODE_SIZE
                                                    if (row.zone == 1) else 0, axis=1)
        node_progs['node_size'] = node_progs.apply( lambda row: NODE_SIZE * (row.final_progs**1.7) + MIN_NODE_SIZE
                                                    if (row.zone == 1) else 0, axis=1)
        node_final['node_size'] = node_final.apply( lambda row: NODE_SIZE * (row.endings**1.7) + MIN_NODE_SIZE
                                                    if (row.zone == 1) else 0, axis=1)
    else: 
        node_losts['node_size'] = NODE_SIZE * (node_losts.final_losts**1.7) + MIN_NODE_SIZE
        node_progs['node_size'] = NODE_SIZE * (node_progs.final_progs**1.7) + MIN_NODE_SIZE
        node_final['node_size'] = NODE_SIZE * (node_final.endings**1.7) + MIN_NODE_SIZE
        
    drawn_nodes['node_size'] = NODE_SIZE * (drawn_nodes.pl_zone_sum**1.7) + MIN_NODE_SIZE
#     display( drawn_nodes, 'final drawn_nodes', 'length:', len(drawn_nodes))
        
#     display( node_losts.head(1), 'node_losts ^')
#     display( node_progs.head(1), 'node_progs ^')
#     display( node_final.head(1), 'node_final ^')
    
#     team_dest_prog_nodes['node_size'] = NODE_SIZE * (team_dest_prog_nodes.edge_amount_sum**1.7) + MIN_NODE_SIZE
#     display(losts.head(1))
#     display('node_progs', node_progs.head(3))
    
    pitch.scatter( drawn_nodes.loc_avg_x, drawn_nodes.loc_avg_y,
                  s= drawn_nodes['node_size'], color= 'white', edgecolors= 'black',
                  linewidth= 1, alpha= .4, ax= ax, zorder= 1)  

    pitch.scatter( node_losts.loc_avg_x, node_losts.loc_avg_y,
                  s= node_losts['node_size'], color= 'grey',
                  linewidth= 0, alpha= 0.8, ax= ax, zorder= 1)  
    
    pitch.scatter( node_progs.loc_avg_x, node_progs.loc_avg_y,
                   s= node_progs['node_size'], color= 'red', 
                   linewidth= 0, alpha= 0.8, ax= ax, zorder= 3)

#     if VIS=='GLOBAL':
    pitch.scatter( node_final.loc_avg_x, node_final.loc_avg_y,
                  s= node_final['node_size'], color= 'violet',
                  linewidth= 0, alpha= 1, ax= ax, zorder= 4)   
    
#     pitch.scatter( team_dest_prog_nodes.dest_loc_x, 
#                  team_dest_prog_nodes.dest_loc_y,
#                  s= team_dest_prog_nodes['node_size'],
#                  color= 'orange', edgecolors= 'black', 
#                  linewidth= 0, alpha= 0.8, ax= ax, zorder = 3)
    
    
    """ PAINT EDGES """
    
    """ Edge width definition """
#     prog_edges.loc[ (prog_edges.team==team) & (prog_edges.period==period), 
#                    'width'] = LINE_WIDTH * (prog_edges.edge_amount / REFERENCE_PASSES_AMOUNT) 
    filtered_edges= prog_edges[ (prog_edges.team == team) & (prog_edges.period == period) 
                               & (prog_edges.edge_amount >= MIN_CONNEX_PASSES) ].copy()
    filtered_edges['width']= LINE_WIDTH * (filtered_edges.edge_amount / REFERENCE_PASSES_AMOUNT) 

#     if VIS=='GLOBAL':
    filt_crosses= vis_crosses[ (vis_crosses.team == team) & (vis_crosses.period == period)
                         & (vis_crosses.cross_amount >= MIN_CONNEX_PASSES)].copy()
    filt_crosses['width']= LINE_WIDTH * (filt_crosses.cross_amount / REFERENCE_PASSES_AMOUNT)
#     display( filt_crosses)
    paint_crosses( filt_crosses.orig_loc_x, filt_crosses.orig_loc_y, 
                   filt_crosses.dest_loc_x, filt_crosses.dest_loc_y, 
                   filt_crosses.width, ax, zorder= 3, color= 'violet')
        
    """ Agafem el tamany dels nodes de progressió """
    filtered_edges= filtered_edges.merge( node_progs[['player', 'zone', 'period', 'node_size']], 
                                          how= 'left', suffixes=('', '_progs'),
                                          left_on= ['orig_player', 'origin_zone', 'period'], 
                                          right_on= ['player', 'zone', 'period'])
    filtered_edges= filtered_edges.rename( columns= {'node_size':'orig_prog_node_size'})
    
    filtered_edges= filtered_edges.merge( node_progs[['player', 'zone', 'period', 'node_size']], 
                                          how= 'left', suffixes=('', '_progs2'),
                                          left_on= ['dest_player', 'dest_zone', 'period'], 
                                          right_on= ['player', 'zone', 'period'])
    filtered_edges= filtered_edges.rename( columns= {'node_size':'dest_prog_node_size'})
    
    filtered_edges= filtered_edges.merge( node_final[['player', 'zone', 'period', 'node_size']], 
                                          how= 'left', suffixes=('', '_final'),
                                          left_on= ['dest_player', 'dest_zone', 'period'], 
                                          right_on= ['player', 'zone', 'period'])
    
    filtered_edges['node_size']= filtered_edges.apply( lambda row: MIN_NODE_SIZE + NODE_SIZE
                                                           if np.isnan(row.node_size)
                                                           else row.node_size, axis=1)

    filtered_edges['dest_prog_node_size']= filtered_edges.apply( lambda row: row.node_size
                                                           if np.isnan(row.dest_prog_node_size)
                                                           else row.dest_prog_node_size, axis=1)

#     display( filtered_edges, 'filtered_edges ^')
    
    biedges= filtered_edges.merge( filtered_edges[['orig_player', 'origin_zone', 'dest_player', 'dest_zone']],
                                  how= 'inner', suffixes=('', '_bis'),
                                  left_on= ['orig_player', 'origin_zone', 'dest_player', 'dest_zone'], 
                                  right_on= ['dest_player', 'dest_zone', 'orig_player', 'origin_zone'])
    
    carry_biedges= biedges[ biedges.dest_player == biedges.orig_player ]
    pass_biedges= biedges[ biedges.dest_player != biedges.orig_player ]
    
    paint_edge_arrows( pass_biedges.orig_loc_x, pass_biedges.orig_loc_y,
                       pass_biedges.dest_loc_x, pass_biedges.dest_loc_y, 
                       pass_biedges.dest_prog_node_size, pass_biedges.orig_prog_node_size,
                       pass_biedges.width, bidir= True, ax= ax, color= 'white', zorder= 2, alpha= .8 )
    paint_edge_arrows( carry_biedges.orig_loc_x, carry_biedges.orig_loc_y,
                       carry_biedges.dest_loc_x, carry_biedges.dest_loc_y,
                       carry_biedges.dest_prog_node_size, carry_biedges.orig_prog_node_size,
                       carry_biedges.width, bidir= True, ax= ax, color= 'deepskyblue', zorder= 2, alpha= 1 )

    uniedges= filtered_edges.merge( biedges[['orig_player', 'origin_zone', 'dest_player', 'dest_zone']],
                                   how= 'left', indicator= True, suffixes= ('', '_bis'),
                                   on= ['orig_player', 'origin_zone', 'dest_player', 'dest_zone'] )
    uniedges= uniedges[ uniedges._merge=='left_only']
#     display( 'Uniedges from biedges left-only merge', uniedges['width'].head(9))
    
    carry_uniedges= uniedges[ uniedges.dest_player == uniedges.orig_player ]
    pass_uniedges= uniedges[ uniedges.dest_player != uniedges.orig_player ]
    
    if VIS == 'PLAYER':
        prog_uniedges= pass_uniedges[ pass_uniedges.orig_player == player]
        pass_uniedges= pass_uniedges[ pass_uniedges.dest_player == player]
        
        paint_edge_arrows( prog_uniedges.orig_loc_x, prog_uniedges.orig_loc_y,
                           prog_uniedges.dest_loc_x, prog_uniedges.dest_loc_y,
                           prog_uniedges.dest_prog_node_size, prog_uniedges.orig_prog_node_size,
                           prog_uniedges.width, bidir= False, ax= ax, color= 'yellow', zorder= 2, alpha= .55 )
    
    paint_edge_arrows( pass_uniedges.orig_loc_x, pass_uniedges.orig_loc_y,
                       pass_uniedges.dest_loc_x, pass_uniedges.dest_loc_y,
                       pass_uniedges.dest_prog_node_size, pass_uniedges.orig_prog_node_size,
                       pass_uniedges.width, bidir= False, ax= ax, color= 'white', zorder= 2, alpha= .55 )
    paint_edge_arrows( carry_uniedges.orig_loc_x, carry_uniedges.orig_loc_y,
                       carry_uniedges.dest_loc_x, carry_uniedges.dest_loc_y,
                       carry_uniedges.dest_prog_node_size, carry_uniedges.orig_prog_node_size,
                       carry_uniedges.width, bidir= False, ax= ax, color= 'deepskyblue', zorder= 2, alpha= .7 )
    
#     pitch.lines( pass_uniedges.orig_loc_x, pass_uniedges.orig_loc_y, 
#                  pass_uniedges.dest_loc_x, pass_uniedges.dest_loc_y, 
#                  lw= pass_uniedges.width, color= 'white', zorder= 1, alpha= 0.8, ax= ax)
#     pitch.lines( carry_uniedges.orig_loc_x, carry_uniedges.orig_loc_y, 
#                  carry_uniedges.dest_loc_x, carry_uniedges.dest_loc_y, 
#                  lw= carry_uniedges.width, color= 'deepskyblue', zorder= 1, alpha= 0.8, ax= ax)
#     arrows = pitch.lines( filt_crosses.orig_loc_x, filt_crosses.orig_loc_y, 
#                           filt_crosses.dest_loc_x, filt_crosses.dest_loc_y, 
#                           lw= filt_crosses.width, color= 'violet', zorder= 3, alpha= 0.8, ax= ax)    
    
    """ Vis names """
    for index, row in drawn_nodes.iterrows():
        zone= int(row.zone)
        name_color= 'black' if VIS=='PLAYER' and row.player == player else 'white'
        name= getNick( row.player, team)
#         if zone>55 or zone==9 or zone==10: name= str(zone)+'_'+name
        ha= 'center'
        if zone==1: loc= (row.loc_avg_x-2, row.loc_avg_y)
        elif [2,7,77].count(zone): 
            loc= (row.loc_avg_x, row.loc_avg_y+1)
            ha= 'left'
        elif [3,11,111].count(zone): 
            loc= (row.loc_avg_x, row.loc_avg_y-1)
            ha= 'right'
        elif [6,9,99,10].count(zone): loc= (row.loc_avg_x+1.5, row.loc_avg_y)
#         elif zone==6: loc= (row.loc_avg_x+1, row.loc_avg_y)
        pitch.annotate( name, xy= loc, color= name_color, va='center',
                        ha=ha, size=9, ax=ax, zorder=7, alpha=1)

    """ Header """
    half= '1st Half' if period==1 else '2nd Half'
    home_score= len( match_events[ (match_events.shot_outcome=='Goal') 
                                  & (match_events.team==team_home) 
                                  & (match_events.period==period) ] )
    away_score= len( match_events[ (match_events.shot_outcome=='Goal') 
                                  & (match_events.team==team_away) 
                                  & (match_events.period==period) ] )
    ax.text(0, 122, half, ha='left', weight='bold',
                         color= light_white, fontsize=12)
    
    name_height= 121 if VIS!='GLOBAL' else 122
    ax.text(40, name_height, TEAM.upper(), ha='center', weight='bold',
                         color= light_white, fontsize=12)
    ax.text(80, 123, 'period score:', ha='right', weight='bold',
                         color= light_white, fontsize=10)    
    ax.text(80, 121, team_home[0:3].upper()+' '+str(home_score)+'-'
            +str(away_score)+' '+team_away[0:3].upper(), 
            ha='right', weight='bold', color= light_white, fontsize=10)    
    
    
    """ Lateral tips """
    line_props= {'linewidth': 1, 'color': 'red', 'zorder':4}
    commentline1 = Line2D( [80.5, 88], [BROKEN_HEIGHT, BROKEN_HEIGHT], linestyle='--', **line_props)
    commentline2 = Line2D( [80.5, 88], [TOP_TEN_HEIGHT, TOP_TEN_HEIGHT], linestyle='--', **line_props)
    ax.add_artist(commentline1)
    ax.text( 83.5, BROKEN_HEIGHT+2, 'Broken', color= 'red', ha='left', fontsize=9)
    ax.text( 83.5, BROKEN_HEIGHT+0.5, 'block', color= 'red', ha='left', fontsize=9)
    ax.add_artist(commentline2)
    ax.text( 83.5, TOP_TEN_HEIGHT+1.5, 'Last', color= 'red', ha='left', fontsize=9)
    ax.text( 83.5, TOP_TEN_HEIGHT, 'def.', color= 'red', ha='left', fontsize=9)
    ax.text( 83.5, TOP_TEN_HEIGHT-1.5, 'line', color= 'red', ha='left', fontsize=9)
    
    
    """ Tactics """
    if period==1:
        """ Starting LineUp """
        form, lineup= get_match_lineup( TEAM, lineups)
        players= list(lineup.keys())
        pl_pos= 0
        pl_nick= getNick( players[pl_pos], team)

        ax.text( 83.5, EPS_TOP_HEIGHT, 'Formation:', color= 'black', ha='left', fontsize=9, weight='bold')
        ax.text( 83.5, EPS_TOP_HEIGHT-5, 'Starting lineup:', color= 'black', ha='left', fontsize=9, weight='bold')
        line= EPS_TOP_HEIGHT-7
        ax.text( 83.5, line, pl_nick, color= 'black', ha='left', fontsize=9)
        formation= '1'
        for ch in str(form):
            formation += '-'+ch
            line -= 1
            for i in range(int(ch)):
                pl_pos +=1
                pl_nick= getNick( players[pl_pos], team)
                line -= 1.5
                ax.text( 83.5, line, pl_nick, 
                        color= 'black', ha='left', fontsize=9)

        ax.text( 83.5, EPS_TOP_HEIGHT-2, formation, color= 'black', ha='left', fontsize=9)


def draw_prog_play_network_3(team, period, ax, player, node_type='full'):
    """ """

    """ filtering Team & Period Nodes """
    filtered_nodes = nodes[(nodes.team == team) & (nodes.period == period)].copy()
    filt_fin_nodes = vis_finaliz[(vis_finaliz.team == team) & (vis_finaliz.period == period)].copy()
    filt_lost_nodes = lost_nodes[(lost_nodes.team == team) & (lost_nodes.period == period)].copy()
    filt_recov_nodes = recov_nodes[(recov_nodes.team == team) & (recov_nodes.period == period)].copy()

    dest_nodes = dest_prog_nodes[(dest_prog_nodes.team == team) & (dest_prog_nodes.period == period)].copy()
    orig_nodes = orig_prog_nodes[(orig_prog_nodes.team == team) & (orig_prog_nodes.period == period)].copy()
    cross_recep_nodes = dest_cross_nodes[(dest_cross_nodes.team == team)
                                         & (dest_cross_nodes.period == period)].copy()
    cross_orig_nodes = orig_cross_nodes[(orig_cross_nodes.team == team)
                                        & (orig_cross_nodes.period == period)].copy()

    filtered_nodes.set_index(['player', 'zone', 'period', 'team'], inplace=True)
    filt_lost_nodes.set_index(['player', 'zone', 'period', 'team'], inplace=True)
    filt_fin_nodes.set_index(['player', 'zone', 'period', 'team'], inplace=True)
    filt_recov_nodes.set_index(['player', 'zone', 'period', 'team'], inplace=True)
    orig_nodes.set_index(['player', 'zone', 'period', 'team'], inplace=True)
    dest_nodes.set_index(['player', 'zone', 'period', 'team'], inplace=True)
    cross_recep_nodes.set_index(['player', 'zone', 'period', 'team'], inplace=True)
    cross_orig_nodes.set_index(['player', 'zone', 'period', 'team'], inplace=True)

    #     display( filtered_nodes.head(1), 'filtered_nodes ^')
    #     display( orig_nodes.head(1), 'orig_nodes ^')
    #     display( dest_nodes.head(1), 'dest_nodes ^')
    #     display( filt_fin_nodes.head(1), 'filt_fin_nodes ^', 'length:', len(filt_fin_nodes))
    #     display( filt_lost_nodes.head(1), 'filt_lost_nodes ^', 'length:', len(filt_lost_nodes))

    """ Getting the nodes to paint from Prog Edges + Finalizations """
    # [[]] --> We don't need the columns, just the rows (index columns)
    drawn_nodes = dest_nodes[[]].merge(orig_nodes[[]], how='outer',
                                       left_index=True, right_index=True)
    # Old way: on=['player', 'zone', 'team', 'period']
    #     display( drawn_nodes.head(), 'drawn_nodes ^', 'length:', len(drawn_nodes))

    if VIS == 'GLOBAL':
        drawn_nodes = filt_fin_nodes[[]].merge(drawn_nodes, how='outer', left_index=True, right_index=True)
        drawn_nodes = filtered_nodes[filtered_nodes.pl_zone_sum > 4
                                     ][[]].merge(drawn_nodes, how='outer', left_index=True, right_index=True)
    elif VIS == 'BUILDUP':
        drawn_nodes = filtered_nodes[(filtered_nodes.pl_zone_sum > 5)
        ][[]].merge(drawn_nodes, how='outer', left_index=True, right_index=True)

    #     display( drawn_nodes.head(1), 'drawn_nodes after merge final nodes: ^', 'length:', len(drawn_nodes))
    drawn_nodes = cross_recep_nodes[['cross_amount_sum']].merge(drawn_nodes, how='outer', left_index=True,
                                                                right_index=True)
    drawn_nodes.cross_amount_sum.fillna(0, inplace=True)
    #     display( drawn_nodes.head(1), 'drawn_nodes after merge cross nodes: ^', 'length:', len(drawn_nodes))
    drawn_nodes = cross_orig_nodes[[]].merge(drawn_nodes, how='outer', left_index=True, right_index=True)

    #     display( drawn_nodes.head(1), 'drawn_nodes after add big nodes without edges: ^', 'length:', len(drawn_nodes))
    #     if VIS=='PLAYER':
    #         if len(cross_orig_nodes) > 0:
    #             drawn_nodes= cross_orig_nodes.merge( drawn_nodes, how='outer', 
    #                                                  left_index=True, right_index=True )

    """ Getting the info to paint """
    drawn_nodes = filtered_nodes.merge(drawn_nodes, how='inner',
                                       left_index=True, right_index=True)
    #     display( drawn_nodes.head(1), 'drawn_nodes after Filtered ^', 'length:', len(drawn_nodes))
    #     if VIS=='BUILDUP':
    if VIS != 'GLOBAL':
        drawn_nodes = dest_nodes[['prog_receptions']].merge(drawn_nodes, how='right', left_index=True, right_index=True)
        drawn_nodes.prog_receptions.fillna(0, inplace=True)
    if VIS == 'PLAYER':
        drawn_nodes = orig_nodes[['progs']].merge(drawn_nodes, how='right', left_index=True, right_index=True)
        drawn_nodes.progs.fillna(0, inplace=True)

    node_losts = filt_lost_nodes.merge(drawn_nodes, how='inner', left_index=True, right_index=True)
    node_recov = filt_recov_nodes.merge(drawn_nodes, how='inner', left_index=True, right_index=True)
    """ S'ha de fer de drawn enlloc de filtered pq no volem nodes només amb pèrdues """
    #     display( node_losts.head(1), 'node_losts after merge drawn_nodes ^', 'length:', len(node_losts))

    node_progs = orig_nodes[['progs']].merge(filtered_nodes, how='inner', left_index=True, right_index=True)
    #     display( node_progs.head(1), 'node_progs after merge filtered_nodes ^', 'length:', len(node_progs))
    node_recep = dest_nodes[['prog_receptions']].merge(filtered_nodes, how='inner', left_index=True, right_index=True)

    if VIS == 'GLOBAL':
        node_final = filt_fin_nodes.merge(filtered_nodes, how='left', left_index=True, right_index=True)
    #         display( node_final.head(1), 'node_final after merge filtered_nodes ^', 'length:', len(node_final))
    else:
        node_final = filt_fin_nodes.merge(drawn_nodes, how='right', left_index=True, right_index=True)
    #         display( node_final.head(1), 'node_final after merge drawn_nodes ^', 'length:', len(node_final))

    """ Merges to get the info of inferior node slice """
    node_progs = node_progs.merge(node_final[['endings']],
                                  how='left', left_index=True, right_index=True)
    node_progs['final_progs'] = node_progs[['progs', 'endings']].sum(axis=1)

    node_losts = node_losts.merge(node_progs[['final_progs']],
                                  how='left', left_index=True, right_index=True)
    node_losts['final_losts'] = node_losts[['losts', 'final_progs']].sum(axis=1)

    node_recov = node_recov.merge(node_recep[['prog_receptions']],
                                  how='left', left_index=True, right_index=True)
    node_recov['final_recov'] = node_recov[['recov', 'prog_receptions']].sum(axis=1)

    drawn_nodes.reset_index(inplace=True)
    node_losts.reset_index(inplace=True)
    node_progs.reset_index(inplace=True)
    node_final.reset_index(inplace=True)
    node_recep.reset_index(inplace=True)
    node_recov.reset_index(inplace=True)

    """ Node size definition """
    if VIS == 'PLAYER':
        drawn_nodes['pl_zone_sum'] = drawn_nodes.apply(lambda row: row.pl_zone_sum
        if row.player == player
        else row.prog_receptions + row.progs, axis=1)
        node_losts['node_size'] = node_losts.apply(lambda row: NODE_SIZE * (row.final_losts ** 1.7) + MIN_NODE_SIZE
        if (row.player == player) else 0, axis=1)
        node_progs['node_size'] = node_progs.apply(lambda row: NODE_SIZE * (row.final_progs ** 1.7) + MIN_NODE_SIZE
        if (row.player == player) else 0, axis=1)
        node_final['node_size'] = node_final.apply(lambda row: NODE_SIZE * (row.endings ** 1.7) + MIN_NODE_SIZE
        if (row.player == player) else 0, axis=1)
    elif VIS == 'BUILDUP':
        drawn_nodes['pl_zone_sum'] = drawn_nodes.apply(lambda row: row.pl_zone_sum
        if row.zone == 1
        else row.prog_receptions + row.cross_amount_sum, axis=1)
        node_losts['node_size'] = node_losts.apply(lambda row: NODE_SIZE * (row.final_losts ** 1.7) + MIN_NODE_SIZE
        if (row.zone == 1) else 0, axis=1)
        node_progs['node_size'] = node_progs.apply(lambda row: NODE_SIZE * (row.final_progs ** 1.7) + MIN_NODE_SIZE
        if (row.zone == 1) else 0, axis=1)
        node_final['node_size'] = node_final.apply(lambda row: NODE_SIZE * (row.endings ** 1.7) + MIN_NODE_SIZE
        if (row.zone == 1) else 0, axis=1)
    else:
        node_losts['node_size'] = NODE_SIZE * (node_losts.final_losts ** 1.7) + MIN_NODE_SIZE
        node_progs['node_size'] = NODE_SIZE * (node_progs.final_progs ** 1.7) + MIN_NODE_SIZE
        node_final['node_size'] = NODE_SIZE * (node_final.endings ** 1.7) + MIN_NODE_SIZE

        node_recov['node_size'] = NODE_SIZE * (node_recov.final_recov ** 1.7) + MIN_NODE_SIZE
        node_recep['node_size'] = NODE_SIZE * (node_recep.prog_receptions ** 1.7) + MIN_NODE_SIZE

    drawn_nodes['node_size'] = NODE_SIZE * (drawn_nodes.pl_zone_sum ** 1.7) + MIN_NODE_SIZE
    #     display( drawn_nodes, 'final drawn_nodes', 'length:', len(drawn_nodes))

    #     display( node_losts.head(1), 'node_losts ^')
    #     display( node_progs.head(1), 'node_progs ^')
    #     display( node_final.head(1), 'node_final ^')

    #     team_dest_prog_nodes['node_size'] = NODE_SIZE * (team_dest_prog_nodes.edge_amount_sum**1.7) + MIN_NODE_SIZE
    #     display(losts.head(1))
    #     display('node_progs', node_progs.head(3))

    half_nodes = drawn_nodes[drawn_nodes.zone == 1]
    full_nodes = drawn_nodes[drawn_nodes.zone != 1]
    h_node_losts = node_losts[node_losts.zone == 1]
    full_node_losts = node_losts[node_losts.zone != 1]
    h_node_progs = node_progs[node_progs.zone == 1]
    full_node_progs = node_progs[node_progs.zone != 1]
    h_node_final = node_final[node_final.zone == 1]
    full_node_final = node_final[node_final.zone != 1]

    pitch.scatter(half_nodes.loc_avg_x, half_nodes.loc_avg_y,
                  marker=MarkerStyle('o', fillstyle='top'),
                  s=half_nodes['node_size'], color='white', edgecolors='black',
                  linewidth=1, alpha=.4, ax=ax, zorder=1)

    pitch.scatter(h_node_losts.loc_avg_x, h_node_losts.loc_avg_y,
                  marker=MarkerStyle('o', fillstyle='top'),
                  s=h_node_losts['node_size'], color='grey',
                  linewidth=0, alpha=0.8, ax=ax, zorder=1)

    pitch.scatter(h_node_progs.loc_avg_x, h_node_progs.loc_avg_y,
                  marker=MarkerStyle('o', fillstyle='top'),
                  s=h_node_progs['node_size'], color='red',
                  linewidth=0, alpha=0.8, ax=ax, zorder=3)

    pitch.scatter(h_node_final.loc_avg_x, h_node_final.loc_avg_y,
                  marker=MarkerStyle('o', fillstyle='top'),
                  s=h_node_final['node_size'], color='violet',
                  linewidth=0, alpha=1, ax=ax, zorder=4)

    globals()['node_paths_' + str(period)] = pitch.scatter(full_nodes.loc_avg_x, full_nodes.loc_avg_y,
                                                           marker=MarkerStyle('o', fillstyle='full'),
                                                           s=full_nodes['node_size'], color='white', edgecolors='black',
                                                           linewidth=1, alpha=.4, ax=ax, zorder=1,
                                                           label='Interventions')

    globals()['full_losts_coll_' + str(period)] = pitch.scatter(full_node_losts.loc_avg_x, full_node_losts.loc_avg_y,
                                                                marker=MarkerStyle('o', fillstyle='full'),
                                                                s=full_node_losts['node_size'], color='grey',
                                                                linewidth=0, alpha=0.8, ax=ax, zorder=1,
                                                                label='Progressions')

    globals()['full_progs_coll_' + str(period)] = pitch.scatter(full_node_progs.loc_avg_x, full_node_progs.loc_avg_y,
                                                                marker=MarkerStyle('o', fillstyle='full'),
                                                                s=full_node_progs['node_size'], color='red',
                                                                linewidth=0, alpha=0.8, ax=ax, zorder=3,
                                                                label='Progressions')

    globals()['full_final_coll_' + str(period)] = pitch.scatter(full_node_final.loc_avg_x, full_node_final.loc_avg_y,
                                                                marker=MarkerStyle('o', fillstyle='full'),
                                                                s=full_node_final['node_size'], color='violet',
                                                                linewidth=0, alpha=1, ax=ax, zorder=4,
                                                                label='Progressions')

    globals()['top_losts_coll_' + str(period)] = pitch.scatter(full_node_losts.loc_avg_x, full_node_losts.loc_avg_y,
                                                               marker=MarkerStyle('o', fillstyle='top'),
                                                               s=full_node_losts['node_size'], color='grey',
                                                               linewidth=0, alpha=0.8, ax=ax, zorder=1)

    globals()['top_progs_coll_' + str(period)] = pitch.scatter(full_node_progs.loc_avg_x, full_node_progs.loc_avg_y,
                                                               marker=MarkerStyle('o', fillstyle='top'),
                                                               s=full_node_progs['node_size'], color='red',
                                                               linewidth=0, alpha=0.8, ax=ax, zorder=3)

    globals()['top_final_coll_' + str(period)] = pitch.scatter(full_node_final.loc_avg_x, full_node_final.loc_avg_y,
                                                               marker=MarkerStyle('o', fillstyle='top'),
                                                               s=full_node_final['node_size'], color='violet',
                                                               linewidth=0, alpha=1, ax=ax, zorder=4)

    globals()['bottom_recep_coll_' + str(period)] = pitch.scatter(node_recep.loc_avg_x, node_recep.loc_avg_y,
                                                                  marker=MarkerStyle('o', fillstyle='bottom'),
                                                                  s=node_recep['node_size'],
                                                                  color='orange', edgecolors='black',
                                                                  linewidth=0, alpha=0.8, ax=ax, zorder=3)

    globals()['bottom_recov_coll_' + str(period)] = pitch.scatter(node_recov.loc_avg_x, node_recov.loc_avg_y,
                                                                  marker=MarkerStyle('o', fillstyle='bottom'),
                                                                  s=node_recov['node_size'],
                                                                  color='yellow', edgecolors='black',
                                                                  linewidth=0, alpha=0.8, ax=ax, zorder=2)

    globals()['full_recep_coll_' + str(period)] = pitch.scatter(node_recep.loc_avg_x, node_recep.loc_avg_y,
                                                                marker=MarkerStyle('o', fillstyle='full'),
                                                                s=node_recep['node_size'], picker=True,
                                                                color='orange', edgecolors='black',
                                                                linewidth=0, alpha=0.8, ax=ax, zorder=3,
                                                                label='Receptions')

    globals()['full_recov_coll_' + str(period)] = pitch.scatter(node_recov.loc_avg_x, node_recov.loc_avg_y,
                                                                marker=MarkerStyle('o', fillstyle='full'),
                                                                s=node_recov['node_size'], picker=True,
                                                                color='yellow', edgecolors='black',
                                                                linewidth=0, alpha=0.8, ax=ax, zorder=2,
                                                                label='Receptions')

    # leg= ax.legend()
    # print(leg.get_lines())
    # ctypes.windll.user32.MessageBoxW(0, 'HOla', "Your title", 1)
    # ctypes.windll.user32.MessageBoxW(0, leg.get_lines()[0], "Your title", 1)

    # globals()['full_recep_coll_'+str(period)].set_visible(False)
    # globals()['full_progs_coll_'+str(period)].set_picker(True)
    # globals()['full_recep_coll_'+str(period)].set_picker(True)
    # globals()['full_progs_coll_'+str(period)].set_pickradius(10)
    # globals()['full_recep_coll_'+str(period)].set_pickradius(10)

    # fig.canvas.mpl_connect('pick_event', on_pick)

    """ PAINT EDGES """

    """ Edge width definition """
    #     prog_edges.loc[ (prog_edges.team==team) & (prog_edges.period==period), 
    #                    'width'] = LINE_WIDTH * (prog_edges.edge_amount / REFERENCE_PASSES_AMOUNT) 
    filtered_edges = prog_edges[(prog_edges.team == team) & (prog_edges.period == period)
                                & (prog_edges.edge_amount >= MIN_CONNEX_PASSES)].copy()
    filtered_edges['width'] = LINE_WIDTH * (filtered_edges.edge_amount / REFERENCE_PASSES_AMOUNT)

    #     if VIS=='GLOBAL':
    filt_crosses = vis_crosses[(vis_crosses.team == team) & (vis_crosses.period == period)
                               & (vis_crosses.cross_amount >= MIN_CONNEX_PASSES)].copy()
    filt_crosses['width'] = LINE_WIDTH * (filt_crosses.cross_amount / REFERENCE_PASSES_AMOUNT)
    #     display( filt_crosses)
    paint_crosses(filt_crosses.orig_loc_x, filt_crosses.orig_loc_y,
                  filt_crosses.dest_loc_x, filt_crosses.dest_loc_y,
                  filt_crosses.width, ax, zorder=3, color='violet')

    """ Agafem el tamany dels nodes de progressió """
    filtered_edges = filtered_edges.merge(node_progs[['player', 'zone', 'period', 'node_size']],
                                          how='left', suffixes=('', '_progs'),
                                          left_on=['orig_player', 'origin_zone', 'period'],
                                          right_on=['player', 'zone', 'period'])
    filtered_edges = filtered_edges.rename(columns={'node_size': 'orig_prog_node_size'})

    filtered_edges = filtered_edges.merge(node_progs[['player', 'zone', 'period', 'node_size']],
                                          how='left', suffixes=('', '_progs2'),
                                          left_on=['dest_player', 'dest_zone', 'period'],
                                          right_on=['player', 'zone', 'period'])
    filtered_edges = filtered_edges.rename(columns={'node_size': 'dest_prog_node_size'})

    filtered_edges = filtered_edges.merge(node_final[['player', 'zone', 'period', 'node_size']],
                                          how='left', suffixes=('', '_final'),
                                          left_on=['dest_player', 'dest_zone', 'period'],
                                          right_on=['player', 'zone', 'period'])

    filtered_edges['node_size'] = filtered_edges.apply(lambda row: MIN_NODE_SIZE + NODE_SIZE
    if np.isnan(row.node_size)
    else row.node_size, axis=1)

    filtered_edges['dest_prog_node_size'] = filtered_edges.apply(lambda row: row.node_size
    if np.isnan(row.dest_prog_node_size)
    else row.dest_prog_node_size, axis=1)

    #     display( filtered_edges, 'filtered_edges ^')

    biedges = filtered_edges.merge(filtered_edges[['orig_player', 'origin_zone', 'dest_player', 'dest_zone']],
                                   how='inner', suffixes=('', '_bis'),
                                   left_on=['orig_player', 'origin_zone', 'dest_player', 'dest_zone'],
                                   right_on=['dest_player', 'dest_zone', 'orig_player', 'origin_zone'])

    carry_biedges = biedges[biedges.dest_player == biedges.orig_player]
    pass_biedges = biedges[biedges.dest_player != biedges.orig_player]

    paint_edge_arrows(pass_biedges.orig_loc_x, pass_biedges.orig_loc_y,
                      pass_biedges.dest_loc_x, pass_biedges.dest_loc_y,
                      pass_biedges.dest_prog_node_size, pass_biedges.orig_prog_node_size,
                      pass_biedges.width, bidir=True, ax=ax, color='white', zorder=2, alpha=.8)
    paint_edge_arrows(carry_biedges.orig_loc_x, carry_biedges.orig_loc_y,
                      carry_biedges.dest_loc_x, carry_biedges.dest_loc_y,
                      carry_biedges.dest_prog_node_size, carry_biedges.orig_prog_node_size,
                      carry_biedges.width, bidir=True, ax=ax, color='deepskyblue', zorder=2, alpha=1)

    uniedges = filtered_edges.merge(biedges[['orig_player', 'origin_zone', 'dest_player', 'dest_zone']],
                                    how='left', indicator=True, suffixes=('', '_bis'),
                                    on=['orig_player', 'origin_zone', 'dest_player', 'dest_zone'])
    uniedges = uniedges[uniedges._merge == 'left_only']
    #     display( 'Uniedges from biedges left-only merge', uniedges['width'].head(9))

    carry_uniedges = uniedges[uniedges.dest_player == uniedges.orig_player]
    pass_uniedges = uniedges[uniedges.dest_player != uniedges.orig_player]

    if VIS == 'PLAYER':
        prog_uniedges = pass_uniedges[pass_uniedges.orig_player == player]
        pass_uniedges = pass_uniedges[pass_uniedges.dest_player == player]

        paint_edge_arrows(prog_uniedges.orig_loc_x, prog_uniedges.orig_loc_y,
                          prog_uniedges.dest_loc_x, prog_uniedges.dest_loc_y,
                          prog_uniedges.dest_prog_node_size, prog_uniedges.orig_prog_node_size,
                          prog_uniedges.width, bidir=False, ax=ax, color='yellow', zorder=2, alpha=.55)

    paint_edge_arrows(pass_uniedges.orig_loc_x, pass_uniedges.orig_loc_y,
                      pass_uniedges.dest_loc_x, pass_uniedges.dest_loc_y,
                      pass_uniedges.dest_prog_node_size, pass_uniedges.orig_prog_node_size,
                      pass_uniedges.width, bidir=False, ax=ax, color='white', zorder=2, alpha=.55)
    paint_edge_arrows(carry_uniedges.orig_loc_x, carry_uniedges.orig_loc_y,
                      carry_uniedges.dest_loc_x, carry_uniedges.dest_loc_y,
                      carry_uniedges.dest_prog_node_size, carry_uniedges.orig_prog_node_size,
                      carry_uniedges.width, bidir=False, ax=ax, color='deepskyblue', zorder=2, alpha=.7)

    #     pitch.lines( pass_uniedges.orig_loc_x, pass_uniedges.orig_loc_y, 
    #                  pass_uniedges.dest_loc_x, pass_uniedges.dest_loc_y, 
    #                  lw= pass_uniedges.width, color= 'white', zorder= 1, alpha= 0.8, ax= ax)
    #     pitch.lines( carry_uniedges.orig_loc_x, carry_uniedges.orig_loc_y, 
    #                  carry_uniedges.dest_loc_x, carry_uniedges.dest_loc_y, 
    #                  lw= carry_uniedges.width, color= 'deepskyblue', zorder= 1, alpha= 0.8, ax= ax)
    #     arrows = pitch.lines( filt_crosses.orig_loc_x, filt_crosses.orig_loc_y, 
    #                           filt_crosses.dest_loc_x, filt_crosses.dest_loc_y, 
    #                           lw= filt_crosses.width, color= 'violet', zorder= 3, alpha= 0.8, ax= ax)    

    """ Vis names """
    for index, row in drawn_nodes.iterrows():
        zone = int(row.zone)
        name_color = 'black' if VIS == 'PLAYER' and row.player == player else 'white'
        name = getNick(row.player, team)
        #         if zone>55 or zone==9 or zone==10: name= str(zone)+'_'+name
        ha = 'center'
        if zone == 1:
            loc = (row.loc_avg_x - 2, row.loc_avg_y)
        elif [2, 7, 77].count(zone):
            loc = (row.loc_avg_x, row.loc_avg_y + 1)
            ha = 'left'
        elif [3, 11, 111].count(zone):
            loc = (row.loc_avg_x, row.loc_avg_y - 1)
            ha = 'right'
        elif [6, 9, 99, 10].count(zone):
            loc = (row.loc_avg_x + 1.5, row.loc_avg_y)
        #         elif zone==6: loc= (row.loc_avg_x+1, row.loc_avg_y)
        pitch.annotate(name, xy=loc, color=name_color, va='center',
                       ha=ha, size=9, ax=ax, zorder=7, alpha=1)

    """ Header """
    half = '1st Half' if period == 1 else '2nd Half'
    home_score = len(match_events[(match_events.shot_outcome == 'Goal')
                                  & (match_events.team == team_home)
                                  & (match_events.period == period)])
    away_score = len(match_events[(match_events.shot_outcome == 'Goal')
                                  & (match_events.team == team_away)
                                  & (match_events.period == period)])
    ax.text(0, 122, half, ha='left', weight='bold',
            color=light_white, fontsize=12)

    name_height = 121 if VIS != 'GLOBAL' else 122
    ax.text(40, name_height, TEAM.upper(), ha='center', weight='bold',
            color=light_white, fontsize=12)
    ax.text(80, 123, 'period score:', ha='right', weight='bold',
            color=light_white, fontsize=10)
    ax.text(80, 121, team_home[0:3].upper() + ' ' + str(home_score) + '-'
            + str(away_score) + ' ' + team_away[0:3].upper(),
            ha='right', weight='bold', color=light_white, fontsize=10)

    """ Lateral tips """
    line_props = {'linewidth': 1, 'color': 'red', 'zorder': 4}
    commentline1 = Line2D([80.5, 88], [BROKEN_HEIGHT, BROKEN_HEIGHT], linestyle='--', **line_props)
    commentline2 = Line2D([80.5, 88], [TOP_TEN_HEIGHT, TOP_TEN_HEIGHT], linestyle='--', **line_props)
    ax.add_artist(commentline1)
    ax.text(83.5, BROKEN_HEIGHT + 2, 'Broken', color='red', ha='left', fontsize=9)
    ax.text(83.5, BROKEN_HEIGHT + 0.5, 'block', color='red', ha='left', fontsize=9)
    ax.add_artist(commentline2)
    ax.text(83.5, TOP_TEN_HEIGHT + 1.5, 'Last', color='red', ha='left', fontsize=9)
    ax.text(83.5, TOP_TEN_HEIGHT, 'def.', color='red', ha='left', fontsize=9)
    ax.text(83.5, TOP_TEN_HEIGHT - 1.5, 'line', color='red', ha='left', fontsize=9)

    """ Tactics """
    if period == 1:
        """ Starting LineUp """
        form, lineup = get_match_lineup(TEAM, lineups)
        players = list(lineup.keys())
        pl_pos = 0
        pl_nick = getNick(players[pl_pos], team)

        ax.text(83.5, EPS_TOP_HEIGHT, 'Formation:', color='black', ha='left', fontsize=9, weight='bold')
        ax.text(83.5, EPS_TOP_HEIGHT - 5, 'Starting lineup:', color='black', ha='left', fontsize=9, weight='bold')
        line = EPS_TOP_HEIGHT - 7
        ax.text(83.5, line, pl_nick, color='black', ha='left', fontsize=9)
        formation = '1'
        for ch in str(form):
            formation += '-' + ch
            line -= 1
            for i in range(int(ch)):
                pl_pos += 1
                pl_nick = getNick(players[pl_pos], team)
                line -= 1.5
                ax.text(83.5, line, pl_nick,
                        color='black', ha='left', fontsize=9)

        ax.text(83.5, EPS_TOP_HEIGHT - 2, formation, color='black', ha='left', fontsize=9)


