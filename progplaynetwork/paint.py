import math
import numpy as np
MIN_NODE_SIZE = 75

def paint_arrow(orig_x, orig_y, dest_x, dest_y,
                ax, bidir=False, width=2, alpha=1, zorder=1, color='red'):
    """ """
    ARROW_SCALE = 8
    #     max_arrow_width= 3
    #     max_head_width = 2.5 * max_arrow_width
    #     head_width = max_head_width # 0.075 # 2.5 * max_arrow_width
    head_width = 4 * width + (3 / width) if bidir else 2 * width + (3 / width)
    #     max_head_length = 2 * max_arrow_width
    #     head_length = max_head_length # 0.06 # 2 * max_arrow_width
    head_length = 3 * width + (3 / width) if bidir else 2 * width + (4 / width)
    arrow_width = width / ARROW_SCALE
    head_width = head_width / ARROW_SCALE
    head_length = head_length / ARROW_SCALE
    #     print( 'width=', width, 'head_width=', head_width, 'head_length=', head_length)
    color = color

    if bidir:
        """ Desplaçament perpendicular a la direccio per no solapar les dues arestes amb direccio """
        a = np.array([orig_y - dest_y, orig_x - dest_x])
        arrow_dist = math.dist([orig_x, orig_y], [dest_x, dest_y])
        #     print( arrow_dist )
        norm = a / arrow_dist
        #     coef= 15/arrow_dist
        #     print(norm)
        #     despl= width/3 +0.1
        despl = .15
        perp = np.array([-norm[1], +norm[0]]) * despl
        #     perp= perp
        #     print(perp)
        ax.arrow(
            orig_y - perp[0], orig_x - perp[1],
            (dest_y - perp[0]) - (orig_y - perp[0]),
            (dest_x - perp[1]) - (orig_x - perp[1]),
            fc=color, ec=color, alpha=alpha, zorder=zorder, shape='right', length_includes_head=True,
            width=arrow_width, head_width=head_width, head_length=head_length)
    else:
        ax.arrow(
            orig_y, orig_x, dest_y - orig_y, dest_x - orig_x,
            fc=color, ec=color, alpha=alpha, zorder=zorder, shape='full', length_includes_head=True,
            width=arrow_width, head_width=head_width, head_length=head_length)


#     ax.arrow(
#         dest_y +perp[0], dest_x +perp[1],
#         (orig_y +perp[0]) -(dest_y +perp[0]),
#         (orig_x +perp[1]) -(dest_x +perp[1]),
#         fc=fc, ec=fc, alpha=alpha, zorder=1, shape='right', length_includes_head=True,
#         width= width, head_width= head_width, head_length= head_length
#     )


def paint_edge_arrows(orig_x_array, orig_y_array, dest_x_array, dest_y_array,
                      dest_node_size_array, orig_node_size_array, lw_array,
                      ax, ppm, bidir=False, color='white', zorder=1, alpha=1):
    """ """
    for idx, x in enumerate(orig_x_array):
        width = lw_array.iloc[idx]
        dest_node_size = dest_node_size_array.iloc[idx]
        orig_node_size = orig_node_size_array.iloc[idx]
        #         node_size = NODE_SIZE * (node_amount**1.7) + MIN_NODE_SIZE
        #         display( width, dest_node_size)
        dest_node_rad = ((dest_node_size + MIN_NODE_SIZE) / math.pi) ** (1 / 1.9)
        orig_node_rad = ((orig_node_size + MIN_NODE_SIZE) / math.pi) ** (1 / 1.9)

        # ppm = fig.get_figwidth() * fig.dpi / 90  # Punts per metre (unitat de mesura del gràfic)
        dest_length2deduct = dest_node_rad / ppm
        orig_length2deduct = orig_node_rad / ppm

        orig_x = orig_x_array.iloc[idx]
        orig_y = orig_y_array.iloc[idx]
        dest_x = dest_x_array.iloc[idx]
        dest_y = dest_y_array.iloc[idx]

        arrow_dist = math.dist([orig_x, orig_y], [dest_x, dest_y])
        a_dest = np.array([dest_y - orig_y, dest_x - orig_x])
        """ to avoid nan values from non prog nodes: """
        #         display('dest_length2deduct=', dest_length2deduct)
        norm_dest = (a_dest / arrow_dist) * dest_length2deduct if not np.isnan(dest_length2deduct) else [0, 0]
        norm_orig = (a_dest / arrow_dist) * orig_length2deduct

        paint_arrow(orig_x + norm_orig[1], orig_y + norm_orig[0],
                    dest_x - norm_dest[1], dest_y - norm_dest[0],
                    ax, bidir, width, alpha, zorder, color)


