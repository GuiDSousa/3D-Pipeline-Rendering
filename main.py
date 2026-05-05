import numpy as np
import pygame

from camera import Camera
from formas import criar_cubo, criar_esfera, criar_piramide, criar_prisma_hexagonal
from renderizador import Renderizador
from formas import criar_cilindro
from transformacoes import escala, translacao


def main():
    pygame.init()

    width, height = 1200, 720
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("Pipeline 3D em Software - NumPy + Pygame")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)

    renderizador = Renderizador(width, height)
    camera = Camera(
        eye=np.array([0.0, 1.5, 8.0], dtype=float),
        at=np.array([0.0, 0.0, 0.0], dtype=float),
        up=np.array([0.0, 1.0, 0.0], dtype=float),
        fov=60,
        aspect=width / height,
        near=0.1,
        far=100.0,
    )

    # start with empty scene; objects will be added by UI
    objetos = []

    # Simple UI buttons
    class Button:
        def __init__(self, rect, text, color=(200, 200, 200)):
            self.rect = pygame.Rect(rect)
            self.text = text
            self.color = color

        def draw(self, surf, active=False):
            fill = self.color
            border = (30, 30, 30)
            txt_color = (0, 0, 0)
            if active:
                fill = (255, 215, 90)
                border = (255, 245, 180)
                txt_color = (20, 20, 20)

            pygame.draw.rect(surf, fill, self.rect)
            pygame.draw.rect(surf, border, self.rect, 2)
            txt = font.render(self.text, True, txt_color)
            tx = self.rect.x + 6
            ty = self.rect.y + (self.rect.height - txt.get_height()) // 2
            surf.blit(txt, (tx, ty))

        def clicked(self, pos):
            return self.rect.collidepoint(pos)

    # Sidebar configuration
    sidebar_w = 200
    btn_w = sidebar_w - 20
    btn_h = 36
    margin_x = 10
    start_y = 12
    btn_gap = 6

    btn_add_cube = Button((margin_x, start_y + 0 * (btn_h + btn_gap), btn_w, btn_h), "Adicionar Cubo")
    btn_add_sphere = Button((margin_x, start_y + 1 * (btn_h + btn_gap), btn_w, btn_h), "Adicionar Esfera")
    btn_add_prisma = Button((margin_x, start_y + 2 * (btn_h + btn_gap), btn_w, btn_h), "Adicionar Prisma")
    btn_add_piramide = Button((margin_x, start_y + 3 * (btn_h + btn_gap), btn_w, btn_h), "Adicionar Pirâmide")
    btn_add_cilindro = Button((margin_x, start_y + 4 * (btn_h + btn_gap), btn_w, btn_h), "Adicionar Cilindro")
    btn_orbital_scene = Button((margin_x, start_y + 5 * (btn_h + btn_gap), btn_w, btn_h), "Cena de Órbita")
    btn_mode_translate = Button((margin_x, start_y + 7 * (btn_h + btn_gap), btn_w, btn_h), "Modo: Transladar")
    btn_mode_rotate = Button((margin_x, start_y + 8 * (btn_h + btn_gap), btn_w, btn_h), "Modo: Rotacionar")
    btn_mode_scale = Button((margin_x, start_y + 9 * (btn_h + btn_gap), btn_w, btn_h), "Modo: Escalar")
    btn_plane_xy = Button((margin_x, start_y + 11 * (btn_h + btn_gap), btn_w, btn_h), "Plano XY")
    btn_plane_xz = Button((margin_x, start_y + 12 * (btn_h + btn_gap), btn_w, btn_h), "Plano XZ")
    btn_plane_yz = Button((margin_x, start_y + 13 * (btn_h + btn_gap), btn_w, btn_h), "Plano YZ")
    btn_render_wire = Button((margin_x, start_y + 14 * (btn_h + btn_gap), btn_w, btn_h), "Render: Wireframe")
    btn_render_filled = Button((margin_x, start_y + 15 * (btn_h + btn_gap), btn_w, btn_h), "Render: Filled")
    btn_toggle_auto_rotate = Button((margin_x, start_y + 16 * (btn_h + btn_gap), btn_w, btn_h), "Rotação: Ativada")

    running = True
    selected = None
    dragging = False
    grab_offset = np.array([0.0, 0.0, 0.0])
    drag_plane = "XY"  # XY keeps Z fixed; better for ordered-pair manipulation
    drag_plane_value = 0.0
    transform_mode = "TRANSLATE"
    last_mouse = None
    render_mode = "WIREFRAME"
    auto_rotate_enabled = True  # Toggle para rotacao continua
    last_frame_time = pygame.time.get_ticks() / 1000.0  # em segundos

    def screen_ray(mx, my):
        # returns ray origin and direction in world coordinates
        ndc_x = (mx / width) * 2.0 - 1.0
        ndc_y = 1.0 - (my / height) * 2.0

        V = camera.get_view_matrix()
        P = camera.get_projection_matrix()
        inv = np.linalg.inv(P @ V)

        near_clip = np.array([ndc_x, ndc_y, -1.0, 1.0])
        far_clip = np.array([ndc_x, ndc_y, 1.0, 1.0])

        near_world = inv @ near_clip
        far_world = inv @ far_clip
        near_world /= near_world[3]
        far_world /= far_world[3]

        origin = near_world[:3]
        direction = far_world[:3] - origin
        direction = direction / np.linalg.norm(direction)
        return origin, direction

    def project_to_screen(point):
        V = camera.get_view_matrix()
        P = camera.get_projection_matrix()
        clip = (P @ V @ np.array([point[0], point[1], point[2], 1.0]))
        if abs(clip[3]) < 1e-8:
            return None
        ndc = clip[:3] / clip[3]
        # Keep points near the view frustum; loose threshold avoids dropping partial lines.
        if ndc[2] < -2.0 or ndc[2] > 2.0:
            return None
        sx = int((ndc[0] + 1.0) * 0.5 * width)
        sy = int((1.0 - (ndc[1] + 1.0) * 0.5) * height)
        return (sx, sy)


    def intersect_ray_plane(origin, direction, plane_name, plane_value):
        # plane_name in {XY, XZ, YZ}
        if plane_name == "XY":
            # z = plane_value
            denom = direction[2]
            if abs(denom) < 1e-6:
                return None
            t = (plane_value - origin[2]) / denom
        elif plane_name == "XZ":
            # y = plane_value
            denom = direction[1]
            if abs(denom) < 1e-6:
                return None
            t = (plane_value - origin[1]) / denom
        else:
            # YZ -> x = plane_value
            denom = direction[0]
            if abs(denom) < 1e-6:
                return None
            t = (plane_value - origin[0]) / denom
        return origin + direction * t

    def get_scale_value(obj):
        # uniform scale currently stored on matrix diagonal
        return float(obj.model_matrix[0, 0])

    def set_uniform_scale(obj, scale_value):
        # keep translation while updating uniform scale
        scale_value = max(0.2, min(4.0, float(scale_value)))
        t = obj.model_matrix[:3, 3].copy()
        obj.model_matrix = np.eye(4)
        obj.model_matrix[0, 0] = scale_value
        obj.model_matrix[1, 1] = scale_value
        obj.model_matrix[2, 2] = scale_value
        obj.model_matrix[:3, 3] = t

    while running:
        clock.tick(60)
        current_time = pygame.time.get_ticks() / 1000.0
        delta_time = current_time - last_frame_time
        last_frame_time = current_time
        delta_time = min(delta_time, 0.05)  # Clamp para evitar pulos grandes

        # Aplicar rotacao continua se habilitada
        if auto_rotate_enabled:
            for obj in objetos:
                if obj.angular_velocity is not None:
                    obj.apply_rotation_step(delta_time)
                if obj.orbital_motion is not None:
                    obj.apply_orbital_step(delta_time)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.size
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                renderizador.width = width
                renderizador.height = height
                camera.aspect = width / height
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    drag_plane = "XY"
                elif event.key == pygame.K_2:
                    drag_plane = "XZ"
                elif event.key == pygame.K_3:
                    drag_plane = "YZ"
                elif event.key == pygame.K_DELETE:
                    if selected is not None and selected in objetos:
                        objetos.remove(selected)
                        selected = None
                        dragging = False
                        last_mouse = None
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # ignore clicks inside sidebar area for scene interactions
                if mx <= sidebar_w:
                    if btn_add_cube.clicked((mx, my)):
                        new = criar_cubo(1.0, cor=(0.6, 0.6, 1.0))
                        idx = len(objetos)
                        x = (idx - 2) * 2.2
                        new.apply_transform(translacao(x, 0.0, 0.0))
                        set_uniform_scale(new, 1.0)
                        new.set_angular_velocity([0, 1, 0], 1.0)  # Rotacao em Y a 1 rad/s
                        objetos.append(new)
                    elif btn_add_sphere.clicked((mx, my)):
                        new = criar_esfera(raio=1.0, stacks=10, slices=18, cor=(0.3, 1.0, 0.5))
                        idx = len(objetos)
                        x = (idx - 2) * 2.2
                        new.apply_transform(translacao(x, 0.0, 0.0))
                        set_uniform_scale(new, 1.0)
                        new.set_angular_velocity([1, 0, 0], 0.8)  # Rotacao em X a 0.8 rad/s
                        objetos.append(new)
                    elif btn_add_prisma.clicked((mx, my)):
                        new = criar_prisma_hexagonal(raio=0.9, altura=1.8, cor=(0.9, 0.4, 0.3))
                        idx = len(objetos)
                        x = (idx - 2) * 2.2
                        new.apply_transform(translacao(x, 0.0, 0.0))
                        set_uniform_scale(new, 1.0)
                        new.set_angular_velocity([1, 1, 0], 1.2)  # Rotacao em XY a 1.2 rad/s
                        objetos.append(new)
                    elif btn_add_piramide.clicked((mx, my)):
                        new = criar_piramide(base=1.4, altura=1.8, cor=(1.0, 0.65, 0.2))
                        idx = len(objetos)
                        x = (idx - 2) * 2.2
                        new.apply_transform(translacao(x, 0.0, 0.0))
                        set_uniform_scale(new, 1.0)
                        new.set_angular_velocity([0, 0, 1], 1.5)  # Rotacao em Z a 1.5 rad/s
                        objetos.append(new)
                    elif btn_add_cilindro.clicked((mx, my)):
                        new = criar_cilindro(raio=0.8, altura=1.6, slices=18, cor=(0.8, 0.5, 0.2))
                        idx = len(objetos)
                        x = (idx - 2) * 2.2
                        new.apply_transform(translacao(x, 0.0, 0.0))
                        set_uniform_scale(new, 1.0)
                        new.set_angular_velocity([1, 1, 1], 0.9)  # Rotacao em XYZ a 0.9 rad/s
                        objetos.append(new)
                    elif btn_orbital_scene.clicked((mx, my)):
                        # Limpar cena e criar cubo central + pirâmide orbitante
                        objetos.clear()
                        selected = None
                        
                        # Cubo central (estático ou com rotação própria)
                        cubo_central = criar_cubo(1.5, cor=(0.2, 0.8, 1.0))
                        cubo_central.set_angular_velocity([0, 1, 0], 0.5)
                        objetos.append(cubo_central)
                        
                        # Pirâmide orbitante
                        piramide_orbitante = criar_piramide(base=1.0, altura=1.5, cor=(1.0, 0.65, 0.2))
                        piramide_orbitante.set_angular_velocity([1, 0, 0], 1.5)  # Gira sobre si mesma
                        piramide_orbitante.set_orbital_motion(
                            center_pos=[0, 0, 0],  # Centro do cubo
                            radius=4.0,  # Distancia de orbita
                            orbital_speed_rad_s=0.5,  # Velocidade de orbita
                            orbital_axis=[0, 1, 0]  # Orbita no plano horizontal (em torno do Y)
                        )
                        objetos.append(piramide_orbitante)
                    elif btn_mode_translate.clicked((mx, my)):
                        transform_mode = "TRANSLATE"
                    elif btn_mode_rotate.clicked((mx, my)):
                        transform_mode = "ROTATE"
                    elif btn_mode_scale.clicked((mx, my)):
                        transform_mode = "SCALE"
                    elif btn_plane_xy.clicked((mx, my)):
                        drag_plane = "XY"
                    elif btn_plane_xz.clicked((mx, my)):
                        drag_plane = "XZ"
                    elif btn_plane_yz.clicked((mx, my)):
                        drag_plane = "YZ"
                    elif btn_render_wire.clicked((mx, my)):
                        render_mode = "WIREFRAME"
                    elif btn_render_filled.clicked((mx, my)):
                        render_mode = "FILLED"
                    elif btn_toggle_auto_rotate.clicked((mx, my)):
                        auto_rotate_enabled = not auto_rotate_enabled
                        btn_toggle_auto_rotate.text = "Rotação: Ativada" if auto_rotate_enabled else "Rotação: Desativada"
                else:
                    # clicks on scene area -> try select object under cursor
                    best = None
                    best_d = 9999
                    for obj in objetos:
                        center = obj.model_matrix[:3, 3]
                        proj = project_to_screen(center)
                        if proj is None:
                            continue
                        d = np.hypot(proj[0] - mx, proj[1] - my)
                        if d < best_d:
                            best_d = d
                            best = obj
                    if best is not None and best_d < 32:
                        selected = best
                        dragging = True
                        last_mouse = np.array([mx, my], dtype=float)
                        if transform_mode == "TRANSLATE":
                            origin, direction = screen_ray(mx, my)
                            if drag_plane == "XY":
                                drag_plane_value = selected.model_matrix[2, 3]
                            elif drag_plane == "XZ":
                                drag_plane_value = selected.model_matrix[1, 3]
                            else:
                                drag_plane_value = selected.model_matrix[0, 3]

                            hit = intersect_ray_plane(origin, direction, drag_plane, drag_plane_value)
                            if hit is None:
                                hit = selected.model_matrix[:3, 3]
                            obj_pos = selected.model_matrix[:3, 3]
                            grab_offset = obj_pos - hit
                    else:
                        selected = None
                        dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging and selected is not None:
                    mx, my = event.pos
                    if transform_mode == "TRANSLATE":
                        origin, direction = screen_ray(mx, my)
                        hit = intersect_ray_plane(origin, direction, drag_plane, drag_plane_value)
                        if hit is not None:
                            new_pos = hit + grab_offset
                            selected.model_matrix[0, 3] = new_pos[0]
                            selected.model_matrix[1, 3] = new_pos[1]
                            selected.model_matrix[2, 3] = new_pos[2]
                    elif transform_mode == "ROTATE" and last_mouse is not None:
                        dx = mx - last_mouse[0]
                        dy = my - last_mouse[1]
                        selected.rotate_quaternion([0, 1, 0], dx * 0.01)
                        selected.rotate_quaternion([1, 0, 0], dy * 0.01)
                    elif transform_mode == "SCALE" and last_mouse is not None:
                        dy = my - last_mouse[1]
                        current_scale = get_scale_value(selected)
                        scale_factor = 1.0 - dy * 0.01
                        set_uniform_scale(selected, current_scale * scale_factor)

                    last_mouse = np.array([mx, my], dtype=float)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
                last_mouse = None
                # keep selected for possible future operations

        # Render scene first, then draw UI on top so UI isn't cleared by renderer
        renderizador.render(screen, objetos, camera, background=(12, 12, 20), render_mode=render_mode)

        # selected marker
        if selected is not None:
            center = selected.model_matrix[:3, 3]
            p = project_to_screen(center)
            if p is not None:
                pygame.draw.circle(screen, (255, 220, 80), p, 8, 1)

        # draw left sidebar on top
        pygame.draw.rect(screen, (18, 18, 24), (0, 0, sidebar_w, height))

        mode_text = font.render(f"Plano: {drag_plane} (1/2/3)", True, (220, 220, 220))
        screen.blit(mode_text, (margin_x, start_y + 6 * (btn_h + btn_gap) + 6))
        hint_text = font.render(f"Modo atual: {transform_mode}", True, (210, 210, 210))
        screen.blit(hint_text, (margin_x, start_y + 6 * (btn_h + btn_gap) + 30))

        btn_add_cube.draw(screen)
        btn_add_sphere.draw(screen)
        btn_add_prisma.draw(screen)
        btn_add_piramide.draw(screen)
        btn_add_cilindro.draw(screen)
        btn_orbital_scene.draw(screen)
        btn_mode_translate.draw(screen, active=(transform_mode == "TRANSLATE"))
        btn_mode_rotate.draw(screen, active=(transform_mode == "ROTATE"))
        btn_mode_scale.draw(screen, active=(transform_mode == "SCALE"))
        btn_plane_xy.draw(screen, active=(drag_plane == "XY"))
        btn_plane_xz.draw(screen, active=(drag_plane == "XZ"))
        btn_plane_yz.draw(screen, active=(drag_plane == "YZ"))
        btn_render_wire.draw(screen, active=(render_mode == "WIREFRAME"))
        btn_render_filled.draw(screen, active=(render_mode == "FILLED"))
        btn_toggle_auto_rotate.draw(screen, active=auto_rotate_enabled)

        # Fixed status panel at the bottom of sidebar for key hints.
        info_h = 74
        info_rect = pygame.Rect(8, height - info_h - 8, sidebar_w - 16, info_h)
        pygame.draw.rect(screen, (28, 28, 36), info_rect)
        pygame.draw.rect(screen, (120, 120, 150), info_rect, 1)
        delete_hint = font.render("Excluir objeto: tecla Delete", True, (250, 250, 250))
        screen.blit(delete_hint, (info_rect.x + 8, info_rect.y + 10))
        key_hint = font.render("Plano: 1=XY  2=XZ  3=YZ", True, (220, 220, 220))
        screen.blit(key_hint, (info_rect.x + 8, info_rect.y + 34))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
