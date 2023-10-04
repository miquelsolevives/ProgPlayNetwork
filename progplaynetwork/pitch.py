import mplsoccer
import numpy as np # numerical python package
from matplotlib.lines import Line2D
from matplotlib.colors import to_rgba
from scipy.spatial import ConvexHull
import math
from progplaynetwork import statsbomb as ppn_sb
from progplaynetwork import db_players as ppn_db

""" GLOBAL VARS """

frontal_box_line_x= 102
small_box_line_x= 114
right_box_line_y= 18
left_box_line_y= 62
small_box_left_vtx= [small_box_line_x, 50]
small_box_right_vtx= [small_box_line_x, 30]
frontal_vtx_right= [frontal_box_line_x, right_box_line_y]
frontal_vtx_left= [frontal_box_line_x, left_box_line_y]
frontal_box_edge= [frontal_vtx_right, frontal_vtx_left]
small_box_edge= [small_box_left_vtx, small_box_right_vtx]
left_box_edge= [frontal_vtx_left, [120, left_box_line_y]]
right_box_edge= [frontal_vtx_right, [120, right_box_line_y]]
left_corner= [120, 0]
right_corner= [120, 80]

BROKEN_HEIGHT= 109
EPS_TOP_HEIGHT= 95
EPS_BOTTOM_HEIGHT= 75
TOP_TEN_HEIGHT= frontal_box_line_x+1
EXT_F_HEIGHT= (TOP_TEN_HEIGHT + EPS_TOP_HEIGHT) /2
LEFT_EXT_WIDTH= 17
RIGHT_EXT_WIDTH= 63

def draw_lateral_tips( ax):
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


def draw_starting_lineup( ax, team, lineups):
    """ Starting LineUp """
    form, lineup = ppn_sb.get_match_lineup( team, lineups)
    players = list(lineup.keys())
    pl_pos = 0
    pl_nick = ppn_db.getNick( players[pl_pos], team)

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
            pl_nick = ppn_db.getNick( players[pl_pos], team)
            line -= 1.5
            ax.text(83.5, line, pl_nick,
                    color='black', ha='left', fontsize=9)

    ax.text(83.5, EPS_TOP_HEIGHT - 2, formation, color='black', ha='left', fontsize=9)


def draw_zonal_pitch( pitch, ax):
    """ """

    EPS_shape = np.array([ [120, LEFT_EXT_WIDTH], [120, RIGHT_EXT_WIDTH],
                        [BROKEN_HEIGHT, RIGHT_EXT_WIDTH], [BROKEN_HEIGHT, LEFT_EXT_WIDTH] ])
    # shape2 = np.array([[70, 70], [60, 50], [40, 40]])
    pitch.polygon( [EPS_shape], color='red', alpha=0.15, ax=ax)
    
    BOX_shape = np.array([ [TOP_TEN_HEIGHT, LEFT_EXT_WIDTH], [TOP_TEN_HEIGHT, RIGHT_EXT_WIDTH],
                        [EPS_BOTTOM_HEIGHT, RIGHT_EXT_WIDTH], [EPS_BOTTOM_HEIGHT, LEFT_EXT_WIDTH] ])
    pitch.polygon( [BOX_shape], color='red', alpha=0.15, ax=ax)

    line_props= {'linewidth': 1, 'color': 'red', 'zorder':4}
    lineF = Line2D( [0,80], [BROKEN_HEIGHT, BROKEN_HEIGHT], **line_props)
    lineP3 = Line2D( [LEFT_EXT_WIDTH, RIGHT_EXT_WIDTH], [TOP_TEN_HEIGHT, TOP_TEN_HEIGHT], **line_props)
    lineP2 = Line2D( [LEFT_EXT_WIDTH, RIGHT_EXT_WIDTH], [EPS_TOP_HEIGHT, EPS_TOP_HEIGHT], **line_props)
    lineP1 = Line2D( [0,80], [EPS_BOTTOM_HEIGHT, EPS_BOTTOM_HEIGHT], **line_props)
    linePF_left_ext = Line2D( [0,LEFT_EXT_WIDTH], [EXT_F_HEIGHT, EXT_F_HEIGHT], **line_props)
    linePF_right_extF = Line2D( [RIGHT_EXT_WIDTH,80], [EXT_F_HEIGHT, EXT_F_HEIGHT], **line_props)
    line_extL = Line2D( [LEFT_EXT_WIDTH,LEFT_EXT_WIDTH], [EPS_BOTTOM_HEIGHT, 120], **line_props)
    line_extR = Line2D( [RIGHT_EXT_WIDTH,RIGHT_EXT_WIDTH], [EPS_BOTTOM_HEIGHT, 120], **line_props)
    ax.add_artist(lineF)
    ax.add_artist(lineP3)
    ax.add_artist(lineP2)
    ax.add_artist(lineP1)
    ax.add_artist(linePF_left_ext)
    ax.add_artist(linePF_right_extF)
    ax.add_artist(line_extL)
    ax.add_artist(line_extR)
