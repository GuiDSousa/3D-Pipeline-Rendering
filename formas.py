import numpy as np

from objeto3d import Objeto3D


def criar_cubo(tamanho=1.0, cor=(0.2, 0.8, 1.0)):
    h = tamanho / 2.0
    vertices = [
        (-h, -h, -h),
        (h, -h, -h),
        (h, h, -h),
        (-h, h, -h),
        (-h, -h, h),
        (h, -h, h),
        (h, h, h),
        (-h, h, h),
    ]
    arestas = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),
        (4, 5),
        (5, 6),
        (6, 7),
        (7, 4),
        (0, 4),
        (1, 5),
        (2, 6),
        (3, 7),
    ]
    # faces as quads (each face is list of vertex indices)
    faces = [
        [0, 1, 2, 3],
        [4, 5, 6, 7],
        [0, 1, 5, 4],
        [2, 3, 7, 6],
        [1, 2, 6, 5],
        [0, 3, 7, 4],
    ]
    return Objeto3D(vertices, arestas, cor, faces)


def criar_piramide(base=1.4, altura=1.8, cor=(1.0, 0.65, 0.2)):
    h = base / 2.0
    vertices = [
        (-h, -h, 0),
        (h, -h, 0),
        (h, h, 0),
        (-h, h, 0),
        (0, 0, altura),
    ]
    arestas = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),
        (0, 4),
        (1, 4),
        (2, 4),
        (3, 4),
    ]
    # faces: base quad and 4 triangular sides
    faces = [
        [0, 1, 2, 3],
        [0, 1, 4],
        [1, 2, 4],
        [2, 3, 4],
        [3, 0, 4],
    ]
    return Objeto3D(vertices, arestas, cor, faces)


def criar_esfera(raio=1.0, stacks=10, slices=16, cor=(0.35, 1.0, 0.55)):
    vertices = []
    for i in range(stacks + 1):
        phi = np.pi * i / stacks
        y = raio * np.cos(phi)
        r = raio * np.sin(phi)
        for j in range(slices):
            theta = 2 * np.pi * j / slices
            x = r * np.cos(theta)
            z = r * np.sin(theta)
            vertices.append((x, y, z))

    arestas = []
    for i in range(stacks + 1):
        for j in range(slices):
            idx = i * slices + j
            nxt = i * slices + ((j + 1) % slices)
            arestas.append((idx, nxt))
            if i < stacks:
                down = (i + 1) * slices + j
                arestas.append((idx, down))

    # faces as quads between stacks (degenerate near poles handled by renderer)
    faces = []
    for i in range(stacks):
        for j in range(slices):
            a = i * slices + j
            b = i * slices + ((j + 1) % slices)
            c = (i + 1) * slices + ((j + 1) % slices)
            d = (i + 1) * slices + j
            faces.append([a, b, c, d])

    return Objeto3D(vertices, arestas, cor, faces)


def criar_prisma_hexagonal(raio=0.8, altura=1.4, cor=(0.95, 0.3, 0.3)):
    vertices = []
    for y in (-altura / 2.0, altura / 2.0):
        for i in range(6):
            ang = 2 * np.pi * i / 6
            vertices.append((raio * np.cos(ang), y, raio * np.sin(ang)))

    arestas = []
    for i in range(6):
        arestas.append((i, (i + 1) % 6))
        arestas.append((i + 6, ((i + 1) % 6) + 6))
        arestas.append((i, i + 6))

    # faces: bottom, top and 6 side quads
    faces = []
    faces.append([0, 1, 2, 3, 4, 5])
    faces.append([6, 7, 8, 9, 10, 11])
    for i in range(6):
        a = i
        b = (i + 1) % 6
        faces.append([a, b, b + 6, a + 6])

    return Objeto3D(vertices, arestas, cor, faces)


def criar_cilindro(raio=0.7, altura=1.6, slices=18, cor=(0.8, 0.5, 0.2)):
    """Cria um prisma cilíndrico (wireframe) com `slices` subdivisoes."""
    vertices = []
    half = altura / 2.0
    # bottom circle (y = -half), top circle (y = +half)
    for y in (-half, half):
        for i in range(slices):
            theta = 2 * np.pi * i / slices
            x = raio * np.cos(theta)
            z = raio * np.sin(theta)
            vertices.append((x, y, z))

    arestas = []
    # circle edges
    for base in (0, slices):
        for i in range(slices):
            a = base + i
            b = base + ((i + 1) % slices)
            arestas.append((a, b))

    # vertical edges
    for i in range(slices):
        arestas.append((i, i + slices))

    # faces: bottom cap, top cap, and side quads
    faces = []
    bottom = [i for i in range(0, slices)]
    top = [i + slices for i in range(0, slices)]
    faces.append(bottom)
    faces.append(top)
    for i in range(slices):
        a = i
        b = (i + 1) % slices
        faces.append([a, b, b + slices, a + slices])

    return Objeto3D(vertices, arestas, cor, faces)