def paint_ev_track(pass_frame, ev):
    """  """
    
    if (ev.type=='Foul Won' or ev.type=='Dispossessed' or
        (ev.type == 'Dribble' and ev.dribble_outcome=='Incomplete')):
        print('Inverse tracking!')
        team_pos, team_x, team_y, team_gk = get_inverse_tracking( pass_frame, True )
        opp_pos, opp_x, opp_y, opp_gk = get_inverse_tracking( pass_frame, False )
    else:
        team_pos, team_x, team_y, team_gk = get_tracking( pass_frame, True )
        opp_pos, opp_x, opp_y, opp_gk = get_tracking( pass_frame, False )
    # display(team_pos)

    pitch = Pitch(axis=True, label=True, tick=True )
    fig, ax = pitch.draw(figsize=(8, 6)) # figsize=(8, 6)
    # hull = pitch.convexhull(opp_x, opp_y)
    if len(opp_x)>2:
        hull = ConvexHull(opp_pos)
        # display(hull)
        hull_vertx= hull.points[hull.vertices]
        # display([hull_vertx])
        poly = pitch.polygon([hull_vertx], ax=ax, edgecolor='cornflowerblue', facecolor='cornflowerblue', alpha=0.5)
        left_pl1, left_pl2, right_pl1, right_pl2 = paint_exteriors(hull_vertx, ax, color='blue')
        # display("First left def: ", left_pl1[0])
        # display("Second left def: ", left_pl2[0])
        mean_posX= np.mean(opp_x)
        mean_posY= np.mean(opp_y)
        last_def_Xpos= np.max(opp_x)
        ax.plot([mean_posX, mean_posX], [0, 80], lw=1, color='blue')
        pitch.annotate( round(mean_posX, 2), xy= [mean_posX, +82], 
                    c='blue', va='center', ha='center', size=7, ax=ax, zorder=7)
        paint_pos( ax, pitch, hull, team_x, team_y, opp_pos, 
                  left_pl1, left_pl2, right_pl1, right_pl2, mean_posY, mean_posX, ev.opp_def_type, last_def_Xpos)
    
    end_location= None
    if ev.type=='Pass':
        end_location= ev.pass_end_location
    elif ev.type=='Carry':
        end_location= ev.carry_end_location        
    elif (ev.type=='Ball Receipt*' or ev.type=='Shot' or ev.type=='Foul Won' 
          or ev.type=='Ball Recovery' or ev.type=='Interception' or ev.type=='Dispossessed' 
          or ev.type=='Miscontrol' or ev.type=='Duel' or ev.type=='Dribble'):
        nodes = pitch.scatter( ev.location[0], ev.location[1],
                      s= 200, color= 'white', edgecolors= 'black', 
                      linewidth= 1, alpha= .4, ax= ax, zorder = 2)

    """ Painting arrow of ball movement (pass or carry) """
    if end_location: 
        width=0.3
        # ax.plot([ev.location[0], end_location[0]], [ev.location[1], end_location[1]], lw=2, color='red')
        ax.arrow( ev.location[0], ev.location[1], 
                 end_location[0]-ev.location[0], 
                 end_location[1]-ev.location[1],
                 width= width, head_width= 4*width, head_length= 6*width, color='red')

    
    pitch.annotate( str(ev.type) +" - "+ getNick( ev.player, TEAM) +" zone_"+ str(ev.origin_zone)+
                   " to "+ str(getNick( ev.pass_recipient, TEAM)) +" zone_"+ str(ev.dest_zone), 
                    xy= [20, -2], c='black', va='center', ha='left', size=10, ax=ax, zorder=7 )

    visible_area = np.array(pass_frame.iloc[0].visible_area).reshape(-1, 2)
    pitch.polygon([visible_area], color='#ffff9e', alpha=0.4, zorder=1, ax=ax)

    """ Painting player nodes """
    scatter_opp = pitch.scatter(opp_x, opp_y, ax=ax, edgecolor='black', facecolor='cornflowerblue', zorder=3, alpha=1)
    scatter_team = pitch.scatter(team_x, team_y, ax=ax, edgecolor='black', facecolor='red')
    if team_gk:
        scatter_gk1 = pitch.scatter(team_gk[0], team_gk[1], ax=ax, edgecolor='black', facecolor='black')
    if opp_gk:
        scatter_gk2 = pitch.scatter(opp_gk[0], opp_gk[1], ax=ax, edgecolor='black', facecolor='black')

        