#     ax.add_artist(frontal_box_edge)
#     ax.add_artist(small_box_edge)
#     red_trans = np.array(to_rgba('red'))
#     red_trans[3]= 0.7
    white_trans = np.array(to_rgba('white'))
    white_trans[3]= 0.4
    ax.text( 1, 118, '111', ha='left', weight='bold',
                     color= white_trans , fontsize=10)
    ax.text( 79, 118, '77', ha='right', weight='bold',
                     color= white_trans , fontsize=10)  
#     red_trans[3]= 0.7
    ax.text( 40, 118, '99', ha='center', weight='bold',
                     color= white_trans , fontsize=10)  
    ax.text( 1, 107, '11', ha='left', weight='bold',
                     color= white_trans , fontsize=10)
    ax.text( 79, 107, '7', ha='right', weight='bold',
                     color= white_trans , fontsize=10)  
    ax.text( 40, 106, '9', ha='center', weight='bold',
                     color= white_trans , fontsize=10)
    ax.text( 40, 96, '10', ha='center', weight='bold',
                     color= white_trans , fontsize=10)
    ax.text( 40, 90, '6', ha='center', weight='bold',
                     color= white_trans , fontsize=10)    
    ax.text( 14, 91, '3', ha='left', weight='bold',
                     color= white_trans , fontsize=10)
    ax.text( 66, 91, '2', ha='right', weight='bold',
                     color= white_trans , fontsize=10)  
    ax.text( 1, 61, 'zone 1', ha='left', weight='bold',
                     color= white_trans , fontsize=10)
    ax.text( 79, 61, 'zone 1', ha='right', weight='bold',
                     color= white_trans , fontsize=10)  
    
    return pitch


