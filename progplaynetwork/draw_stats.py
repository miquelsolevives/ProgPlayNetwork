import numpy as np # numerical python package
from matplotlib.colors import to_rgba
from progplaynetwork import pitch as ppn_pitch

white_trans = np.array(to_rgba('white'))
white_trans[3] = 0.6

def draw_global_stats( team, period, ax, passes, edge_events):
    """ STATS """
    light_black = np.array(to_rgba('black'))
    light_black[3] = 0.5
    tot_pas= passes[ (passes.team==team) & (passes.period==period) ]
    ax.text(4, 57, 'Completed passes:', ha='left', color=light_black , fontsize=10)
    ax.text(23, 57, len(tot_pas), ha='right', color=light_black , fontsize=10)
    ax.text(6, 55, 'High block:', ha='left', color= light_black, fontsize=10)
    ax.text(23, 55, len(tot_pas[ tot_pas.opp_def_type=='High block']), 
            ha='right', color= light_black, fontsize=10)
    ax.text(6, 53, 'Retrieved block:', ha='left', color= 'black', fontsize=10)
    ret_block= len(tot_pas[ tot_pas.opp_def_type=='Retrieved block'])
    ax.text(23, 53, ret_block, ha='right', color= 'black', fontsize=10)
    ax.text(6, 51, 'Broken block:', ha='left', color= light_black, fontsize=10)
    ax.text(23, 51, len(tot_pas[ tot_pas.opp_def_type=='Broken block']), 
            ha='right', color= light_black, fontsize=10)
    
    ax.arrow(24, 53.5, 3, 0, head_width=0.75, head_length=0.75, lw=1.5, ec='black', fc='black')
    prog_plays= edge_events[ (edge_events.progression) 
                                & (edge_events.team==team) 
                                & (edge_events.period==period)]
    prog_perc= round( len(prog_plays) / ret_block *100, 1)
    ax.text(29, 53, 'Progressive Plays: '+ str( len(prog_plays))+', '+str(prog_perc)+'%', 
            ha='left', color= 'black', fontsize=10)
    ax.arrow(54, 53.8, 9, 1, head_width=0.75, head_length=0.75, lw=1.5, ec='deepskyblue', fc='deepskyblue')
    ax.arrow(54, 53.2, 9, -1, head_width=0.75, head_length=0.75, lw=1.5, ec='white', fc='white')

    ax.text(65, 54.5, 'Carries:', ha='left', weight='bold',
                         color= 'deepskyblue', fontsize=10)
    ax.text(72, 54.5, len( prog_plays[ prog_plays.type=='Carry']), ha='left', weight='bold',
                         color= 'deepskyblue', fontsize=10)    
    ax.text(65, 51.5, 'Passes:', ha='left', weight='bold',
                         color= 'white', fontsize=10)    
    ax.text(72, 51.5, len( prog_plays[ prog_plays.type=='Pass']), ha='left', weight='bold',
                         color= 'white', fontsize=10)      


