import numpy as np

from Quaternion import Quaternion


class Objeto3D:
    def __init__(self, vertices, arestas, cor=(0, 0, 1), faces=None):
        """
        vertices: lista de pontos 3D (x, y, z)
        arestas: lista de pares (i, j) indices dos vertices
        cor: cor RGB (0 a 1) do objeto
        """
        self.vertices = np.array(vertices)  # Converter para numpy array
        self.arestas = arestas
        self.cor = cor
        # faces: lista de listas de indices (poligonos) para renderizacao preenchida
        self.faces = faces or []
        self.model_matrix = np.eye(4)  # Matriz de modelo inicial (identidade)
        self.orientation = Quaternion(1, 0, 0, 0)
        # Velocidade angular: (eixo, velocidade_rad_s)
        self.angular_velocity = None  # None = sem rotação automática
        # Órbita: (center_pos, raio, velocidade_angular_rad_s, eixo_orbital)
        self.orbital_motion = None  # None = sem órbita

    def apply_transform(self, matrix):
        """Aplica transformacao ao objeto."""
        # Nova transformacao aplicada antes da atual.
        self.model_matrix = matrix @ self.model_matrix

    def get_transformed_vertices(self):
        """Retorna vertices transformados pelo model_matrix."""
        # Aplicar self.model_matrix aos vertices (coordenadas homogeneas)
        vertices_h = np.hstack([self.vertices, np.ones((self.vertices.shape[0], 1))])
        transformed = (self.model_matrix @ vertices_h.T).T
        return transformed[:, :3]

    def set_rotation_quaternion(self, q):
        """Define orientacao via quaternion."""
        if not isinstance(q, Quaternion):
            raise TypeError("q deve ser instancia de Quaternion.")
        self.orientation = Quaternion(q.w, q.x, q.y, q.z).normalize()

    def rotate_quaternion(self, axis, angle):
        """Aplica rotacao incremental por quaternion."""
        delta = Quaternion.from_axis_angle(axis, angle)
        self.orientation = (delta * self.orientation).normalize()

    def set_position(self, x, y, z):
        """Define translacao atual do objeto."""
        self.model_matrix[0, 3] = x
        self.model_matrix[1, 3] = y
        self.model_matrix[2, 3] = z

    def set_angular_velocity(self, axis, speed_rad_s):
        """Define velocidade angular (eixo e velocidade em rad/s)."""
        self.angular_velocity = (np.asarray(axis, dtype=float), float(speed_rad_s))

    def apply_rotation_step(self, delta_time):
        """Aplica rotacao incremental baseada em tempo decorrido (delta_time em segundos)."""
        if self.angular_velocity is None:
            return
        axis, speed = self.angular_velocity
        angle_increment = speed * delta_time
        self.rotate_quaternion(axis, angle_increment)

    def set_orbital_motion(self, center_pos, radius, orbital_speed_rad_s, orbital_axis):
        """Define movimento orbital (órbita em torno de um ponto central)."""
        self.orbital_motion = {
            'center': np.asarray(center_pos, dtype=float),
            'radius': float(radius),
            'speed': float(orbital_speed_rad_s),
            'axis': np.asarray(orbital_axis, dtype=float),
            'current_angle': 0.0
        }

    def apply_orbital_step(self, delta_time):
        """Aplica movimento orbital baseado em tempo decorrido."""
        if self.orbital_motion is None:
            return
        orbit = self.orbital_motion
        angle_increment = orbit['speed'] * delta_time
        orbit['current_angle'] += angle_increment
        
        # Calcular posição na órbita (parametrização circular)
        # Eixo da órbita define o plano de rotação
        axis = orbit['axis'] / (np.linalg.norm(orbit['axis']) + 1e-8)
        
        # Criar dois vetores perpendiculares ao eixo
        if abs(axis[0]) < 0.9:
            perp1 = np.cross(axis, [1, 0, 0])
        else:
            perp1 = np.cross(axis, [0, 1, 0])
        perp1 = perp1 / (np.linalg.norm(perp1) + 1e-8)
        perp2 = np.cross(axis, perp1)
        perp2 = perp2 / (np.linalg.norm(perp2) + 1e-8)
        
        # Posição na órbita
        x = orbit['radius'] * np.cos(orbit['current_angle']) * perp1 + \
            orbit['radius'] * np.sin(orbit['current_angle']) * perp2
        orbital_pos = orbit['center'] + x
        
        # Atualizar posição (mantendo escala e rotação)
        self.set_position(orbital_pos[0], orbital_pos[1], orbital_pos[2])