def draw_zonal_pitch_11( pitch, ax):
    """ Two new zones in forward exterior wings when broken block """
    global LEFT_EXT_WIDTH
    LEFT_EXT_WIDTH = 14
    global RIGHT_EXT_WIDTH
    RIGHT_EXT_WIDTH = 66
    global TOP_TEN_HEIGHT
    TOP_TEN_HEIGHT = frontal_box_line_x + 2  # 104
    global EPS_TOP_HEIGHT
    EPS_TOP_HEIGHT = 91
    global EPS_BOTTOM_HEIGHT
    EPS_BOTTOM_HEIGHT = 73
    global TOP_FIVE_HEIGHT
    TOP_FIVE_HEIGHT = 96
    global EXT_F_HEIGHT
    EXT_F_HEIGHT = (TOP_TEN_HEIGHT + TOP_FIVE_HEIGHT) / 2
    EXT_BOT_HEIGHT = EPS_BOTTOM_HEIGHT + 5
    LAT_L_WIDTH_99 = 27
    LAT_R_WIDTH_99 = 53

    BOX_shape = np.array([[120, LAT_L_WIDTH_99], [120, LAT_R_WIDTH_99],
                          [BROKEN_HEIGHT, left_box_line_y], [BROKEN_HEIGHT, right_box_line_y]])
    LEFT_shape = np.array([[120, LAT_L_WIDTH_99 - 6], [120, right_box_line_y - 6],
                           [BROKEN_HEIGHT, right_box_line_y - 6]])
    RIGHT_shape = np.array([[120, LAT_R_WIDTH_99 + 6], [120, left_box_line_y + 6],
                            [BROKEN_HEIGHT, left_box_line_y + 6]])
    TEN_shape = np.array([[TOP_TEN_HEIGHT, LEFT_EXT_WIDTH], [TOP_TEN_HEIGHT, RIGHT_EXT_WIDTH],
                          [TOP_FIVE_HEIGHT, RIGHT_EXT_WIDTH], [TOP_FIVE_HEIGHT, LEFT_EXT_WIDTH]])
    EPS_shape = np.array([[EPS_TOP_HEIGHT, LEFT_EXT_WIDTH], [EPS_TOP_HEIGHT, RIGHT_EXT_WIDTH],
                          [EXT_BOT_HEIGHT, RIGHT_EXT_WIDTH], [EPS_BOTTOM_HEIGHT, left_box_line_y],
                          [EPS_BOTTOM_HEIGHT, right_box_line_y], [EXT_BOT_HEIGHT, LEFT_EXT_WIDTH]])
    pitch.polygon([BOX_shape], color='red', alpha=0.15, ax=ax)
    pitch.polygon([TEN_shape], color='red', alpha=0.15, ax=ax)
    pitch.polygon([EPS_shape], color='red', alpha=0.15, ax=ax)
    pitch.polygon([LEFT_shape], color='red', alpha=0.15, ax=ax)
    pitch.polygon([RIGHT_shape], color='red', alpha=0.15, ax=ax)

    line_props = {'linewidth': 1, 'color': 'red', 'zorder': 4}
    lineF = Line2D([right_box_line_y, left_box_line_y],
                   [BROKEN_HEIGHT, BROKEN_HEIGHT], **line_props)
    lineP4 = Line2D([LEFT_EXT_WIDTH, RIGHT_EXT_WIDTH],
                    [TOP_TEN_HEIGHT, TOP_TEN_HEIGHT], **line_props)
    lineP3 = Line2D([LEFT_EXT_WIDTH, RIGHT_EXT_WIDTH],
                    [TOP_FIVE_HEIGHT, TOP_FIVE_HEIGHT], **line_props)
    lineP2 = Line2D([LEFT_EXT_WIDTH, RIGHT_EXT_WIDTH],
                    [EPS_TOP_HEIGHT, EPS_TOP_HEIGHT], **line_props)
    lineP1 = Line2D([right_box_line_y, left_box_line_y],
                    [EPS_BOTTOM_HEIGHT, EPS_BOTTOM_HEIGHT], **line_props)
    linePF_left_ext = Line2D([0, LEFT_EXT_WIDTH],
                             [EXT_F_HEIGHT, EXT_F_HEIGHT], **line_props)
    linePF_right_ext = Line2D([RIGHT_EXT_WIDTH, 80],
                              [EXT_F_HEIGHT, EXT_F_HEIGHT], **line_props)
    linePB_left_ext = Line2D([0, LEFT_EXT_WIDTH],
                             [EXT_BOT_HEIGHT, EXT_BOT_HEIGHT], **line_props)
    linePB_right_ext = Line2D([RIGHT_EXT_WIDTH, 80],
                              [EXT_BOT_HEIGHT, EXT_BOT_HEIGHT], **line_props)
    linePB_left_ext2 = Line2D([0, LEFT_EXT_WIDTH - 2],
                              [BROKEN_HEIGHT, BROKEN_HEIGHT], **line_props)
    linePB_right_ext2 = Line2D([RIGHT_EXT_WIDTH + 2, 80],
                               [BROKEN_HEIGHT, BROKEN_HEIGHT], **line_props)
    line_extL = Line2D([LEFT_EXT_WIDTH, LEFT_EXT_WIDTH],
                       [EXT_BOT_HEIGHT, TOP_TEN_HEIGHT], **line_props)
    line_extR = Line2D([RIGHT_EXT_WIDTH, RIGHT_EXT_WIDTH],
                       [EXT_BOT_HEIGHT, TOP_TEN_HEIGHT], **line_props)
    line_extL2 = Line2D([right_box_line_y - 6, LEFT_EXT_WIDTH],
                        [BROKEN_HEIGHT, TOP_TEN_HEIGHT], **line_props)
    line_extR2 = Line2D([left_box_line_y + 6, RIGHT_EXT_WIDTH],
                        [BROKEN_HEIGHT, TOP_TEN_HEIGHT], **line_props)
    line_extL3 = Line2D([right_box_line_y - 6, right_box_line_y - 6],
                        [BROKEN_HEIGHT, 120], **line_props)
    line_extR3 = Line2D([left_box_line_y + 6, left_box_line_y + 6],
                        [BROKEN_HEIGHT, 120], **line_props)
    line_cornerL = Line2D([right_box_line_y, LEFT_EXT_WIDTH],
                          [EPS_BOTTOM_HEIGHT, EXT_BOT_HEIGHT], **line_props)
    line_cornerR = Line2D([left_box_line_y, RIGHT_EXT_WIDTH],
                          [EPS_BOTTOM_HEIGHT, EXT_BOT_HEIGHT], **line_props)
    line_diag_R = Line2D([RIGHT_EXT_WIDTH, LAT_R_WIDTH_99],
                         [TOP_TEN_HEIGHT, 120], **line_props)
    line_diag_R2 = Line2D([left_box_line_y + 6, LAT_R_WIDTH_99 + 6],
                          [BROKEN_HEIGHT, 120], **line_props)
    line_diag_L = Line2D([LEFT_EXT_WIDTH, LAT_L_WIDTH_99],
                         [TOP_TEN_HEIGHT, 120], **line_props)
    line_diag_L2 = Line2D([right_box_line_y - 6, LAT_L_WIDTH_99 - 6],
                          [BROKEN_HEIGHT, 120], **line_props)
    # line_props2= {'linewidth': 1, 'color': 'blue', 'zorder':4}
    # linePF_left_ext2 = Line2D( [0, LEFT_EXT_WIDTH],
    #                            [BROKEN_HEIGHT+2.5, BROKEN_HEIGHT+2.5], **line_props2)
    ax.add_artist(lineF)
    ax.add_artist(lineP4)
    ax.add_artist(lineP3)
    ax.add_artist(lineP2)
    ax.add_artist(lineP1)
    ax.add_artist(linePF_left_ext)
    ax.add_artist(linePF_right_ext)
    ax.add_artist(linePB_left_ext)
    ax.add_artist(linePB_right_ext)
    ax.add_artist(linePB_left_ext2)
    ax.add_artist(linePB_right_ext2)
    ax.add_artist(line_extL)
    ax.add_artist(line_extR)
    ax.add_artist(line_extL2)
    ax.add_artist(line_extR2)
    ax.add_artist(line_extL3)
    ax.add_artist(line_extR3)
    ax.add_artist(line_cornerL)
    ax.add_artist(line_cornerR)
    ax.add_artist(line_diag_L)
    ax.add_artist(line_diag_R)
    ax.add_artist(line_diag_L2)
    ax.add_artist(line_diag_R2)
    # ax.add_artist( Line2D( [LEFT_EXT_WIDTH,22], [BROKEN_HEIGHT+1.5, 126.5], **line_props) )
    # ax.add_artist(linePF_left_ext2)
    #     red_trans = np.array(to_rgba('red'))
    #     red_trans[3]= 0.7
    white_trans = np.array(to_rgba('white'))
    white_trans[3] = 0.4
    ax.text(1, 118, '111', ha='left', weight='bold',
            color=white_trans, fontsize=10)
    ax.text(right_box_line_y - 1, BROKEN_HEIGHT, '119', ha='right', va='center',
            weight='bold', color=white_trans, fontsize=10)
    ax.text(left_box_line_y + 1, BROKEN_HEIGHT, '79', ha='left', va='center',
            weight='bold', color=white_trans, fontsize=10)
    ax.text(79, 118, '77', ha='right', weight='bold',
            color=white_trans, fontsize=10)
    #     red_trans[3]= 0.7
    ax.text(40, 118, '99', ha='center', weight='bold',
            color=white_trans, fontsize=10)
    ax.text(1, 107, '11', ha='left', weight='bold',
            color=white_trans, fontsize=10)
    ax.text(79, 107, '7', ha='right', weight='bold',
            color=white_trans, fontsize=10)
    ax.text(40, 106, '9', ha='center', weight='bold',
            color=white_trans, fontsize=10)
    ax.text(40, 99, '10', ha='center', weight='bold',
            color=white_trans, fontsize=10)
    ax.text(40, 85, '6', ha='center', weight='bold',
            color=white_trans, fontsize=10)
    ax.text(40, 93, '5', ha='center', weight='bold',
            color=white_trans, fontsize=10)
    ax.text(11, 91, '3', ha='left', weight='bold',
            color=white_trans, fontsize=10)
    ax.text(69, 91, '2', ha='right', weight='bold',
            color=white_trans, fontsize=10)
    ax.text(1, 61, 'zone 1', ha='left', weight='bold',
            color=white_trans, fontsize=10)
    ax.text(79, 61, 'zone 1', ha='right', weight='bold',
            color=white_trans, fontsize=10)

    return pitch


