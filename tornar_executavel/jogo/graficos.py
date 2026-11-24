# ==============================================================================
# UTILITÁRIOS GRÁFICOS: FONTES, TEXTO, ÍCONES, BOTÕES E TRANSPARÊNCIA
# ==============================================================================
import pygame

from . import config as C


class FontManager:
    _fonts = {}

    @classmethod
    def get(cls, size: int, bold: bool = False) -> pygame.font.Font:
        key = (size, bold)
        if key not in cls._fonts:
            try:
                cls._fonts[key] = pygame.font.SysFont("arial", size, bold=bold)
            except Exception:
                cls._fonts[key] = pygame.font.Font(None, size)
        return cls._fonts[key]


def alpha_rect(surf, color_rgba, rect, radius=0):
    """Retângulo com transparência real (pygame.draw ignora o alfa em superfícies sem SRCALPHA)."""
    rect = pygame.Rect(rect)
    tmp = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(tmp, color_rgba, tmp.get_rect(), border_radius=radius)
    surf.blit(tmp, rect.topleft)


def alpha_circle(surf, color_rgba, center, radius):
    radius = max(1, int(radius))
    tmp = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(tmp, color_rgba, (radius, radius), radius)
    surf.blit(tmp, (int(center[0]) - radius, int(center[1]) - radius))


def alpha_ellipse(surf, color_rgba, rect):
    rect = pygame.Rect(rect)
    tmp = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(tmp, color_rgba, tmp.get_rect())
    surf.blit(tmp, rect.topleft)


def alpha_polygon(surf, color_rgba, pontos):
    xs = [p[0] for p in pontos]
    ys = [p[1] for p in pontos]
    x0, y0 = min(xs), min(ys)
    w, h = max(xs) - x0 + 1, max(ys) - y0 + 1
    tmp = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(tmp, color_rgba, [(x - x0, y - y0) for x, y in pontos])
    surf.blit(tmp, (x0, y0))


