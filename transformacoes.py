import numpy as np


def translacao(tx, ty, tz):
    """Matriz de translacao 4x4."""
    return np.array(
        [
            [1, 0, 0, tx],
            [0, 1, 0, ty],
            [0, 0, 1, tz],
            [0, 0, 0, 1],
        ]
    )


def escala(sx, sy, sz):
    """Matriz de escala 4x4."""
    return np.array(
        [
            [sx, 0, 0, 0],
            [0, sy, 0, 0],
            [0, 0, sz, 0],
            [0, 0, 0, 1],
        ],
        dtype=float,
    )


def rotacao_x(theta):
    """Matriz de rotacao em torno do eixo x (em radianos)."""
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array(
        [
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1],
        ],
        dtype=float,
    )


def rotacao_z(theta):
    """Matriz de rotacao em torno do eixo z."""
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array(
        [
            [c, -s, 0, 0],
            [s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ],
        dtype=float,
    )


def rotacao_y(theta):
    """Matriz de rotacao em torno do eixo y."""
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array(
        [
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1],
        ],
        dtype=float,
    )


def cisalhamento_xy(a, b):
    """Matriz de cisalhamento nos eixos x e y."""
    return np.array(
        [
            [1, a, 0, 0],
            [b, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ],
        dtype=float,
    )