def point_in_hull(point, hull, tolerance=1e-12):
    return all(
        (np.dot(eq[:-1], point) + eq[-1] <= tolerance)
        for eq in hull.equations)


def isLeft(a, b, c):
    return ((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])) > 0


def get_player_zone( pl_pos, hull, opp_pos, mean_posY, mean_posX, def_type, last_def_Xpos):
    """ """

    hull_vertx = hull.points[hull.vertices]
    left_pl1, left_pl2, right_pl1, right_pl2 = get_exteriors(hull_vertx)

    zone = 1  # Bottom by default
    into_box = is_into_box(pl_pos)

    if into_box:
        if pl_pos[0] > last_def_Xpos and is_into_def_zone(pl_pos):
            zone = 9

        elif (pl_pos[0] > BROKEN_HEIGHT) or def_type == 'Broken block':
            zone = 99
        else:
            zone = 10

    elif is_final_zone(pl_pos, opp_pos):
        zone = 9  # Estalviem alguns càlculs si han entrat abans a 9 o 99

    elif point_in_hull(pl_pos, hull):  # and pl_pos[1] < EPS_TOP_HEIGHT:
        if (((pl_pos[0] > mean_posX) and (mean_posX > 60))
                or ((pl_pos[0] > mean_posX - 3) and (mean_posX > 80))
                or (pl_pos[0] > EPS_TOP_HEIGHT)):
            zone = 10
        else:
            zone = 6  # EPS

    elif (pl_pos[1] < right_box_line_y) and (pl_pos[0] >= EXT_F_HEIGHT):  # left wing
        zone = 11
        if (def_type == 'Broken block') or (pl_pos[0] > BROKEN_HEIGHT):
            zone = 111
    # Nearer to corner
    elif (pl_pos[0] > 60) & (pl_pos[1] < right_box_line_y) & is_nearer_to_corner(pl_pos, opp_pos, "left"):
        zone = 11

    elif (pl_pos[1] > left_box_line_y) and (pl_pos[0] >= EXT_F_HEIGHT):  # right wing
        zone = 7
        # Finalization zone if def block is broken
        if (def_type == 'Broken block') or (pl_pos[0] > BROKEN_HEIGHT):
            zone = 77
            # Nearer to corner
    elif (pl_pos[0] > 60) & (pl_pos[1] > left_box_line_y) & is_nearer_to_corner(pl_pos, opp_pos, "right"):
        zone = 7

    elif (pl_pos[0] > EPS_TOP_HEIGHT):
        if (pl_pos[1] < right_box_line_y):
            zone = 3
        elif (pl_pos[1] > left_box_line_y):
            zone = 2
        else:  # if (pl_pos[1] > right_box_line_y) and (pl_pos[1] < left_box_line_y) ):
            zone = 10

    # left exterior progression
    elif (not isLeft(right_pl1, right_pl2, pl_pos) and
          (pl_pos[0] > right_pl1[0])):
        zone = 3

        # right exterior progression
    elif (isLeft(left_pl1, left_pl2, pl_pos) and
          (pl_pos[0] > left_pl1[0])):
        zone = 2

        # Back defense outside EPS
    elif ((pl_pos[0] > mean_posX) and (pl_pos[0] > right_pl2[0]) and (pl_pos[0] > left_pl2[0])):
        # print('Posició oblidada!')
        zone = 10

    return zone