class UIUtils:
    @staticmethod
    def draw_rounded_rect(surf, rect, color, radius=8, border_width=0, border_color=None):
        pygame.draw.rect(surf, color, rect, border_radius=radius)
        if border_width > 0 and border_color:
            pygame.draw.rect(surf, border_color, rect, width=border_width, border_radius=radius)

    @staticmethod
    def wrap_lines(text, font, width):
        """Quebra o texto em linhas que cabem na largura. '\\n' força quebra; '' = linha em branco."""
        lines = []
        for paragraph in text.split("\n"):
            if not paragraph.strip():
                lines.append("")
                continue
            current = []
            for word in paragraph.split(" "):
                if not word:
                    continue
                trial = " ".join(current + [word])
                if font.size(trial)[0] <= width or not current:
                    current.append(word)
                else:
                    lines.append(" ".join(current))
                    current = [word]
            if current:
                lines.append(" ".join(current))
        return lines

    @staticmethod
    def text_height(text, width, font, line_spacing=4):
        lines = UIUtils.wrap_lines(text, font, width)
        h = 0
        for line in lines:
            h += font.get_linesize() // 2 if not line else font.get_linesize() + line_spacing
        return h

    @staticmethod
    def draw_text(surf, text, rect, font, color, line_spacing=4, center=False):
        """Desenha texto com quebra de linha. Retorna a altura usada."""
        if not text:
            return 0
        rect = pygame.Rect(rect)
        y = rect.y
        for line in UIUtils.wrap_lines(text, font, rect.width):
            if not line:
                y += font.get_linesize() // 2
                continue
            ts = font.render(line, True, color)
            x = rect.x + (rect.width - ts.get_width()) // 2 if center else rect.x
            surf.blit(ts, (x, y))
            y += font.get_linesize() + line_spacing
        return y - rect.y

    @staticmethod
    def draw_icon(surf, icon_type, pos, size, color):
        cx, cy = pos
        hs = size // 2
        if icon_type == "magnifier":
            pygame.draw.circle(surf, color, (cx - 3, cy - 3), hs - 2, 2)
            pygame.draw.line(surf, color, (cx + 1, cy + 1), (cx + hs, cy + hs), 3)
        elif icon_type == "document":
            pygame.draw.rect(surf, color, (cx - hs + 2, cy - hs, size - 4, size), 2, 2)
            pygame.draw.line(surf, color, (cx - hs + 6, cy - hs + 6), (cx + hs - 6, cy - hs + 6), 2)
            pygame.draw.line(surf, color, (cx - hs + 6, cy - hs + 12), (cx + hs - 6, cy - hs + 12), 2)
        elif icon_type == "speech":
            pygame.draw.rect(surf, color, (cx - hs, cy - hs, size, size - 4), 2, 3)
            pygame.draw.polygon(surf, color, [(cx - 4, cy + hs - 4), (cx - 8, cy + hs), (cx + 2, cy + hs - 4)])
        elif icon_type == "registry":
            pygame.draw.rect(surf, color, (cx - hs, cy - hs, size, size), 2, 2)
            pygame.draw.line(surf, color, (cx - 4, cy - 2), (cx, cy + 4), 2)
            pygame.draw.line(surf, color, (cx, cy + 4), (cx + 6, cy - 4), 2)
        elif icon_type == "check":
            pygame.draw.line(surf, color, (cx - 6, cy), (cx - 2, cy + 6), 3)
            pygame.draw.line(surf, color, (cx - 2, cy + 6), (cx + 8, cy - 6), 3)
        elif icon_type == "cross":
            pygame.draw.line(surf, color, (cx - 6, cy - 6), (cx + 6, cy + 6), 3)
            pygame.draw.line(surf, color, (cx - 6, cy + 6), (cx + 6, cy - 6), 3)
        elif icon_type == "trophy":
            pygame.draw.rect(surf, color, (cx - 6, cy - hs + 2, 12, 9), border_bottom_left_radius=6,
                             border_bottom_right_radius=6)
            pygame.draw.circle(surf, color, (cx - 7, cy - hs + 5), 3, 1)
            pygame.draw.circle(surf, color, (cx + 7, cy - hs + 5), 3, 1)
            pygame.draw.line(surf, color, (cx, cy - hs + 10), (cx, cy + 3), 2)
            pygame.draw.rect(surf, color, (cx - 5, cy + 3, 10, 3))
        elif icon_type == "sun":
            pygame.draw.circle(surf, color, (cx, cy), hs - 4)
            for i in range(8):
                v = pygame.math.Vector2(1, 0).rotate(i * 45)
                pygame.draw.line(surf, color, (cx + v.x * (hs - 2), cy + v.y * (hs - 2)),
                                 (cx + v.x * (hs + 2), cy + v.y * (hs + 2)), 2)
        elif icon_type == "moon":
            pygame.draw.circle(surf, color, (cx, cy), hs - 2)
            pygame.draw.circle(surf, C.COLOR_PANEL_BG, (cx + 5, cy - 3), hs - 3)
        elif icon_type == "lock":
            pygame.draw.rect(surf, color, (cx - 6, cy - 1, 12, 9), border_radius=2)
            pygame.draw.circle(surf, color, (cx, cy - 2), 4, 2)
        else:
            pygame.draw.circle(surf, color, (cx, cy), hs - 2, 2)


class Button:
    def __init__(self, rect, text, bg_color=C.COLOR_PANEL_ALT, hover_color=C.COLOR_PANEL_BORDER,
                 text_color=C.COLOR_TEXT_LIGHT, font_size=16, align="center"):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.align = align
        self.is_hovered = False
        self.enabled = True

    def draw(self, surf, mouse_pos):
        self.is_hovered = self.enabled and self.rect.collidepoint(mouse_pos)
        color = self.hover_color if self.is_hovered else self.bg_color
        if not self.enabled:
            color = (40, 46, 52)
        UIUtils.draw_rounded_rect(surf, self.rect, color, radius=6, border_width=2,
                                  border_color=C.COLOR_ACCENT_GOLD if self.is_hovered else C.COLOR_PANEL_BORDER)
        tcolor = C.COLOR_ACCENT_GOLD if self.is_hovered else self.text_color
        if not self.enabled:
            tcolor = (110, 120, 130)
        font = FontManager.get(self.font_size, True)
        if self.align == "left":
            UIUtils.draw_text(surf, self.text, self.rect.inflate(-24, -14), font, tcolor, line_spacing=2)
        else:
            ts = font.render(self.text, True, tcolor)
            surf.blit(ts, ts.get_rect(center=self.rect.center))

    def clicked(self, event, mouse_pos):
        return (self.enabled and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(mouse_pos))


def is_left_click(event):
    return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
