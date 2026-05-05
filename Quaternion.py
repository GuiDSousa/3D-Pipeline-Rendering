import numpy as np


class Quaternion:
	def __init__(self, w, x, y, z):
		self.w = float(w)  # Parte real
		self.x = float(x)  # Componente i
		self.y = float(y)  # Componente j
		self.z = float(z)  # Componente k

	def norm(self):
		"""Retorna a norma do quaternion."""
		return np.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)

	def normalize(self):
		"""Normaliza o quaternion."""
		n = self.norm()
		if n == 0:
			raise ValueError("Nao e possivel normalizar quaternion nulo.")
		self.w /= n
		self.x /= n
		self.y /= n
		self.z /= n
		return self

	def conjugate(self):
		"""Retorna o conjugado do quaternion."""
		return Quaternion(self.w, -self.x, -self.y, -self.z)

	def __mul__(self, other):
		"""Produto de Hamilton (multiplicacao de quaternions)."""
		if not isinstance(other, Quaternion):
			raise TypeError("Multiplicacao suportada apenas entre quaternions.")

		w1, x1, y1, z1 = self.w, self.x, self.y, self.z
		w2, x2, y2, z2 = other.w, other.x, other.y, other.z

		return Quaternion(
			w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
			w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
			w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
			w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
		)

	@staticmethod
	def from_axis_angle(axis, angle):
		"""Cria um quaternion a partir de eixo unitario e angulo em radianos."""
		axis = np.asarray(axis, dtype=float)
		norm_axis = np.linalg.norm(axis)
		if norm_axis == 0:
			raise ValueError("Eixo de rotacao nao pode ser nulo.")

		axis = axis / norm_axis
		half = angle / 2.0
		s = np.sin(half)
		q = Quaternion(np.cos(half), axis[0] * s, axis[1] * s, axis[2] * s)
		return q.normalize()

	def rotate_point(self, point):
		"""Roda um ponto 3D usando q * p * q_con."""
		p = Quaternion(0.0, point[0], point[1], point[2])
		q = Quaternion(self.w, self.x, self.y, self.z).normalize()
		rotated = q * p * q.conjugate()
		return np.array([rotated.x, rotated.y, rotated.z], dtype=float)

	def to_rotation_matrix(self):
		"""Converte para matriz de rotacao 4x4."""
		q = Quaternion(self.w, self.x, self.y, self.z).normalize()
		w, x, y, z = q.w, q.x, q.y, q.z

		return np.array(
			[
				[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w), 0],
				[2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w), 0],
				[2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y), 0],
				[0, 0, 0, 1],
			],
			dtype=float,
		)