def is_nearer_to_corner( pl_pos, opp_pos, side):
    """ """
    if side == 'left':
        opp_dist, closest_opp = get_closest(left_corner, opp_pos)
        pl_dist = math.dist(pl_pos, left_corner)
    elif side == 'right':
        opp_dist, closest_opp = get_closest(right_corner, opp_pos)
        pl_dist = math.dist(pl_pos, right_corner)

    return pl_dist < opp_dist


def is_into_box( pl_pos):
    """ """
    hull = ConvexHull([frontal_vtx_left, frontal_vtx_right,
                       [120, left_box_line_y], [120, right_box_line_y]])
    return point_in_hull(pl_pos, hull)


def is_into_def_zone( pl_pos):
    """ Definition zone (to score) into box """
    return (pl_pos[0] > frontal_box_line_x
            and isLeft(frontal_vtx_right, [120, 30], pl_pos)
            and not isLeft(frontal_vtx_left, [120, 50], pl_pos))


def is_final_zone( pl_pos, opp_pos):
    """ Si, en campo rival, el jugador está mas cerca de la porteria q cualquier defensa """

    if pl_pos[0] < 60: return False  # Filtramos un poquito

    #     inters_p= get_box_intersection( pl_pos )
    inters_p = get_small_box_inters(pl_pos)
    #     print('\nIntersection point with small box', inters_p)

    """ Once we have the nearest intersection point with box, calculate the nearest player """
    opp_dist, closest_opp = get_closest(inters_p, opp_pos)
    pl_dist = math.dist(pl_pos, inters_p)
    #     print('Op dist', opp_dist)
    #     print('Player dist', pl_dist)

    """ If player gets into the box in the way to goal before the defense is final zone  """
    if opp_dist > (pl_dist * 1.1):  # Let's give a 10% margin needed
        return True
    else:
        return False


def get_closest(point, players):
    """ From a players array to the point """
    closest = players[0]
    dist = 999
    for pl in players:
        if math.dist(point, pl) < dist:
            dist = math.dist(point, pl)
            closest = pl
    return dist, closest


# intersection between line(p1, p2) and line(p3, p4)
def intersect_lines(l1, l2):
    p1, p2 = l1
    p3, p4 = l2
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
    if denom == 0:  # parallel
        return None
    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
    if ua < 0 or ua > 1:  # out of range
        return None
    ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
    if ub < 0 or ub > 1:  # out of range
        return None
    x = x1 + ua * (x2 - x1)
    y = y1 + ua * (y2 - y1)
    return (x, y)


