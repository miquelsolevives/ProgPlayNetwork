from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from matplotlib.widgets import RadioButtons
import mplsoccer as mpl
from statsbombpy import sb # statsbomb api
import matplotlib.pyplot as plt # matplotlib for plotting
from mplsoccer import Pitch, Sbopen, FontManager, add_image # for drawing the football pitch
import numpy as np # numerical python package
from matplotlib.colors import to_rgba
from matplotlib.markers import MarkerStyle

from progplaynetwork import tools as ppn_tools
from progplaynetwork import pitch as ppn_pitch
from progplaynetwork import db_players as ppn_db
from progplaynetwork import statsbomb as ppn_sb
from progplaynetwork import paint as ppn_paint
from progplaynetwork import df_ppn as ppn_df
from progplaynetwork import draw_ppn as ppn_draw
from progplaynetwork import draw_stats as ppn_stats

class AppPPN( QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.version= '11'
        self.vis= 'GLOBAL'
        self.player= ""
        self.MIN_CONNEX_PASSES = 1
        
        self.wc_matches= sb.matches(competition_id=43, season_id=106)
        self.wc_matches.sort_values('match_date', inplace=True)
        teams= self.wc_matches.home_team.drop_duplicates().to_list()
        teams.insert(0,'-')
        
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        self.layout = QtWidgets.QVBoxLayout(self._main)

        lab1= QtWidgets.QLabel( text='Filter by team')
        cb1 = QtWidgets.QComboBox()
        lab2= QtWidgets.QLabel( text='Select the match')
        cb2 = QtWidgets.QComboBox()
        
        matches= []
        i=0
        cb2.addItem( '-')
        for idx, wc_match in self.wc_matches.iterrows():
            match_text= (wc_match.home_team+ ' '+str(wc_match.home_score)+'-'
                         +str(wc_match.away_score)+' '+ wc_match.away_team +', '+wc_match.competition_stage)
            matches.append( match_text)
            cb2.addItem( match_text)
        
        cb1.addItems( teams)
        cb2.currentIndexChanged.connect( self.carry_match_cb)
        self.layout.addWidget(lab1)
        self.layout.addWidget(cb1)
        self.layout.addWidget(lab2)
        self.layout.addWidget(cb2)
        
        lab3= QtWidgets.QLabel( text='Select the team')
        self.cb3 = QtWidgets.QComboBox()
        self.cb3.currentIndexChanged.connect( self.carry_players )
        self.layout.addWidget( lab3)
        self.layout.addWidget( self.cb3)
        self.cb3.setDisabled(True)
        
        lab4= QtWidgets.QLabel( text='Select the viz')
        self.cb4 = QtWidgets.QComboBox()
        self.cb4.addItems( ['GLOBAL', 'BUILDUP', 'PLAYER'])
        self.cb4.currentIndexChanged.connect( self.carry_players )
        self.vis= self.cb4.currentText()
        
        lab5= QtWidgets.QLabel( text='Select the player')
        self.cb5 = QtWidgets.QComboBox()
        self.cb5.setDisabled(True)
        self.cb5.currentIndexChanged.connect( self.select_player )
        self.layout.addWidget(lab4)
        self.layout.addWidget(self.cb4)
        self.layout.addWidget(lab5)
        self.layout.addWidget(self.cb5)
        
        self.but= QtWidgets.QPushButton('Show Viz')
        self.layout.addWidget(self.but)
        self.but.setDisabled(True)
        self.but.clicked.connect( self.show_ppn)
        
        
    def select_player( self, val):
        """ """
        self.player= self.cb5.currentText()
        self.but.setDisabled(False)
        
    def carry_players( self, val):
        """ Put players of selected team to ComboBox """
        self.team= self.cb3.currentText()
        self.vis= self.cb4.currentText()
        if self.cb4.currentText() == 'PLAYER':
            self.cb5.setDisabled( False)
            self.cb5.clear()
            players= self.home_players if self.cb3.currentText() == self.team_home else self.away_players
            self.cb5.addItems( list(players))
            self.player= self.cb5.currentText()
        else:
            self.cb5.setDisabled( True)
        self.but.setDisabled(False)
        
        
    def carry_match_cb( self, val):
        """ """
        self.cb3.clear()
        self.cb3.setDisabled(False)
        self.match_id= self.wc_matches.iloc[val-1].match_id
        self.carry_match( self.match_id )
        self.match_built= False
        self.cb3.addItem( self.team_home)
        self.team= self.team_home
        self.cb3.addItem( self.team_away)
        self.but.setDisabled(False)
        
        
    def carry_match( self, match_id):
        """ """
        self.match_events = sb.events(match_id= match_id, fmt='dataframe')
        # wc_matches= sb.matches(competition_id=43, season_id=106)
        self.lineups = self.match_events[ self.match_events.type=='Starting XI'][['team', 'tactics']]
        # match_events[match_events.type== 'Starting XI']['tactics'][0]
        subs = self.match_events[ self.match_events.type=='Substitution'][['team', 'substitution_replacement']]
        self.team_home = self.lineups.loc[0]['team']
        self.team_away = self.lineups.loc[1]['team']
        dict_home = self.lineups.loc[0]['tactics']
        dict_away = self.lineups.loc[1]['tactics']
        self.home_players, self.away_players, self.home_GK, self.away_GK = ppn_sb.get_match_players( dict_home, dict_away, subs, self.team_home)

        
    def build_ppn( self):
        """ CONSTRUCCIO DE LA PASSING NETWORK """
        self.edge_events= ppn_df.get_edge_events( self.match_events)
        self.passes= ppn_df.get_pass_events( self.match_events)
        self.node_events= ppn_df.get_node_events( self.match_events)

        losts= ppn_df.get_losts( self.node_events)
        finals= ppn_df.get_finalizations( self.node_events)
        recovs= ppn_df.get_recoveries( self.match_events)

        self.nodes= ppn_df.get_nodes( self.node_events)
        self.lost_nodes= ppn_df.get_lost_nodes( losts)
        self.final_nodes= ppn_df.get_final_nodes( finals)
        self.recov_nodes= ppn_df.get_recov_nodes( recovs)

        home_mean = self.edge_events[ self.edge_events.team == self.team_home].groupby('team')['opp_block_height'].mean()
        away_mean = self.edge_events[ self.edge_events.team == self.team_away].groupby('team')['opp_block_height'].mean()
        ppn_pitch.zone_normalizing( self.team_home, 1, self.nodes, self.home_GK, home_mean)
        ppn_pitch.zone_normalizing( self.team_away, 1, self.nodes, self.away_GK, away_mean)
        ppn_pitch.zone_normalizing( self.team_home, 2, self.nodes, self.home_GK, home_mean)
        ppn_pitch.zone_normalizing( self.team_away, 2, self.nodes, self.away_GK, away_mean)

        self.edges= ppn_df.get_edges( self.edge_events, self.nodes)
        self.crosses= ppn_df.get_crosses( self.match_events, self.nodes)

        
    def build_match( self):
        """ """
        self.match_frames = sb.frames( match_id= self.match_id, fmt='dataframe')

        """ INIT & COOKING NEW NEEDED ATRIBUTES """
        ppn_df.set_ppn_params_1( self.match_events, self.match_frames)
        ppn_sb.set_recovery_zones_2( self.match_events)
        """ SETTING THE ZONES FOR OUR EVENTS (passes, carries and receptions) """
        ppn_sb.set_EPS_params( self.match_events, self.match_frames)
        """ SETTING NEEDED PARAMS AFTER DEFINING TRACKING ZONES """
        ppn_df.set_ppn_params_2( self.match_events, self.match_frames)
        
        """ MAKING THE NETWORK """
        self.build_ppn()
        self.match_built= True
        

    def show_ppn( self, val):
        """ Check if needed to build the match checking the last loaded """
        self.but.setDisabled(True)
        if not self.match_built:
            self.build_match()
        
        self.draw_vis()


    def draw_player_stats( self, period, player, ax ):
        """ """
        white_trans = np.array(to_rgba('white'))
        white_trans[3]= 0.6    

        player_interv= self.nodes[ (self.nodes.player==player) & (self.nodes.period==period) 
                            ].pl_zone_sum.sum()
        pl_fouls_won= len( self.node_events[ (self.node_events.player==player) & (self.node_events.period==period) 
                                       & (self.node_events.type == 'Foul Won') ])
        player_finaliz= self.vis_finaliz[ (self.vis_finaliz.player==player) & (self.vis_finaliz.period==period) 
                                   ].endings.sum()
        player_losts= self.lost_nodes[ (self.lost_nodes.player==player) & (self.lost_nodes.period==period) 
                                ].losts.sum()
        player_prog = self.orig_prog_nodes[ (self.orig_prog_nodes.player == player) 
                                           & (self.orig_prog_nodes.period == period) 
                                     ].progs.sum()

        ax.text(4, 56, ppn_db.getNick( player, self.team), ha='left', color= 'black', fontsize=11, weight='bold')
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
        ax.arrow(56, 53.5, 7, 0, head_width=0.75, head_length=0.75, lw=1.5, ec='red', fc='red')
        ax.arrow(58, 51, 5, 0, head_width=0.75, head_length=0.75, lw=1.5, ec='orange', fc='orange')

        pl_carries= self.prog_edges[ (self.prog_edges.period == period)
                                    & (self.prog_edges.dest_player == player) 
                                    & (self.prog_edges.orig_player == player) ]
        pl_passes= self.prog_edges[ (self.prog_edges.period == period)
                                   & (self.prog_edges.orig_player == player) 
                                   & (self.prog_edges.dest_player != player) ]
        pl_recep= self.prog_edges[ (self.prog_edges.period == period)
                                  & (self.prog_edges.dest_player == player) 
                                  & (self.prog_edges.orig_player != player) ]
        ax.text(65, 55.5, 'Carries:', ha='left', weight='bold', color= 'deepskyblue', fontsize=10)
        ax.text(75, 55.5, pl_carries.edge_amount.sum(), ha='right', weight='bold', color= 'deepskyblue', fontsize=10)       
        ax.text(65, 53, 'Passes:', ha='left', weight='bold', color= 'red', fontsize=10)
        ax.text(75, 53, pl_passes.edge_amount.sum(), ha='right', weight='bold', color= 'red', fontsize=10)
        ax.text(65, 50.5, 'Receptions:', ha='left', weight='bold', color= 'orange', fontsize=10)    
        ax.text(78, 50.5, pl_recep.edge_amount.sum(), ha='right', weight='bold', color= 'orange', fontsize=10)

        ax.text( 40, 124, 'Player Analysis', ha='center', weight='bold',
                 bbox=dict( fc=white_trans, ec=white_trans, pad=2.0), color= 'red', fontsize=11)


    def draw_prog_play_network_3( self, team, period, pitch, ax, player):
        """ DRAW PPN TO FIG AXes """
        NODE_SIZE = 25
        MIN_NODE_SIZE = 75
        LINE_WIDTH = 1
        
        """ filtering Team & Period Nodes """
        filtered_nodes = self.nodes[ (self.nodes.team == team) & (self.nodes.period == period)]
        filt_fin_nodes = self.vis_finaliz[ (self.vis_finaliz.team == team) 
                                              & (self.vis_finaliz.period == period)]
        filt_lost_nodes = self.lost_nodes[ (self.lost_nodes.team == team) 
                                          & (self.lost_nodes.period == period)]
        filt_recov_nodes = self.recov_nodes[ (self.recov_nodes.team == team) 
                                            & (self.recov_nodes.period == period)]
        dest_nodes = self.dest_prog_nodes[ (self.dest_prog_nodes.team == team) 
                                          & (self.dest_prog_nodes.period == period)]
        orig_nodes = self.orig_prog_nodes[ (self.orig_prog_nodes.team == team) 
                                          & (self.orig_prog_nodes.period == period)]
        cross_recep_nodes = self.dest_cross_nodes[ (self.dest_cross_nodes.team == team)
                                                  & (self.dest_cross_nodes.period == period)]
        cross_orig_nodes = self.orig_cross_nodes[ (self.orig_cross_nodes.team == team)
                                                 & (self.orig_cross_nodes.period == period)]

        filtered_nodes.set_index(['player', 'zone', 'period', 'team'], inplace=True)
        filt_lost_nodes.set_index(['player', 'zone', 'period', 'team'], inplace=True)
        filt_fin_nodes.set_index(['player', 'zone', 'period', 'team'], inplace=True)
        filt_recov_nodes.set_index(['player', 'zone', 'period', 'team'], inplace=True)
        orig_nodes.set_index(['player', 'zone', 'period', 'team'], inplace=True)
        dest_nodes.set_index(['player', 'zone', 'period', 'team'], inplace=True)
        cross_recep_nodes.set_index(['player', 'zone', 'period', 'team'], inplace=True)
        cross_orig_nodes.set_index(['player', 'zone', 'period', 'team'], inplace=True)

        """ Getting the nodes to paint from Prog Edges + Finalizations """
        # [[]] --> We don't need the columns, just the rows (index columns)
        drawn_nodes = dest_nodes[[]].merge( orig_nodes[[]], how='outer',
                                            left_index=True, right_index=True)
        if self.vis == 'GLOBAL':
            drawn_nodes = filt_fin_nodes[[]].merge( drawn_nodes, how='outer', left_index=True, right_index=True)
            drawn_nodes = filtered_nodes[ filtered_nodes.pl_zone_sum > 4
                                         ][[]].merge( drawn_nodes, how='outer', left_index=True, right_index=True)
        elif self.vis == 'BUILDUP':
            drawn_nodes = filtered_nodes[ (filtered_nodes.pl_zone_sum > 5)
                                        ][[]].merge( drawn_nodes, how='outer', left_index=True, right_index=True)

        drawn_nodes = cross_recep_nodes[ ['cross_amount_sum']
                                       ].merge( drawn_nodes, how='outer', left_index=True, right_index=True)
        drawn_nodes.cross_amount_sum.fillna( 0, inplace=True)
        drawn_nodes = cross_orig_nodes[[]].merge( drawn_nodes, how='outer', left_index=True, right_index=True)

        """ Getting the info to paint """
        drawn_nodes = filtered_nodes.merge( drawn_nodes, how='inner',
                                            left_index=True, right_index=True)
        drawn_nodes = dest_nodes[['prog_receptions']].merge(drawn_nodes, how='right', left_index=True, right_index=True)
        drawn_nodes.prog_receptions.fillna( 0, inplace=True)
        drawn_nodes = orig_nodes[['progs']].merge(drawn_nodes, how='right', left_index=True, right_index=True)
        drawn_nodes.progs.fillna( 0, inplace=True)

        """ S'ha de fer de drawn enlloc de filtered pq no volem nodes només amb pèrdues """
        node_losts = filt_lost_nodes.merge( drawn_nodes, how='inner', left_index=True, right_index=True)
        node_recov = filt_recov_nodes.merge( drawn_nodes, how='inner', left_index=True, right_index=True)
        node_progs = orig_nodes[[]].merge( drawn_nodes, how='inner', left_index=True, right_index=True)
        node_recep = dest_nodes[[]].merge( drawn_nodes, how='inner', left_index=True, right_index=True)
        # display( node_recov)
        # display( node_losts)
        # display( node_recep)
        # display( node_progs)
        # display( filt_fin_nodes)
        node_final = filt_fin_nodes.merge( filtered_nodes, how='left', left_index=True, right_index=True)
        """ Merges to get the info of inferior node slice """
        node_progs = node_progs.merge( node_final[['endings']],
                                      how='left', left_index=True, right_index=True)
        # node_progs.endings.fillna( 0, inplace=True)
        node_progs['final_progs'] = node_progs[['progs', 'endings']].sum(axis=1)

        node_losts = node_losts.merge( node_progs[['final_progs']],
                                      how='left', left_index=True, right_index=True)
        # node_losts.final_progs.fillna( 0, inplace=True)
        node_losts['final_losts'] = node_losts[['losts', 'final_progs']].sum(axis=1)
        node_recov['final_recov'] = node_recov[['recov', 'prog_receptions']].sum(axis=1)
        
        drawn_nodes.reset_index(inplace=True)
        node_losts.reset_index(inplace=True)
        node_progs.reset_index(inplace=True)
        node_final.reset_index(inplace=True)
        node_recep.reset_index(inplace=True)
        node_recov.reset_index(inplace=True)

        """ Node size definition """
        if self.vis == 'PLAYER':
            drawn_nodes['pl_zone_sum'] = drawn_nodes.apply( lambda row: row.pl_zone_sum
                                                           if row.player == player
                                                           else row.prog_receptions + row.progs, axis=1)
            node_losts['node_size'] = node_losts.apply( lambda row: NODE_SIZE * (row.final_losts ** 1.7) + MIN_NODE_SIZE
                                                       if (row.player == player) else 0, axis=1)
            node_progs['node_size'] = node_progs.apply( lambda row: NODE_SIZE * (row.final_progs ** 1.7) + MIN_NODE_SIZE
                                                       if (row.player == player) else 0, axis=1)
            node_final['node_size'] = node_final.apply( lambda row: NODE_SIZE * (row.endings ** 1.7) + MIN_NODE_SIZE
                                                       if (row.player == player) else 0, axis=1)
            node_recov['node_size'] = node_recov.apply( lambda row: NODE_SIZE * (row.final_recov ** 1.7) + MIN_NODE_SIZE
                                                       if (row.player == player) else 0, axis=1)
            node_recep['node_size'] = node_recep.apply( lambda row: NODE_SIZE * (row.prog_receptions ** 1.7) + MIN_NODE_SIZE
                                                       if (row.player == player) else 0, axis=1)
            
        elif self.vis == 'BUILDUP':
            drawn_nodes['pl_zone_sum'] = drawn_nodes.apply( lambda row: row.pl_zone_sum
                                                           if row.zone == 1
                                                           else row.prog_receptions + row.cross_amount_sum, axis=1)
            node_losts['node_size'] = node_losts.apply( lambda row: NODE_SIZE * (row.final_losts ** 1.7) + MIN_NODE_SIZE
                                                       if (row.zone == 1) else 0, axis=1)
            node_progs['node_size'] = node_progs.apply( lambda row: NODE_SIZE * (row.final_progs ** 1.7) + MIN_NODE_SIZE
                                                       if (row.zone == 1) else 0, axis=1)
            node_final['node_size'] = node_final.apply( lambda row: NODE_SIZE * (row.endings ** 1.7) + MIN_NODE_SIZE
                                                       if (row.zone == 1) else 0, axis=1)
            node_recep['node_size'] = NODE_SIZE * (node_recep.prog_receptions ** 1.7) + MIN_NODE_SIZE
            
        else:
            node_losts['node_size'] = NODE_SIZE * (node_losts.final_losts ** 1.7) + MIN_NODE_SIZE
            node_progs['node_size'] = NODE_SIZE * (node_progs.final_progs ** 1.7) + MIN_NODE_SIZE
            node_final['node_size'] = NODE_SIZE * (node_final.endings ** 1.7) + MIN_NODE_SIZE

            node_recov['node_size'] = NODE_SIZE * (node_recov.final_recov ** 1.7) + MIN_NODE_SIZE
            node_recep['node_size'] = NODE_SIZE * (node_recep.prog_receptions ** 1.7) + MIN_NODE_SIZE

        drawn_nodes['node_size'] = NODE_SIZE * (drawn_nodes.pl_zone_sum ** 1.7) + MIN_NODE_SIZE

        half_nodes = drawn_nodes[ drawn_nodes.zone == 1]
        full_nodes = drawn_nodes[ drawn_nodes.zone != 1]
        h_node_losts = node_losts[ node_losts.zone == 1]
        full_node_losts = node_losts[ node_losts.zone != 1]
        h_node_progs = node_progs[ node_progs.zone == 1]
        full_node_progs = node_progs[ node_progs.zone != 1]
        h_node_final = node_final[ node_final.zone == 1]
        full_node_final = node_final[ node_final.zone != 1]
        """ We don't want the bottom data for buildup nodes """
        node_recep= node_recep[ node_recep.zone != 1]
        node_recov= node_recov[ node_recov.zone != 1]

        pitch.scatter(half_nodes.loc_avg_x, half_nodes.loc_avg_y,
                      marker= MarkerStyle('o', fillstyle='top'),
                      s= half_nodes['node_size'], color='white', edgecolors='black',
                      linewidth=1, alpha=.4, ax=ax, zorder=1)

        pitch.scatter(h_node_losts.loc_avg_x, h_node_losts.loc_avg_y,
                      marker= MarkerStyle('o', fillstyle='top'),
                      s= h_node_losts['node_size'], color='grey',
                      linewidth=0, alpha=0.8, ax=ax, zorder=1)

        pitch.scatter(h_node_progs.loc_avg_x, h_node_progs.loc_avg_y,
                      marker= MarkerStyle('o', fillstyle='top'),
                      s= h_node_progs['node_size'], color='red',
                      linewidth=0, alpha=0.8, ax=ax, zorder=3)

        pitch.scatter(h_node_final.loc_avg_x, h_node_final.loc_avg_y,
                      marker= MarkerStyle('o', fillstyle='top'),
                      s= h_node_final['node_size'], color='violet',
                      linewidth=0, alpha=1, ax=ax, zorder=4)

        globals()['node_paths_' + str(period)] = pitch.scatter( full_nodes.loc_avg_x, full_nodes.loc_avg_y,
                                                               marker= MarkerStyle('o', fillstyle='full'),
                                                               s= full_nodes['node_size'], color='white', edgecolors='black',
                                                               linewidth=1, alpha=.4, ax=ax, zorder=1,
                                                               label='Interventions')

        globals()['full_losts_coll_' + str(period)] = pitch.scatter( full_node_losts.loc_avg_x, full_node_losts.loc_avg_y,
                                                                    marker= MarkerStyle('o', fillstyle='full'),
                                                                    s= full_node_losts['node_size'], color='grey',
                                                                    linewidth=0, alpha=0.8, ax=ax, zorder=1,
                                                                    label='Progressions')

        globals()['full_progs_coll_' + str(period)] = pitch.scatter( full_node_progs.loc_avg_x, full_node_progs.loc_avg_y,
                                                                    marker= MarkerStyle('o', fillstyle='full'),
                                                                    s= full_node_progs['node_size'], color='red',
                                                                    linewidth=0, alpha=0.8, ax=ax, zorder=3,
                                                                    label='Progressions')

        globals()['full_final_coll_' + str(period)] = pitch.scatter( full_node_final.loc_avg_x, full_node_final.loc_avg_y,
                                                                    marker= MarkerStyle('o', fillstyle='full'),
                                                                    s= full_node_final['node_size'], color='violet',
                                                                    linewidth=0, alpha=1, ax=ax, zorder=4,
                                                                    label='Progressions')

        globals()['top_losts_coll_' + str(period)] = pitch.scatter( full_node_losts.loc_avg_x, full_node_losts.loc_avg_y,
                                                                   marker= MarkerStyle('o', fillstyle='top'),
                                                                   s= full_node_losts['node_size'], color='grey',
                                                                   linewidth=0, alpha=0.8, ax=ax, zorder=1)

        globals()['top_progs_coll_' + str(period)] = pitch.scatter( full_node_progs.loc_avg_x, full_node_progs.loc_avg_y,
                                                                   marker= MarkerStyle('o', fillstyle='top'),
                                                                   s= full_node_progs['node_size'], color='red',
                                                                   linewidth=0, alpha=0.8, ax=ax, zorder=3)

        globals()['top_final_coll_' + str(period)] = pitch.scatter( full_node_final.loc_avg_x, full_node_final.loc_avg_y,
                                                                   marker= MarkerStyle('o', fillstyle='top'),
                                                                   s= full_node_final['node_size'], color='violet',
                                                                   linewidth=0, alpha=1, ax=ax, zorder=4)

        if self.vis != 'BUILDUP':
            
            globals()['bottom_recep_coll_' + str(period)] = pitch.scatter( node_recep.loc_avg_x, node_recep.loc_avg_y,
                                                                          marker= MarkerStyle('o', fillstyle='bottom'),
                                                                          s= node_recep['node_size'],
                                                                          color='orange', edgecolors='black',
                                                                          linewidth=0, alpha=0.8, ax=ax, zorder=3)

            globals()['bottom_recov_coll_' + str(period)] = pitch.scatter( node_recov.loc_avg_x, node_recov.loc_avg_y,
                                                                          marker= MarkerStyle('o', fillstyle='bottom'),
                                                                          s= node_recov['node_size'],
                                                                          color='yellow', edgecolors='black',
                                                                          linewidth=0, alpha=0.8, ax=ax, zorder=2)

            globals()['full_recep_coll_' + str(period)] = pitch.scatter( node_recep.loc_avg_x, node_recep.loc_avg_y,
                                                                        marker= MarkerStyle('o', fillstyle='full'),
                                                                        s= node_recep['node_size'], picker=True,
                                                                        color='orange', edgecolors='black',
                                                                        linewidth=0, alpha=0.8, ax=ax, zorder=3,
                                                                        label='Receptions')

            globals()['full_recov_coll_' + str(period)] = pitch.scatter( node_recov.loc_avg_x, node_recov.loc_avg_y,
                                                                        marker= MarkerStyle('o', fillstyle='full'),
                                                                        s= node_recov['node_size'], picker=True,
                                                                        color='yellow', edgecolors='black',
                                                                        linewidth=0, alpha=0.8, ax=ax, zorder=2,
                                                                        label='Receptions')

        """ Drawing names """
        for index, row in drawn_nodes.iterrows():
            zone = int(row.zone)
            name_color = 'black' if (self.vis == 'PLAYER' and row.player == player) else 'white'
            name = ppn_db.getNick(row.player, team)
            ha = 'center'
            if zone == 1:
                loc = (row.loc_avg_x - 1, row.loc_avg_y)
            elif [2, 7, 77].count(zone):
                loc = (row.loc_avg_x, row.loc_avg_y + 1)
                ha = 'left'
            elif [3, 11, 111].count(zone):
                loc = (row.loc_avg_x, row.loc_avg_y - 1)
                ha = 'right'
            elif [6, 9, 99, 10].count(zone):
                loc = (row.loc_avg_x + 1.5, row.loc_avg_y)
            self.pitch.annotate( name, xy=loc, color=name_color, va='center',
                                ha=ha, size=9, ax=ax, zorder=7, alpha=1)        

        """ PAINT EDGES """
        """ Edge width definition """
        filtered_edges=self.prog_edges[ (self.prog_edges.team == team) & (self.prog_edges.period == period) 
                                       & (self.prog_edges.edge_amount >= self.MIN_CONNEX_PASSES) ].copy()
        filtered_edges['width']= LINE_WIDTH * filtered_edges.edge_amount        
        filt_crosses= self.vis_crosses[ (self.vis_crosses.team == team) & (self.vis_crosses.period == period)
                                       & (self.vis_crosses.cross_amount >= self.MIN_CONNEX_PASSES)].copy()
        filt_crosses['width']= LINE_WIDTH * filt_crosses.cross_amount
        
        ppn_tools.paint_crosses( filt_crosses.orig_loc_x, filt_crosses.orig_loc_y, 
                                 filt_crosses.dest_loc_x, filt_crosses.dest_loc_y, 
                                 filt_crosses.width, pitch, ax, zorder= 3, color= 'violet')                                           

        # display( node_progs)
        # display( node_recep)
        """ Agafem el tamany dels nodes de progressió """
        filtered_edges= filtered_edges.merge( node_progs[['player', 'zone', 'period', 'node_size']], 
                                              how= 'left', suffixes=('', '_progs'),
                                              left_on= ['orig_player', 'origin_zone', 'period'], 
                                              right_on= ['player', 'zone', 'period'])
        filtered_edges= filtered_edges.rename( columns= {'node_size':'orig_prog_node_size'})

        filtered_edges= filtered_edges.merge( node_recep[['player', 'zone', 'period', 'node_size']], 
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
        
        if self.vis == 'GLOBAL':
            biedges= filtered_edges.merge( filtered_edges[['orig_player', 'origin_zone', 'dest_player', 'dest_zone']],
                                          how= 'inner', suffixes=('', '_bis'),
                                          left_on= ['orig_player', 'origin_zone', 'dest_player', 'dest_zone'], 
                                          right_on= ['dest_player', 'dest_zone', 'orig_player', 'origin_zone'])

            carry_biedges= biedges[ biedges.dest_player == biedges.orig_player ]
            pass_biedges= biedges[ biedges.dest_player != biedges.orig_player ]

            ppn_paint.paint_edge_arrows( pass_biedges.orig_loc_x, pass_biedges.orig_loc_y,
                                       pass_biedges.dest_loc_x, pass_biedges.dest_loc_y, 
                                       pass_biedges.dest_prog_node_size, pass_biedges.orig_prog_node_size,
                                       pass_biedges.width, ax, self.ppm, bidir= True, 
                                        color= 'white', zorder= 2, alpha= .8 )
            ppn_paint.paint_edge_arrows( carry_biedges.orig_loc_x, carry_biedges.orig_loc_y,
                                       carry_biedges.dest_loc_x, carry_biedges.dest_loc_y,
                                       carry_biedges.dest_prog_node_size, carry_biedges.orig_prog_node_size,
                                       carry_biedges.width, ax, self.ppm, bidir= True, 
                                        color= 'deepskyblue', zorder= 2, alpha= 1 )

            """ With indicator param you get in new '_merge' row if the row matxes or not with right df (both or left-only)"""
            uniedges= filtered_edges.merge( biedges[['orig_player', 'origin_zone', 'dest_player', 'dest_zone']],
                                           how= 'left', indicator= True, suffixes= ('', '_bis'),
                                           on= ['orig_player', 'origin_zone', 'dest_player', 'dest_zone'] )
            uniedges= uniedges[ uniedges._merge=='left_only'] # Biedges out

        else:
            uniedges= filtered_edges
            
        carry_uniedges= uniedges[ uniedges.dest_player == uniedges.orig_player ]
        pass_uniedges= uniedges[ uniedges.dest_player != uniedges.orig_player ]
        color_pass= 'white'

        if self.vis == 'PLAYER':
            prog_uniedges= pass_uniedges[ pass_uniedges.orig_player == player]
            pass_uniedges= pass_uniedges[ pass_uniedges.dest_player == player]
            color_pass= 'orange'

            ppn_paint.paint_edge_arrows( prog_uniedges.orig_loc_x, prog_uniedges.orig_loc_y,
                                       prog_uniedges.dest_loc_x, prog_uniedges.dest_loc_y,
                                       prog_uniedges.dest_prog_node_size, prog_uniedges.orig_prog_node_size,
                                       prog_uniedges.width, ax, self.ppm, bidir= False, 
                                        color= 'red', zorder= 2, alpha= .55 )

        ppn_paint.paint_edge_arrows( pass_uniedges.orig_loc_x, pass_uniedges.orig_loc_y,
                                   pass_uniedges.dest_loc_x, pass_uniedges.dest_loc_y,
                                   pass_uniedges.dest_prog_node_size, pass_uniedges.orig_prog_node_size,
                                   pass_uniedges.width, ax, self.ppm, bidir= False, 
                                    color= color_pass, zorder= 2, alpha= .55 )
        ppn_paint.paint_edge_arrows( carry_uniedges.orig_loc_x, carry_uniedges.orig_loc_y,
                                   carry_uniedges.dest_loc_x, carry_uniedges.dest_loc_y,
                                   carry_uniedges.dest_prog_node_size, carry_uniedges.orig_prog_node_size,
                                   carry_uniedges.width, ax, self.ppm, bidir= False, 
                                   color= 'deepskyblue', zorder= 2, alpha= .7 )
        
        self.draw_header( period, ax)
        
        ppn_pitch.draw_lateral_tips( ax)
        
        
    def draw_header( self, period, ax):
        """ PITCH HEADER """
        light_white = np.array(to_rgba('white'))
        light_white[3]= 0.5
        
        half= '1st Half' if period==1 else '2nd Half'
        home_score= len( self.match_events[ (self.match_events.shot_outcome == 'Goal') 
                                           & (self.match_events.team == self.team_home) 
                                           & (self.match_events.period == period) ] )
        away_score= len( self.match_events[ (self.match_events.shot_outcome == 'Goal') 
                                           & (self.match_events.team == self.team_away) 
                                           & (self.match_events.period == period) ] )
        ax.text(0, 122, half, ha='left', weight='bold',
                             color= light_white, fontsize=12)

        name_height= 121 if self.vis !='GLOBAL' else 122
        ax.text(40, name_height, self.team.upper(), ha='center', weight='bold',
                color= light_white, fontsize=12)
        ax.text(80, 123, 'period score:', ha='right', weight='bold',
                color= light_white, fontsize=10)    
        ax.text(80, 121, self.team_home[0:3].upper()+' '+str(home_score)+'-'
                +str(away_score)+' '+self.team_away[0:3].upper(), 
                ha='right', weight='bold', color= light_white, fontsize=10)            


    def match_header( self, ax):
        """ """
        wc_match= self.wc_matches[ self.wc_matches.match_id == self.match_id].iloc[0]
        ax.text(0.5, 0.7, 'Progressive Play Network', color='#22312b',
                          va='center', ha='center', fontsize=16)
        ax.text(0.73, 0.7, 'against Retrieved Block', color='red',
                          va='center', ha='left', fontsize=11, fontstyle='italic')
        ax.text(-0.03, 0, 'World Cup 2022: '+self.team_home +' '+ str(wc_match.home_score) +'-'
                          +str(wc_match.away_score)+' '+self.team_away +', '+ wc_match.competition_stage, 
                          color='#22312b', va='bottom', ha='left', fontsize=12)
        ax.text(1.03, 0.05, str(round( ppn_sb.get_tracked_perc( self.match_events), 2)) +' % of events with',
                          color='#22312b', va='bottom', ha='right', fontsize=10)
        ax.text(1.03, -0.15, 'tracking data available', color='#22312b',
                          va='bottom', ha='right', fontsize=10)

        
    def make_legend( self, fig, pitch):
        """ Nodes legend between axes valid for both viz """

        added_ax= fig.add_axes( (0.22, 0.472, 0.72, 0.038), frameon=True, fc='#c7d5cc')
        added_ax.set_axis_off()
        added_ax.set_ylim(0, 1)
        added_ax.set_xlim(0, 1)
        pitch.scatter( 0.5, 0.05, s= 850, color= 'white', edgecolors= 'black',
                      linewidth= 0.5, alpha= 0.7, ax= added_ax, zorder = 2)
        pitch.scatter( 0.75, 0.35, s= 300, color= 'grey', edgecolors= 'black',
                      linewidth= 0, alpha= 0.7, ax= added_ax, zorder = 3)
        pitch.scatter( 0.25, 0.35, s= 300, color= 'yellow', edgecolors= 'black',
                      linewidth= 0, alpha= 1, ax= added_ax, zorder = 3)
        pitch.scatter( 0.75, 0.55, s= 250, color= 'red', edgecolors= 'black',
                      linewidth= 0, alpha= 1, ax= added_ax, zorder = 4)
        pitch.scatter( 0.25, 0.65, s= 250, color= 'orange', edgecolors= 'black',
                      linewidth= 0, alpha= 1, ax= added_ax, zorder = 4)
        pitch.scatter( 0.75, 0.82, s= 200, color= 'fuchsia', edgecolors= 'black',
                      linewidth= 0, alpha= 0.7, ax= added_ax, zorder = 5)
        added_ax.text( 0.10, 0.5, 'Total \ninterventions', ha= 'left', va= 'center', fontsize=10)
        added_ax.text( 0.38, 0.75, 'Losts', ha= 'left', va= 'center', fontsize=10)
        added_ax.text( 0.38, 0.25, 'Recoveries', ha= 'left', va= 'center', fontsize=10)
        added_ax.text( 0.58, 0.75, 'Progressions', ha= 'left', va= 'center', fontsize=10)
        added_ax.text( 0.68, 0.25, 'Receptions', ha= 'left', va= 'center', fontsize=10)
        added_ax.text( 0.85, 0.75, 'Finalizations', ha= 'left', va= 'center', fontsize=10)

        if self.MIN_CONNEX_PASSES > 1:
            added_ax.text( 1.10, 0, 'Filtered edges \nwith minimum of \n'
                          +str(self.MIN_CONNEX_PASSES)+' plays', 
                           ha= 'left', va= 'center', fontsize=8)
    
        
    def make_footer( self, ax, fig):
        """ """
        from PIL import Image
        from urllib.request import urlopen
        SB_LOGO_URL = ('https://raw.githubusercontent.com/statsbomb/open-data/'
                       'master/img/SB%20-%20Icon%20Lockup%20-%20Colour%20positive.png')
        sb_logo = Image.open(urlopen(SB_LOGO_URL))

        ax_sb_logo = add_image(sb_logo, fig,
                               left= ax.get_position().x0,
                               bottom= ax.get_position().y0,
                               height= ax.get_position().height)

        ax.text(1, 0.5, '@diguemmiquel', va='center', ha='right', fontsize=12)        
        
        
    def save_file( self, file_ext, version):
        """ """
        if self.team==self.team_home:
            t_home= self.team.upper()
            t_away= self.team_away[0:3]
        else: 
            t_away= self.team.upper()
            t_home= self.team_home[0:3]

        if self.vis=='BUILDUP':
            png_name= "ProgPlayNetwork_v" +version+ "_Buildup_" +t_home +'-'+ t_away +file_ext
        elif self.vis=='PLAYER':
            png_name= "ProgPlayNetwork_v" +version +"_"+ ppn_db.getNick( self.player, self.team) 
            +'_'+ t_home +'-'+ t_away +file_ext
        else:
            png_name= "ProgPlayNetwork_v" +version +"_"+ t_home +'-'+ t_away +file_ext

        plt.savefig( "reports/"+png_name, dpi=300, bbox_inches='tight')
        
        
    def set_full_nodes( self, viz_type, value):
        if viz_type=='Progressions':
            full_losts_coll_1.set_visible(value)
            full_progs_coll_1.set_visible(value)
            full_final_coll_1.set_visible(value)
            full_losts_coll_2.set_visible(value)
            full_progs_coll_2.set_visible(value)
            full_final_coll_2.set_visible(value)
        elif viz_type=='Receptions':
            full_recep_coll_1.set_visible(value)
            full_recep_coll_2.set_visible(value)
            full_recov_coll_1.set_visible(value)
            full_recov_coll_2.set_visible(value)

    def set_half_nodes( self, value):
        top_losts_coll_1.set_visible(value)
        top_progs_coll_1.set_visible(value)
        top_final_coll_1.set_visible(value)
        top_losts_coll_2.set_visible(value)
        top_progs_coll_2.set_visible(value)
        top_final_coll_2.set_visible(value)    
        bottom_recep_coll_1.set_visible(value)
        bottom_recep_coll_2.set_visible(value)
        bottom_recov_coll_1.set_visible(value)
        bottom_recov_coll_2.set_visible(value)
        

    def rbfunc( self, label):
        """ """
        print( label)
        if label=='Progressions':
            self.set_full_nodes( 'Progressions', True)
            if self.rb_value== 'Receptions':
                self.set_full_nodes( 'Receptions', False)
            else:
                self.set_half_nodes(False)
        elif label=='Receptions':
            self.set_full_nodes( 'Receptions', True)
            if self.rb_value== 'Progressions':
                self.set_full_nodes( 'Progressions', False)
            else:
                self.set_half_nodes(False)
        else: # Both (half top - half bottom)
            self.set_half_nodes(True)
            if self.rb_value== 'Receptions':
                self.set_full_nodes( 'Receptions', False)
            if self.rb_value== 'Progressions':
                self.set_full_nodes( 'Progressions', False)

        self.rb_value= self.radio.value_selected
        plt.draw() # Necessary for Jupyter QT backend
        

    def draw_vis( self):
        """  """
        if self.vis=='BUILDUP':
            self.vis_finaliz= self.final_nodes[ self.final_nodes.zone == 1]
            self.prog_edges= self.edges[ (self.edges.progression==True) & (self.edges.origin_zone==1) ] # Edges sub-group
            self.vis_crosses= self.crosses[ self.crosses.origin_zone==1]
            buildup_zones= self.prog_edges.groupby( ['team', 'period', 'dest_zone']).agg( {'edge_amount':['sum']} )
            buildup_zones.columns= ['zone_sum']
            buildup_zones.reset_index(inplace=True)
    
        elif self.vis=='PLAYER':
            self.vis_finaliz= self.final_nodes[ self.final_nodes.player == self.player]
            self.vis_crosses= self.crosses[ (self.crosses.orig_player == self.player) 
                                           | (self.crosses.dest_player == self.player) ]
            self.prog_edges= self.edges[ ((self.edges.orig_player == self.player) 
                                          | (self.edges.dest_player == self.player))
                                        & (self.edges.progression==True) ]
        else:
            self.prog_edges= self.edges[ (self.edges.progression==True)]
            self.vis_crosses= self.crosses
            self.vis_finaliz= self.final_nodes
        
        self.orig_prog_nodes, self.dest_prog_nodes= ppn_draw.get_nodes_from_edges( self.prog_edges)
        self.orig_cross_nodes, self.dest_cross_nodes= ppn_draw.get_cross_nodes( self.vis_crosses)
        
        self.pitch = mpl.VerticalPitch( half=True, positional=False, pitch_type='statsbomb', pad_top= 6, pad_bottom= 10, 
                                   pad_left= 3, pad_right= 3, pitch_color='grass', line_color='#c7d5cc' ) 

        fig, axs = self.pitch.grid( ncols=1, nrows=2, axis=False, figheight= 16, space= 0.05,
                               grid_height= 0.88, title_height= 0.045, endnote_height= 0.03, 
                               title_space= 0.01, endnote_space= 0.005)
        fig.set_facecolor("#c7d5cc")
        self.ppm = fig.get_figwidth() * fig.dpi / 90  # Punts per metre (unitat de mesura del gràfic)

        # ppn_canvas= FigureCanvas( fig)
        # self.layout.addWidget( ppn_canvas)
        
        # ppn_pitch.draw_zonal_pitch( self.pitch, axs['pitch'] )
        ppn_pitch.draw_zonal_pitch( self.pitch, axs['pitch'][0])
        ppn_pitch.draw_zonal_pitch( self.pitch, axs['pitch'][1])
        
        if self.vis == 'BUILDUP':
            ppn_stats.draw_zone_stats( self.team, 1, axs['pitch'][0], buildup_zones, self.edges)
            ppn_stats.draw_zone_stats( self.team, 2, axs['pitch'][1], buildup_zones, self.edges)
        elif self.vis == 'GLOBAL':
            ppn_stats.draw_global_stats( self.team, 1, axs['pitch'][0], self.passes, self.edge_events)
            ppn_stats.draw_global_stats( self.team, 2, axs['pitch'][1], self.passes, self.edge_events)
        elif self.vis == 'PLAYER':
            self.draw_player_stats( 1, self.player, axs['pitch'][0] )
            self.draw_player_stats( 2, self.player, axs['pitch'][1] )

        self.draw_prog_play_network_3( self.team, 1, self.pitch, axs['pitch'][0], self.player )
        self.draw_prog_play_network_3( self.team, 2, self.pitch, axs['pitch'][1], self.player )
        # self.draw_prog_play_network_3( self.team, 1, self.pitch, axs['pitch'], self.player )
      
        """ Making Viz Interactive menu """
        rax = fig.add_axes([0.03, 0.441, 0.10, 0.10], frameon=False, aspect='equal', fc='#c7d5cc')
        self.radio = RadioButtons(rax, ('Progressions', 'Receptions', 'Both'))
        # adjust radius here. The default is 0.05
        for circle in self.radio.circles:
            circle.set_radius(0.07)
        self.radio.on_clicked( self.rbfunc)
        
        """ Interactive Initialization: """
        self.rb_value= self.radio.value_selected
        self.set_full_nodes( 'Receptions', False)
        self.set_half_nodes(False)        

        """ Plot Info"""
        ppn_pitch.draw_starting_lineup( axs['pitch'][0], self.team, self.lineups)
        self.match_header( axs['title'])
        self.make_footer( axs['endnote'], fig)
        self.make_legend( fig, self.pitch)
        
        # display(fig)
        plt.show()
        # self.save_file( ".png", self.version)