def paint_pos( ax, pitch, hull, team_x, team_y, opp_pos, 
              left_pl1, left_pl2, right_pl1, right_pl2, mean_posY, mean_posX, def_type, last_def_Xpos):
    """ left_pl1 & right_pl1 are the firsts exterior defenders (nearer the opp goal).
        whereas left_pl2 & right_pl2 are the back exteriors (nearer their goal).
    """

    for i in range(len(team_x)):
        pl_pos= np.array([team_x[i], team_y[i]])
        
        real_zone= get_player_zone( pl_pos, hull, opp_pos, mean_posY, mean_posX, def_type, last_def_Xpos)
        
        pitch.annotate( real_zone, xy= [team_x[i], team_y[i]-2],  # +"_real="+str(real_zone)+is_left
                        c='black', va='center', ha='center', size=7, ax=ax, zorder=7)
        
        if ( (real_zone==9 and not is_into_box(pl_pos) and pl_pos[0] > 60)
            or ( (real_zone==2) and (pl_pos[0] > left_pl2[0]) )
            or ( (real_zone==3) and (pl_pos[0] > right_pl2[0]) )
            or (real_zone==7)
            or (real_zone==11) ): 
            paint_final_zone( ax, pitch, pl_pos, opp_pos, real_zone)
        

def paint_final_zone( ax, pitch, pl, opp_pos, zone ):
    """  """
    if zone>6:
        # Pintamos las opciones de ser zona 9
        if pl[1]>18 and pl[1]<62:
            ax.plot( [pl[0], 120], [pl[1], 40], lw=1, ls='--', color='grey')
        # ax.plot( [frontal_vtx_right[0], frontal_vtx_left[0]],
        #          [frontal_vtx_left[1], frontal_vtx_right[1]], lw=1, color='black' )
        """ point from distance to define the 9 position """
        inters_p= get_small_box_inters( pl )
        """ Once we have the nearest intersection point with box, calculate the nearest player """
        opp_dist, closest_opp= get_closest( inters_p, opp_pos )
        inters_scatter = pitch.scatter(inters_p[0], inters_p[1], ax=ax, s=10, edgecolor='black', facecolor='black')
        opp_dist= paint_distance( closest_opp, inters_p, ax, pitch)
        pl_dist= paint_distance( pl, inters_p, ax, pitch)
    
    """ Pintamos las opciones de ser zona extremo """
    if zone==11 or zone==3:
        opp_dist, closest_opp= get_closest( left_corner, opp_pos )
        pl_dist= paint_distance( pl, left_corner, ax, pitch)
        opp_dist= paint_distance( closest_opp, left_corner, ax, pitch)
        # pl_dist= math.dist( pl_pos, left_corner)
    elif zone==7 or zone==2:
        opp_dist, closest_opp= get_closest( right_corner, opp_pos )
        pl_dist= paint_distance( pl, right_corner, ax, pitch)
        opp_dist= paint_distance( closest_opp, right_corner, ax, pitch)
        # pl_dist= math.distst( pl_pos, right_corner)

    
def paint_distance(p1, p2, ax, pitch):
    """ Paint line and its distance label between both points """
    
    ax.plot( [p1[0], p2[0]], [p1[1], p2[1]], lw=1, ls='--', color='grey')
    dist= math.dist( p1, p2)
    pitch.annotate( round(dist, 2), xy= [(p1[0]+p2[0])/2, (p1[1]+p2[1])/2-2], 
                    c='black', va='center', ha='center', size=7, ax=ax, zorder=7)
    return dist
    

def paint_exteriors(hull_vertx, ax, color):
    """ Let's set and paint the exterior borders """
    
    left_pl1, left_pl2, right_pl1, right_pl2 = get_exteriors(hull_vertx)
        # print("max right=", right_pl1, "second max=", right_pl2)
        # print("max left=", left_pl1, "second max=", left_pl2)    
    ax.plot([right_pl1[0], right_pl2[0]], [right_pl1[1], right_pl2[1]], lw=2, color=color)
    ax.plot([left_pl1[0], left_pl2[0]], [left_pl1[1], left_pl2[1]], lw=2, color=color)
    ax.plot( [right_pl1[0], right_pl1[0]], [right_pl1[1], 0], lw=1, ls='--', color='grey')
    ax.plot( [right_pl2[0], right_pl2[0]], [right_pl2[1], 0], lw=1, ls='--', color='grey')
    ax.plot( [left_pl1[0], left_pl1[0]], [left_pl1[1], 80], lw=1, ls='--', color='grey')
    ax.plot( [left_pl2[0], left_pl2[0]], [left_pl2[1], 80], lw=1, ls='--', color='grey')    
        
    return left_pl1, left_pl2, right_pl1, right_pl2


            