def get_box_intersection( pl_pos):
    """ """
    inters_p = [120, 40]  # Por si acaso he fet algo malament al codi seguent
    if pl_pos[0] < frontal_box_line_x:
        # In exterior zones the nearest point is the box vertex
        if pl_pos[1] < right_box_line_y:
            inters_p = frontal_vtx_right
        elif pl_pos[1] > left_box_line_y:
            inters_p = frontal_vtx_left
        else:  # Central zone
            inters_p = intersect_lines([pl_pos, [120, 40]], frontal_box_edge)
    elif pl_pos[1] < right_box_line_y:
        inters_p = intersect_lines([pl_pos, [120, 40]], right_box_edge)
    elif pl_pos[1] > left_box_line_y:
        inters_p = intersect_lines([pl_pos, [120, 40]], left_box_edge)

    return inters_p


def get_small_box_inters( pl_pos):
    """ """
    inters_p = intersect_lines([pl_pos, [120, 40]], small_box_edge)
    if not inters_p:
        # In exterior zones the nearest point is the box vertex
        if pl_pos[1] < right_box_line_y:
            inters_p = small_box_right_vtx
        elif pl_pos[1] > left_box_line_y:
            inters_p = small_box_left_vtx

    return inters_p


def get_exteriors( hull_vertx):
    """ We take the 2 more exterior players for each side to set the ext zones of both laterals (2,3) """

    right_pl1 = [0, 80]
    right_pl2 = [0, 80]
    left_pl1 = [80, 0]
    left_pl2 = [80, 0]
    for p in hull_vertx:
        if p[1] < right_pl1[1]:
            right_pl2 = right_pl1
            right_pl1 = p
        elif p[1] < right_pl2[1]:
            right_pl2 = p
        if p[1] > left_pl1[1]:
            left_pl2 = left_pl1
            left_pl1 = p
        elif p[1] > left_pl2[1]:
            left_pl2 = p

    """ Ordering exterior positions """
    if right_pl1[0] > right_pl2[0]:
        aux = right_pl1
        right_pl1 = right_pl2
        right_pl2 = aux
    if left_pl1[0] > left_pl2[0]:
        aux = left_pl1
        left_pl1 = left_pl2
        left_pl2 = aux

    #     print("max right=", right_pl1, "second max=", right_pl2)
    #     print("max left=", left_pl1, "second max=", left_pl2)

    return left_pl1, left_pl2, right_pl1, right_pl2