def draw_zone_stats( team, period, ax, buildup_zones, edges ):
    """ """
    ax.text( 40, 124, 'Build-up Analysis', ha='center', weight='bold',
             bbox=dict( fc=white_trans, ec=white_trans, pad=2.0), color= 'red' , fontsize=11)
    
    buildup_progs_sum= edges[ (edges.period==period) & (edges.team==team)
                             & (edges.origin_zone==1) & (edges.progression==True)] ['edge_amount'].sum()
    buildup_plays_sum= edges[ (edges.period==period) & (edges.team==team) 
                             & (edges.origin_zone==1) ] ['edge_amount'].sum()

    zone6_sum= buildup_zones[ (buildup_zones.period==period) & (buildup_zones.team==team) 
                             & (buildup_zones.dest_zone==6)].zone_sum.to_list()
    zone6_acc= zone6_sum[0] if len(zone6_sum) else 0
    ax.text( 40, 87, str( round( zone6_acc *100 / buildup_progs_sum)) +' %', ha='center', weight='bold', zorder=99,
             bbox=dict( fc=white_trans, ec=white_trans, pad=2.0), color= 'red', fontsize=11)
    
    zone10_sum= buildup_zones[ (buildup_zones.period==period) & (buildup_zones.team==team) 
                             & (buildup_zones.dest_zone==10)].zone_sum.to_list()
    zone10_acc= zone10_sum[0] if len(zone10_sum) else 0
    ax.text( 40, 100, str( round( zone10_acc *100 / buildup_progs_sum)) +' %', ha='center', weight='bold', zorder=99,
             bbox=dict( fc=white_trans, ec=white_trans, pad=2.0), color= 'red', fontsize=11)

    zone9_sum= buildup_zones[ (buildup_zones.period==period) & (buildup_zones.team==team) 
                             & (buildup_zones.dest_zone==9)].zone_sum.to_list()
    zone9_acc= zone9_sum[0] if len(zone9_sum) else 0
    ax.text( 40, 104, str( round( zone9_acc *100 / buildup_progs_sum)) +' %', ha='center', weight='bold', zorder=99,
             bbox=dict( fc=white_trans, ec=white_trans, pad=2.0), color= 'red', fontsize=11)
    
    zone2_sum= buildup_zones[ (buildup_zones.period==period) & (buildup_zones.team==team) 
                             & (buildup_zones.dest_zone==2)].zone_sum.to_list()
    zone2_acc= zone2_sum[0] if len(zone2_sum) else 0
    ax.text( ppn_pitch.RIGHT_EXT_WIDTH+0.5, 88, str( round( zone2_acc *100 / buildup_progs_sum)) +' %', ha='left', weight='bold', zorder=99,
             bbox=dict( fc=white_trans, ec=white_trans, pad=2.0), color= 'red', fontsize=11)
    
    zone3_sum= buildup_zones[ (buildup_zones.period==period) & (buildup_zones.team==team) 
                             & (buildup_zones.dest_zone==3)].zone_sum.to_list()
    zone3_acc= zone3_sum[0] if len(zone3_sum) else 0
    ax.text( ppn_pitch.LEFT_EXT_WIDTH-0.5, 88, str( round( zone3_acc *100 / buildup_progs_sum)) +' %', ha='right', weight='bold', zorder=99,
             bbox=dict( fc=white_trans, ec=white_trans, pad=2.0), color= 'red', fontsize=11)    
    
    zone7_sum= buildup_zones[ (buildup_zones.period==period) & (buildup_zones.team==team) 
                             & (buildup_zones.dest_zone==7)].zone_sum.to_list()
    zone7_acc= zone7_sum[0] if len(zone7_sum) else 0
    ax.text( ppn_pitch.RIGHT_EXT_WIDTH+0.5, ppn_pitch.TOP_TEN_HEIGHT, str( round( zone7_acc *100 / buildup_progs_sum)) +' %', ha='left', weight='bold', zorder=99,
             bbox=dict( fc=white_trans, ec=white_trans, pad=2.0), color= 'red', fontsize=11)
    
    zone11_sum= buildup_zones[ (buildup_zones.period==period) & (buildup_zones.team==team) 
                             & (buildup_zones.dest_zone==11)].zone_sum.to_list()
    zone11_acc= zone11_sum[0] if len(zone11_sum) else 0
    ax.text( ppn_pitch.LEFT_EXT_WIDTH-0.5, ppn_pitch.TOP_TEN_HEIGHT, str( round( zone11_acc *100 / buildup_progs_sum)) +' %', ha='right', weight='bold', zorder=99,
             bbox=dict( fc=white_trans, ec=white_trans, pad=2.0), color= 'red', fontsize=11)      
    
    ax.text( 1, 55, 'Build-up progression plays: ', ha='left',
             bbox=dict( fc=white_trans, edgecolor=white_trans, pad=2.5), color= 'red', fontsize=11)
    ax.text( 27, 55, str(buildup_progs_sum), ha='left', weight='bold',
             bbox=dict( fc=white_trans, ec=white_trans, pad=2.5), color= 'red', fontsize=11)

    ax.text( 1, 52, 'Progression perc.: ', ha='left',
             bbox=dict( fc=white_trans, edgecolor=white_trans, pad=2.5), color= 'red', fontsize=11)
    ax.text( 27, 52, str( round(buildup_progs_sum *100 / buildup_plays_sum, 1))+ ' %', ha='left',
             bbox=dict( fc=white_trans, ec=white_trans, pad=2.5), color= 'red', fontsize=11, weight='bold') 
    
    
