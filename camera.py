import numpy as np


class Camera:
    def __init__(self, eye, at, up, fov, aspect, near, far):
        self.eye = eye  # Posicao da camera
        self.at = at  # Ponto para onde a camera esta olhando
        self.up = up  # Vetor de up da camera
        self.fov = fov  # Campo de visao (em graus)
        self.aspect = aspect  # Aspect ratio (largura/altura)
        self.near = near  # Plano de recorte proximo
        self.far = far  # Plano de recorte distante
        self._compute_vectors()  # Calcula os vetores de camera (u, v, n)

    def _compute_vectors(self):
        """Calcula os vetores n, v e u da camera (Secao 2.10.1)."""
        # n = direcao da camera (normal ao plano de projecao)
        n = self.eye - self.at
        self.n = n / np.linalg.norm(n)  # Normaliza n

        # v = vetor vertical (ortogonal a n)
        # u = direcao horizontal (produto vetorial)
        u = np.cross(self.up, self.n)
        self.u = u / np.linalg.norm(u)

        v = np.cross(self.n, self.u)
        self.v = v / np.linalg.norm(v)

    def get_view_matrix(self):
        """Retorna a matriz de visualizacao da camera (Secao 2.10.1.2)."""
        # Combinar translacao e rotacao para criar a matriz de visualizacao
        self._compute_vectors()
        ex, ey, ez = self.eye

        return np.array(
            [
                [self.u[0], self.u[1], self.u[2], -np.dot(self.u, [ex, ey, ez])],
                [self.v[0], self.v[1], self.v[2], -np.dot(self.v, [ex, ey, ez])],
                [self.n[0], self.n[1], self.n[2], -np.dot(self.n, [ex, ey, ez])],
                [0, 0, 0, 1],
            ],
            dtype=float,
        )

    def get_projection_matrix(self):
        """Retorna a matriz de projecao da camera (Secao 2.10.2.2)."""
        f = 1.0 / np.tan(np.radians(self.fov) / 2)
        # Construir matriz de projecao perspectiva
        n = self.near
        f_far = self.far
        a = self.aspect

        return np.array(
            [
                [f / a, 0, 0, 0],
                [0, f, 0, 0],
                [0, 0, (f_far + n) / (n - f_far), (2 * f_far * n) / (n - f_far)],
                [0, 0, -1, 0],
            ],
            dtype=float,
        )
