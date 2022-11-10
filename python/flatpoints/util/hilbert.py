import math

Extent = dict['xmax': float, 'xmin': float, 'ymax': float, 'ymin': float]

WORLD: Extent = {
    'xmax': 180.0,
    'xmin': -180.0,
    'ymax': 90.0,
    'ymin': -90.0
}

MAX_N = 31


def encode(n: int, x: list[float], y: list[float], extent: Extent) -> list[int]:
    nn = 1 << n
    xpos = x_to_cols(nn, x, extent["xmax"], extent["xmin"])
    ypos = y_to_rows(nn, y, extent["ymax"], extent["ymin"])
    return [pos_to_ind(nn, xpos[i], ypos[i]) for i in range(len(x))]


def decode(n: int, h: list[int], extent: Extent) -> (list[float], list[float]):
    x: list[float] = []
    y: list[float] = []
    nn = 1 << n
    print("starting for loop")
    for hh in h:
        xx, yy = ind_to_pos(nn, hh)
        x.append(xx)
        y.append(yy)
    print("returing")
    return (cols_to_x(nn, x, extent["xmax"], extent["xmin"]),
            rows_to_y(nn, y, extent["ymax"], extent["ymin"]))


def rotate(n, x, y, rx, ry) -> (int, int):
    if ry == 0:
        if rx == 1:
            x = n - 1 - x
            y = n - 1 - y
        t = x
        x = y
        y = t
    return (x, y)


def pos_to_ind(n, x, y) -> int:
    d = 0
    s = n // 2
    while s > 0:
        rx = (x & s) > 0
        ry = (y & s) > 0
        d += s * s * ((3 * rx) ^ ry)
        x, y = rotate(n, x, y, rx, ry)
        s //= 2
    return d


def ind_to_pos(n, h) -> (int, int):
    t = h
    x = 0
    y = 0
    s = 1
    while s < n:
        rx = 1 & (t // 2)
        ry = 1 & (t ^ rx)
        x, y = rotate(s, x, y, rx, ry)
        x += s * rx
        y += s * ry
        t //= 4
        s *= 2
    return (x, y)


def x_to_cols(n: int, x: list[float], xmax: float, xmin: float) -> list[int]:
    cols = []
    diff = n / (xmax - xmin)
    for i in x:
        if i >= xmin and i < xmax:
            cols.append(math.floor((i - xmin) * diff))
        elif i == xmax:
            cols.append(n - 1)
        else:
            cols.append(-1)
    return cols


def cols_to_x(n: int, cols: list[int], xmax: float, xmin: float) -> list[float]:
    x = []
    diff = (xmax - xmin) / n
    for i in cols:
        x.append(xmin + ((i + 0.5) * diff))
    return x


def y_to_rows(n: int, y: list[float], ymax: float, ymin: float) -> list[int]:
    rows = []
    diff = n / (ymax - ymin)
    for i in y:
        if i >= ymin and i < ymax:
            rows.append(math.floor((i - ymin) * diff))
        elif i == ymax:
            rows.append(n - 1)
        else:
            rows.append(-1)
    return rows


def rows_to_y(n: int, rows: list[float], ymax: float, ymin: float) -> list[float]:
    y = []
    diff = (ymax - ymin) / n
    for i in rows:
        y.append(ymin + ((i + 0.5) * diff))
    return y