def paint_event(idx):
    """ """
    ev= match_events.iloc[idx]
    ev_frame= match_frames[match_frames.id==ev.id]
    if len(ev_frame):
        paint_ev_track(ev_frame, ev)
    
    
def paint_play( idx):
    """ """
    sel= get_event( idx)
    display(sel)
    paint_event( idx)
    # Painting related events:
    ev= match_events.iloc[idx]
    if not isinstance(ev.related_events, list):
        return
    for rel_ev_id in ev.related_events:
        rel_sel= match_events[ match_events.id == rel_ev_id] [column_basics]
        display(rel_sel)
        for ridx, rev in rel_sel.iterrows(): 
            if not (ev.type=='Carry' and rev.type=='Ball Receipt*'):
                paint_event(ridx)

            
def paint_possession(poss_num, first=0, last=5, pass_num=None, with_reception=False, just_df= False):
    """  """
    poss_ev= passes.loc[ passes.possession==poss_num ].sort_values('timestamp')
    if just_df: 
        display(poss_ev)
        return
    
    i=0
    for idx, ev in poss_ev.iterrows():
        if (i < first):
            i+=1
            continue
        if (i > last): break
        i+=1
    # idx= events.loc[(events.possession==poss_num) & 
    #                 (events.team==events.possession_team)].sort_values('timestamp').index[pass_num]
    # event_df= events[events.index==idx]
    # # idx= passes.loc[passes.possession==poss_num].index[pass_num]
    # # event_df= passes[passes.index==idx]
    # display(event_df)
    # ev= event_df.iloc[0]
#         display(poss_ev[poss_ev.index==idx])
#         ev_frame= match_frames[match_frames.id==ev.id]
        # display(ev_frame)
        paint_play(idx)
        if ev.pass_outcome == "Incomplete": 
            display( "Incomplete pass" )

        if with_reception:
            paint_track_reception(ev)

            
def paint_track_reception(pase):
    """ Looking for tracking when reception """
    if len(pase.related_events): display("Pass related events:")
    for ev in pase.related_events:
        display(events[events.id==ev])
        rel_ev = events[events.id==ev].iloc[0]
        if rel_ev.type== 'Ball Receipt*':
            receiv_frame= match_frames[match_frames.id==rel_ev.id]
            # display(receiv_frame)
            if len(receiv_frame):
                # pass
                ax.plot( [pase.location[0], pase.pass_end_location[0]], 
                        [pase.location[1], pase.pass_end_location[1]], lw=2, color='red')
                
                _team_pos, _team_x, _team_y, _team_gk = get_tracking( receiv_frame, True )
                _opp_pos, _opp_x, _opp_y, _opp_gk = get_tracking( receiv_frame, False )
                
                _scatter = pitch.scatter( _opp_x, _opp_y, ax=ax, 
                                         edgecolor='black', facecolor='cornflowerblue', linewidth= 0.5, alpha= 0.5)
                _scatter2 = pitch.scatter( _team_x, _team_y, ax=ax, 
                                          edgecolor='black', facecolor='red', linewidth= 0.5, alpha= 0.5)
                """ Paint EPS """
                hull = ConvexHull(_opp_pos)
                hull_vertx= hull.points[hull.vertices]
                poly = pitch.polygon( [hull_vertx], ax=ax, edgecolor='cornflowerblue', 
                                     facecolor='yellow', alpha=0.2, zorder=5)
                left_pl1, left_pl2, right_pl1, right_pl2 = paint_exteriors(hull_vertx, ax, color='cornflowerblue')
                # display("First left def: ", left_pl1[0])
                # display("Second left def: ", left_pl2[0])
                mean_posX= np.mean(_opp_x)
                last_def_Xpos= np.max(opp_x)
                paint_pos( ax, pitch, hull, _team_x, _team_y, _opp_pos, 
                          left_pl1, left_pl2, right_pl1, right_pl2, mean_posY, mean_posX, ev.opp_def_type, last_def_Xpos)
                
            else: display("Not tracking on ball reception")
                