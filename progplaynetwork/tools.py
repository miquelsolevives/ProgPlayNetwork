
def line(p1, p2):
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0] * p2[1] - p2[0] * p1[1])
    return A, B, -C


def intersection(L1, L2):
    D = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x, y
    else:
        return False


# intersection between line(p1, p2) and line(p3, p4)
def intersect(p1, p2, p3, p4):
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



def get_loc_dim(loc, dim):
    if isinstance(loc, (list, tuple, np.ndarray)):
        return loc[dim]


def paint_arrow( orig_x, orig_y, dest_x, dest_y,
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


def paint_edge_arrows( orig_x_array, orig_y_array, dest_x_array, dest_y_array,
                      dest_node_size_array, orig_node_size_array, ax,
                      lw_array, bidir=False, color='white', zorder=1, alpha=1):
    """ """
    for idx, x in enumerate(orig_x_array):
        width = lw_array.iloc[idx]
        dest_node_size = dest_node_size_array.iloc[idx]
        orig_node_size = orig_node_size_array.iloc[idx]
        #         node_size = NODE_SIZE * (node_amount**1.7) + MIN_NODE_SIZE
        #         display( width, dest_node_size)
        dest_node_rad = ((dest_node_size + MIN_NODE_SIZE) / math.pi) ** (1 / 1.9)
        orig_node_rad = ((orig_node_size + MIN_NODE_SIZE) / math.pi) ** (1 / 1.9)

        ppm = fig.get_figwidth() * fig.dpi / 90  # Punts per metre (unitat de mesura del gràfic)
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


import numpy as np
import matplotlib.pyplot as plt
import math

# Definir la función de la parábola
def get_parabola(right=True):
    """ """
    # Generar valores de x
    x = np.linspace(0, 1, 120)

    if right:
        return x, +0.1 * (x ** 14) + 0.3 * x - 0.4 * x ** 0.6
    else:
        return x, -0.1 * (x ** 14) - 0.3 * x + 0.4 * x ** 0.6


def paint_crosses(orig_x, orig_y, dest_x, dest_y, width, pitch, ax, zorder, color):
    """ """
    for idx, x in enumerate(orig_x):
        paint_parabola((x, orig_y.iloc[idx]), (dest_x.iloc[idx], dest_y.iloc[idx]),
                       width.iloc[idx], pitch, ax, zorder, color)


def paint_parabola(p0, p1, width, pitch, ax, zorder, color):
    """ """
    dy = p1[1] - p0[1]
    dx = p1[0] - p0[0]

    if dx == 0:
        rad_angl = math.pi / 2 if dy > 0 else -math.pi / 2
    else:
        m = dy / dx
        if dx < 0:  # Quadrants esquerres
            rad_angl = math.pi + math.atan(m)
        else:  # Quadrants drets
            rad_angl = math.atan(m)

    if dy < 0:  # Extrem esquerra
        x, y = get_parabola(False)
    else:  # Extrem dret
        x, y = get_parabola(True)

    dist = math.dist(p0, p1)
    #     x_factor= dist*math.cos(rad_angl)
    #     y_factor= dist*math.sin(rad_angl)
    x_factor = x * dist
    y_factor = y * dist

    x_trans = x_factor * math.cos(rad_angl) - y_factor * math.sin(rad_angl) + p0[0]
    y_trans = x_factor * math.sin(rad_angl) + y_factor * math.cos(rad_angl) + p0[1]
    #     plt.plot( x, y)
    #     plt.plot( x_factor, y_factor )
    pitch.plot(x_trans, y_trans, lw=width * 2, ax=ax, zorder=zorder, color=color)


def draw_curve(p1, p2):
    a = (p2[1] - p1[1]) / (np.cosh(p2[0]) - np.cosh(p1[0]))
    b = p1[1] - a * np.cosh(p1[0])
    x = np.linspace(p1[0], p2[0], 30)
    y = a * np.cosh(x) + b
    return x, y


def draw_function(p1, p2):
    """ """
    import sympy as sp

    # Create the sympy function f(x)
    f_x = sp.sympify("x*x/4+1")
    symbol_x = sp.Symbol('x')

    # Create domain and image
    domain_x = np.linspace(p1[0], p2[0], 30)
    image = [f_x.subs(symbol_x, value) for value in domain_x]

    pitch.plot(domain_x, image, ax=ax, color='violet')


def change_coord(p1, p2):
    """ """
    # Desplazamiento
    x = x + dx
    y = y + dy

    # Rotación
    theta_rad = math.radians(theta)  # Convertir el ángulo a radianes
    x_new = x * math.cos(theta_rad) - y * math.sin(theta_rad)
    y_new = x * math.sin(theta_rad) + y * math.cos(theta_rad)