def draw_player_stats( team, period, ax, player ):
    """ """
    white_trans = np.array(to_rgba('white'))
    white_trans[3]= 0.6    

    player_interv= nodes[ (nodes.player==player) & (nodes.period==period) 
                        ].pl_zone_sum.sum()
    pl_fouls_won= len( node_events[ (node_events.player==player) & (node_events.period==period) 
                                   & (node_events.type == 'Foul Won') ])
    player_finaliz= vis_finaliz[ (vis_finaliz.player==player) & (vis_finaliz.period==period) 
                               ].endings.sum()
    player_losts= lost_nodes[ (lost_nodes.player==player) & (lost_nodes.period==period) 
                            ].losts.sum()
    player_prog = orig_prog_nodes[ (orig_prog_nodes.player == player) & (orig_prog_nodes.period == period) 
                                 ].progs.sum()

    ax.text(4, 56, getNick( player, team), ha='left', color= 'black', fontsize=11, weight='bold')
    ax.text(4, 53, 'Total interventions:', ha='left', color= 'black', fontsize=10)
    ax.text(23, 53, player_interv, ha='right', color= 'black', fontsize=10)
    ax.arrow(24.5, 53.5, 5, 0, head_width=0.75, head_length=0.75, lw=1.5, ec='black', fc='black', alpha=0.7)
    prog_perc= round( player_prog / player_interv *100, 1)
    ax.text(34, 57, 'Fouls won: ', ha='left', color= 'black', 
            fontsize=10, bbox=dict( fc=white_trans, ec=white_trans, pad=1.5))
    ax.text(34, 55, 'Finalizations: ', ha='left', color= 'fuchsia', 
            fontsize=10, bbox=dict( fc=white_trans, ec=white_trans, pad=1.5))
    ax.text(34, 53, 'Progressive Plays: ', ha='left', color= 'red', 
            fontsize=10, bbox=dict( fc=white_trans, ec=white_trans, pad=1.5))
    ax.text(34, 51, 'Losts: ', ha='left', color= 'grey', 
            fontsize=10, bbox=dict( fc=white_trans, ec=white_trans, pad=1.5))
    ax.text(53, 57, pl_fouls_won, ha='right', color= 'black', fontsize=10)
    ax.text(53, 55, player_finaliz, ha='right', color= 'black', fontsize=10)
    ax.text(53, 53, player_prog, ha='right', color= 'black', fontsize=10)
    # +', '+str(prog_perc)+'%'
    ax.text(53, 51, player_losts, ha='right', color= 'black', fontsize=10)

    ax.arrow(56, 54, 7, 1.6, head_width=0.75, head_length=0.75, lw=1.5, ec='deepskyblue', fc='deepskyblue')
    ax.arrow(56, 53.5, 7, 0, head_width=0.75, head_length=0.75, lw=1.5, ec='yellow', fc='yellow')
    ax.arrow(58, 51, 5, 0, head_width=0.75, head_length=0.75, lw=1.5, ec='white', fc='white')

    pl_carries= prog_edges[ (prog_edges.period == period)
                           & (prog_edges.dest_player == player) & (prog_edges.orig_player == player) ]
    pl_passes= prog_edges[ (prog_edges.period == period)
                          & (prog_edges.orig_player == player) & (prog_edges.dest_player != player) ]
    pl_recep= prog_edges[ (prog_edges.period == period)
                           & (prog_edges.dest_player == player) & (prog_edges.orig_player != player) ]
    ax.text(65, 55.5, 'Carries:', ha='left', weight='bold', color= 'deepskyblue', fontsize=10)
    ax.text(75, 55.5, pl_carries.edge_amount.sum(), ha='right', weight='bold', color= 'deepskyblue', fontsize=10)       
    ax.text(65, 53, 'Passes:', ha='left', weight='bold', color= 'yellow', fontsize=10)
    ax.text(75, 53, pl_passes.edge_amount.sum(), ha='right', weight='bold', color= 'yellow', fontsize=10)
    ax.text(65, 50.5, 'Receptions:', ha='left', weight='bold', color= 'white', fontsize=10)    
    ax.text(78, 50.5, pl_recep.edge_amount.sum(), ha='right', weight='bold', color= 'white', fontsize=10)
    
    ax.text( 40, 124, 'Player Analysis', ha='center', weight='bold',
             bbox=dict( fc=white_trans, ec=white_trans, pad=2.0), color= 'red', fontsize=11)