def zone_normalizing(team, period, nodes, gk, mean_block_height):
    """ HEIGHT NORMALIZATION BY ZONES """

    """ Normalitzem la Z1 per encabir-la a mig camp """

    zone1_min = nodes[(nodes.zone == 1)
                      & (nodes.team == team) & (nodes.period == period)
                      & (nodes.player != gk)].loc_avg_x.min()

    zone1_max = nodes[(nodes.zone == 1)
                      & (nodes.team == team) & (nodes.period == period)
                      & (nodes.player != gk)].loc_avg_x.max()

    nodes.loc[((nodes.zone == 1) & (nodes.team == team) &
               (nodes.period == period) & (nodes.player != gk)),
    'loc_avg_x'] = ((nodes.loc_avg_x - zone1_min) /
                    (zone1_max - zone1_min)) * 13 + 61

    """ Normalitzem les zones 2,3,6 per encabir-les al tram mig de les X (EPS virtual) """

    #     up_limit_h=  mean_block_height[team] +15
    down_limit_h = mean_block_height[team] - 20
    # Posem mínims inferiors i superiors per a que no es solapin els nodes per culpa dels outlyers
    nodes.loc[((nodes.zone == 2) | (nodes.zone == 3) | (nodes.zone == 6))
              & (nodes.team == team) & (nodes.period == period) & (nodes.player != gk)
              & (nodes.loc_avg_x < down_limit_h),
    'loc_avg_x'] = down_limit_h - 2
    #     nodes.loc[ ((nodes.zone==2) | (nodes.zone==3) | (nodes.zone==6))
    #              & (nodes.team == team) & (nodes.player != gk)
    #              & (nodes.loc_avg_x > up_limit_h),
    #              'loc_avg_x'] = up_limit_h +2

    zone_med_min = nodes[((nodes.zone == 2) | (nodes.zone == 3) | (nodes.zone == 6))
                         & (nodes.team == team) & (nodes.period == period)
                         & (nodes.player != gk)].loc_avg_x.min()

    zone_med_max = nodes[((nodes.zone == 2) | (nodes.zone == 3) | (nodes.zone == 6))
                         & (nodes.team == team) & (nodes.period == period)
                         & (nodes.player != gk)].loc_avg_x.max()

    nodes.loc[(nodes.zone == 6)
              & (nodes.team == team) & (nodes.period == period) & (nodes.player != gk),
    'loc_avg_x'] = ((nodes.loc_avg_x - zone_med_min) /
                    (zone_med_max - zone_med_min)) * 18 + EPS_BOTTOM_HEIGHT + 1

    nodes.loc[((nodes.zone == 2) | (nodes.zone == 3))
              & (nodes.team == team) & (nodes.period == period) & (nodes.player != gk),
    'loc_avg_x'] = ((nodes.loc_avg_x - zone_med_min) /
                    (zone_med_max - zone_med_min)) * 22 + EPS_BOTTOM_HEIGHT + 1

    """ Normalitzem les zones 7 i 11 per encabir-les a la zona de progressio exterior """

    nodes.loc[((nodes.zone == 7) | (nodes.zone == 11))
              & (nodes.team == team) & (nodes.period == period) & (nodes.player != gk)
              & (nodes.loc_avg_x < 80),  # Posem un mínim per a que no es solapin els nodes per culpa dels outlyers
    'loc_avg_x'] = 80

    zone_wing_min = 80
    zone_wing_max = BROKEN_HEIGHT

    nodes.loc[((nodes.zone == 7) | (nodes.zone == 11))
              & (nodes.team == team) & (nodes.period == period) & (nodes.player != gk),
    'loc_avg_x'] = (((nodes.loc_avg_x - zone_wing_min) /
                     (zone_wing_max - zone_wing_min))
                    * (BROKEN_HEIGHT - EXT_F_HEIGHT - 1)) + EXT_F_HEIGHT + 1

    """ Normalitzem les zones 77, 99 i 111 per encabir-les a la zona de finalitzacio exterior """

    #     zone_Fwing_min= nodes[ ((nodes.zone==77) | (nodes.zone==99) | (nodes.zone==111))
    #                              & (nodes.team == team)
    #                              & (nodes.player != gk) ].loc_avg_x.min()

    #     zone_Fwing_max= nodes[ ((nodes.zone==77) | (nodes.zone==99) | (nodes.zone==111))
    #                              & (nodes.team == team)
    #                              & (nodes.player != gk)].loc_avg_x.max()

    nodes.loc[((nodes.zone == 77) | (nodes.zone == 99) | (nodes.zone == 111))
              & (nodes.team == team) & (nodes.period == period) & (nodes.player != gk)
              & (nodes.loc_avg_x < BROKEN_HEIGHT + 1),
    'loc_avg_x'] = BROKEN_HEIGHT + 3

    """ Zona 10 només hem de retrocedir els més avançats del límit """

    nodes.loc[(nodes.zone == 10)
              & (nodes.team == team) & (nodes.period == period) & (nodes.player != gk)
              & (nodes.loc_avg_x > TOP_TEN_HEIGHT - 1),
    'loc_avg_x'] = TOP_TEN_HEIGHT - 1

    zone10_min = nodes[(nodes.zone == 10)
                       & (nodes.team == team) & (nodes.period == period)
                       & (nodes.player != gk)].loc_avg_x.min()
    zone10_min = min([zone10_min, EPS_TOP_HEIGHT])
    #     print("Min zone 10: ", zone10_min)

    zone10_max = nodes[(nodes.zone == 10)
                       & (nodes.team == team) & (nodes.period == period)
                       & (nodes.player != gk)].loc_avg_x.max()
    zone10_max = max([zone10_max, TOP_TEN_HEIGHT])
    #     print("Max zone 10: ", zone10_max)

    nodes.loc[((nodes.zone == 10)
               & (nodes.team == team) & (nodes.period == period) & (nodes.player != gk)),
    'loc_avg_x'] = (((nodes.loc_avg_x - zone10_min) /
                     (zone10_max - zone10_min))
                    * (TOP_TEN_HEIGHT - EPS_TOP_HEIGHT - 1)) + EPS_TOP_HEIGHT + 1

    """ Zona 9: Normalització tradicional """

    nodes.loc[(nodes.zone == 9)
              & (nodes.team == team) & (nodes.period == period) & (nodes.player != gk)
              & (nodes.loc_avg_x < 90),  # Posem un mínim per a que no es solapin els nodes per culpa dels outlyers
    'loc_avg_x'] = 90

    zone9_min = 90
    zone9_max = 120
    #     zone9_min= nodes[ (nodes.zone==9)
    #                      & (nodes.team == team) & (nodes.period == period)
    #                      & (nodes.player != gk) ].loc_avg_x.min()
    #     zone9_max= nodes[ (nodes.zone==9)
    #                      & (nodes.team == team) & (nodes.period == period)
    #                      & (nodes.player != gk) ].loc_avg_x.max()

    nodes.loc[(nodes.zone == 9)
              & (nodes.team == team) & (nodes.period == period) & (nodes.player != gk),
    'loc_avg_x'] = (((nodes.loc_avg_x - zone9_min) /
                     (zone9_max - zone9_min))
                    * (BROKEN_HEIGHT - TOP_TEN_HEIGHT - 2)) + TOP_TEN_HEIGHT + 1

    """ WIDE NORMALIZATION """

    """ Normalitzem les zones 2, 7 i 77 per encabir-les a la zona exterior dreta """

    nodes.loc[((nodes.zone == 7) | (nodes.zone == 2) | (nodes.zone == 77))
              & (nodes.team == team) & (nodes.period == period) & (nodes.player != gk)
              & (nodes.loc_avg_y < 60),
    'loc_avg_y'] = 60

    zone_left_wide_min = nodes[((nodes.zone == 7) | (nodes.zone == 2) | (nodes.zone == 77))
                               & (nodes.team == team) & (nodes.period == period)
                               & (nodes.player != gk)].loc_avg_y.min()
    zone_left_wide_max = nodes[((nodes.zone == 7) | (nodes.zone == 2) | (nodes.zone == 77))
                               & (nodes.team == team) & (nodes.period == period)
                               & (nodes.player != gk)].loc_avg_y.max()

    nodes.loc[((nodes.zone == 7) | (nodes.zone == 2) | (nodes.zone == 77))
              & (nodes.team == team) & (nodes.period == period) & (nodes.player != gk),
    'loc_avg_y'] = ((nodes.loc_avg_y - zone_left_wide_min) /
                    (zone_left_wide_max - zone_left_wide_min)) * 14 + 65

    """ Normalitzem les zones 3, 11 i 111 per encabir-les a la zona exterior esquerra """

    nodes.loc[((nodes.zone == 3) | (nodes.zone == 11) | (nodes.zone == 111))
              & (nodes.team == team) & (nodes.period == period) & (nodes.player != gk)
              & (nodes.loc_avg_y > 20),
    'loc_avg_y'] = 20

    nodes.loc[((nodes.zone == 3) | (nodes.zone == 11) | (nodes.zone == 111))
              & (nodes.team == team) & (nodes.period == period) & (nodes.player != gk)
              & (nodes.loc_avg_y > 20),
    'loc_avg_y'] = 20

    zone_right_wide_min = nodes[((nodes.zone == 3) | (nodes.zone == 11) | (nodes.zone == 111))
                                & (nodes.team == team) & (nodes.period == period)
                                & (nodes.player != gk)].loc_avg_y.min()
    zone_right_wide_max = nodes[((nodes.zone == 3) | (nodes.zone == 11) | (nodes.zone == 111))
                                & (nodes.team == team) & (nodes.period == period)
                                & (nodes.player != gk)].loc_avg_y.max()

    nodes.loc[((nodes.zone == 3) | (nodes.zone == 11) | (nodes.zone == 111))
              & (nodes.team == team) & (nodes.period == period) & (nodes.player != gk),
    'loc_avg_y'] = ((nodes.loc_avg_y - zone_right_wide_min) /
                    (zone_right_wide_max - zone_right_wide_min)) * 14 + 1

    """ Normalitzem les zones 6, 10, 9 i 99 per encabir-les a la zona interior """

    zone_center_wide_min = nodes[((nodes.zone == 6) | (nodes.zone == 10) | (nodes.zone == 9) | (nodes.zone == 99))
                                 & (nodes.team == team) & (nodes.period == period)
                                 & (nodes.player != gk)].loc_avg_y.min()
    zone_center_wide_max = nodes[((nodes.zone == 6) | (nodes.zone == 10) | (nodes.zone == 9) | (nodes.zone == 99))
                                 & (nodes.team == team) & (nodes.period == period)
                                 & (nodes.player != gk)].loc_avg_y.max()

    nodes.loc[((nodes.zone == 6) | (nodes.zone == 10) | (nodes.zone == 9) | (nodes.zone == 99))
              & (nodes.team == team) & (nodes.period == period) & (nodes.player != gk),
    'loc_avg_y'] = (((nodes.loc_avg_y - zone_center_wide_min) /
                     (zone_center_wide_max - zone_center_wide_min))
                    * (RIGHT_EXT_WIDTH - LEFT_EXT_WIDTH - 2)) + LEFT_EXT_WIDTH + 1


