import numpy as np
import pygame


class Renderizador:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.image = np.zeros((height, width, 3))  # Buffer RGB auxiliar

    def render(self, surface, objetos, camera, background=(10, 10, 16), render_mode="WIREFRAME"):
        """Pipeline completo de renderizacao."""
        surface.fill(background)

        # 1. Obter matrizes da camera
        v = camera.get_view_matrix()
        p = camera.get_projection_matrix()

        for obj in objetos:
            # 2. Transformacao Modelo-Visao-Projecao
            rot_q = obj.orientation.to_rotation_matrix()
            mvp = p @ v @ obj.model_matrix @ rot_q

            # 3. Transformar vertices para coordenadas de clip
            vertices_clip = self._transform_vertices(obj.vertices, mvp)

            # 4. Recorte no cubo normalizado [-1, 1]
            # 5. Divisao por w (perspective divide)
            # 6. Mapeamento para coordenadas de viewport
            # 7. Rasterizacao das arestas (Bresenham 3D)
            vertices_screen = self._clip_to_screen(vertices_clip)
            color = tuple(int(max(0.0, min(1.0, c)) * 255) for c in obj.cor)

            # Filled mode: draw faces first using painter's algorithm if faces provided
            if render_mode == "FILLED" and getattr(obj, "faces", None):
                # build list of (depth, face_indices)
                faces_to_draw = []
                for f in obj.faces:
                    # compute average depth in clip space (z/w)
                    vals = []
                    pts = []
                    valid = True
                    for idx in f:
                        vc = vertices_clip[idx]
                        if abs(vc[3]) < 1e-8:
                            valid = False
                            break
                        ndc_z = vc[2] / vc[3]
                        vals.append(ndc_z)
                        sc = vertices_screen[idx]
                        if sc is None:
                            valid = False
                            break
                        pts.append(sc)
                    if not valid or len(pts) < 3:
                        continue
                    depth = sum(vals) / len(vals)
                    faces_to_draw.append((depth, pts))

                # sort back-to-front (larger depth is nearer if ndc z in [-1,1])
                faces_to_draw.sort(key=lambda x: x[0])
                for k, (depth, pts) in enumerate(faces_to_draw):
                    # slight per-face shading based on order
                    shade = 0.9 - 0.05 * (k % 6)
                    fill_col = tuple(max(0, min(255, int(c * shade))) for c in color)
                    try:
                        pygame.draw.polygon(surface, fill_col, pts)
                    except Exception:
                        pass

            # Always draw wireframe on top for clarity
            for i, j in obj.arestas:
                p1 = vertices_screen[i]
                p2 = vertices_screen[j]
                if p1 is not None and p2 is not None:
                    self._draw_line(surface, p1, p2, color)

    def _transform_vertices(self, vertices, matrix):
        """Aplica a transformacao a vertices."""
        vertices_h = np.hstack([vertices, np.ones((vertices.shape[0], 1))])
        return (matrix @ vertices_h.T).T

    def _clip_to_screen(self, vertices_clip):
        """Converte clip space para coordenadas de tela, com clipping basico."""
        out = []
        for vc in vertices_clip:
            w = vc[3]
            if abs(w) < 1e-8:
                out.append(None)
                continue

            ndc = vc[:3] / w
            if np.any(ndc < -1.2) or np.any(ndc > 1.2):
                out.append(None)
                continue

            x = int((ndc[0] + 1) * 0.5 * self.width)
            y = int((1 - (ndc[1] + 1) * 0.5) * self.height)
            out.append((x, y))
        return out

    def _draw_line(self, surface, p1, p2, cor):
        """Desenha linha entre dois pontos na tela (Bresenham 3D)."""
        pygame.draw.line(surface, cor, p1, p2, 1)
