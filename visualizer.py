"""
visualizer.py  ─  Second pygame window with two panels:
  LEFT  : State-Space Tree  — player move history as a branching tree
  RIGHT : A* Search Space   — live 5×5 grid showing enemy A* paths each move
"""
import pygame
import math

# ── Panel / layout constants ──────────────────────────────────────
VIS_W       = 900
VIS_H       = 620
PANEL_W     = VIS_W // 2          # 450 each
DIVIDER     = 3

# ── Colours ───────────────────────────────────────────────────────
CV_BG           = (10,  8, 20)
CV_PANEL_BG     = (14, 11, 26)
CV_DIVIDER      = (50, 45, 80)
CV_TITLE        = (200, 195, 255)
CV_SUBTITLE     = (110, 100, 160)
CV_NODE_PLAYER  = (80, 220, 120)    # green  — player node
CV_NODE_ENEMY1  = (220,  60,  60)   # red
CV_NODE_ENEMY2  = (220, 100, 200)   # pink
CV_NODE_GOAL    = (255, 200,  50)   # gold — goal reached
CV_NODE_LOSE    = (220,  60,  60)   # red  — caught
CV_EDGE         = (70,  65, 110)
CV_EDGE_ACTIVE  = (130, 120, 200)
CV_GRID_WALL    = (45,  40, 70)
CV_GRID_FLOOR   = (22,  18, 38)
CV_GRID_FLOOR2  = (28,  24, 46)
CV_GRID_LINE    = (35,  30, 55)
CV_ASTAR_OPEN   = (60, 120, 220)    # A* open-set cells
CV_ASTAR_CLOSED = (40,  80, 160)
CV_PATH_E1      = (220,  60,  60)
CV_PATH_E2      = (220, 100, 200)
CV_PATH_PLAYER  = (80, 220, 120)
CV_CELL_PLAYER  = (80, 220, 120)
CV_CELL_ENEMY1  = (220,  60,  60)
CV_CELL_ENEMY2  = (220, 100, 200)
CV_CELL_GOAL    = (255, 200,  50)
CV_LABEL        = (200, 195, 255)
CV_LEGEND_BG    = (20, 16, 36)

# ── Mini-grid layout (right panel) ────────────────────────────────
MINI_CELL       = 52          # px per cell for 5×5 grid
MINI_ROWS       = 5
MINI_COLS       = 5
MINI_GRID_W     = MINI_CELL * MINI_COLS   # 260
MINI_GRID_H     = MINI_CELL * MINI_ROWS   # 260


# ─────────────────────────────────────────────────────────────────
class StateSpaceVis:
    """
    Renders the state-space TREE in the left panel.

    Tree structure:
      - Root  = initial player position
      - Each child = a position the player moved to
      - Branches never collapse; every move adds a new leaf
      - Node colour = player pos cell; edges = move direction
      - Latest node pulsates; terminal nodes (win/lose) coloured specially
    """

    NODE_R   = 14
    LEVEL_H  = 60      # vertical gap between tree levels
    MIN_XGAP = 38      # minimum horizontal gap between siblings

    def __init__(self):
        self.nodes  = []   # list of {id, parent_id, pos, label, state}
        self.next_id = 0
        self._root_id = None

    def reset(self, start_pos):
        self.nodes   = []
        self.next_id = 0
        self._add_node(None, start_pos, "START", "playing")

    def _add_node(self, parent_id, pos, label, state):
        nid = self.next_id
        self.next_id += 1
        self.nodes.append({
            "id":        nid,
            "parent_id": parent_id,
            "pos":       pos,
            "label":     label,
            "state":     state,   # "playing" | "win" | "lose"
            "children":  [],
        })
        if parent_id is not None:
            self.nodes[parent_id]["children"].append(nid)
        else:
            self._root_id = nid
        return nid

    def record_move(self, new_pos, state):
        """Call every time the player successfully moves."""
        if not self.nodes:
            return
        parent_id = self.next_id - 1   # last added node is the current node
        self._add_node(parent_id, new_pos, str(new_pos), state)

    # ── Layout  ───────────────────────────────────────────────────
    def _layout(self):
        """Assigns (x, y) pixel coords to every node using a simple
        bottom-up / top-down Reingold-Tilford-style pass."""
        if not self.nodes:
            return {}

        # Build depth map
        depth = {0: 0}
        order = [0]
        for n in self.nodes[1:]:
            depth[n["id"]] = depth[n["parent_id"]] + 1
            order.append(n["id"])

        # Group by depth
        by_depth = {}
        for nid in order:
            d = depth[nid]
            by_depth.setdefault(d, []).append(nid)

        # Assign x positions level by level
        coords = {}
        max_depth = max(by_depth.keys())
        # panel usable width (with padding)
        usable_w = PANEL_W - 40

        for d, level_nodes in by_depth.items():
            n = len(level_nodes)
            if n == 1:
                xs = [PANEL_W // 2]
            else:
                gap = max(self.MIN_XGAP, usable_w // (n + 1))
                total = gap * (n - 1)
                start_x = max(self.NODE_R + 10, PANEL_W // 2 - total // 2)
                xs = [start_x + i * gap for i in range(n)]

            # Clamp to panel
            for i, nid in enumerate(level_nodes):
                x = min(max(xs[i], self.NODE_R + 10), PANEL_W - self.NODE_R - 10)
                y = 80 + d * self.LEVEL_H
                coords[nid] = (x, y)

        return coords

    # ── Draw ──────────────────────────────────────────────────────
    def draw(self, surf, font_sm, font_xs, tick, offset_x=0):
        coords = self._layout()
        if not coords:
            return

        # Edges first
        for n in self.nodes:
            if n["parent_id"] is not None:
                px, py = coords[n["parent_id"]]
                cx, cy = coords[n["id"]]
                is_latest = (n["id"] == self.next_id - 1)
                col = CV_EDGE_ACTIVE if is_latest else CV_EDGE
                pygame.draw.line(surf, col,
                                 (px + offset_x, py),
                                 (cx + offset_x, cy), 2)
                # Arrow tip
                angle = math.atan2(cy - py, cx - px)
                tip_x = cx + offset_x
                tip_y = cy
                al, aw = 7, 4
                for sign in (-1, 1):
                    ax = tip_x - al * math.cos(angle) + sign * aw * math.sin(angle)
                    ay = tip_y - al * math.sin(angle) - sign * aw * math.cos(angle)
                    pygame.draw.line(surf, col, (tip_x, tip_y), (int(ax), int(ay)), 1)

        # Nodes
        for n in self.nodes:
            cx, cy = coords[n["id"]]
            cx += offset_x
            is_latest = (n["id"] == self.next_id - 1)
            pulse = 0.5 + 0.5 * math.sin(tick * 0.005) if is_latest else 0
            r = self.NODE_R + int(pulse * 3)

            # Node fill colour
            if n["state"] == "win":
                fill = CV_NODE_GOAL
            elif n["state"] == "lose":
                fill = CV_NODE_LOSE
            else:
                fill = CV_NODE_PLAYER

            # Glow ring for latest
            if is_latest:
                glow_surf = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*fill, 60), (r * 2, r * 2), r * 2)
                surf.blit(glow_surf, (cx - r * 2, cy - r * 2))

            pygame.draw.circle(surf, fill, (cx, cy), r)
            pygame.draw.circle(surf, (255, 255, 255), (cx, cy), r, 1)

            # Label: grid coord
            label = str(n["pos"])
            lbl = font_xs.render(label, True, (20, 15, 35))
            surf.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))

            # Move number above node
            move_lbl = font_xs.render(f"#{n['id']}", True, CV_SUBTITLE)
            surf.blit(move_lbl, (cx - move_lbl.get_width() // 2, cy - r - 14))


# ─────────────────────────────────────────────────────────────────
class AStarSearchVis:
    """
    Renders the A* search-space panel on the right.

    Shows the 5×5 grid with:
      • Grid cells (walls / floor)
      • Enemy A* paths (coloured trails with step numbers)
      • Current positions of player + enemies + goal
      • Legend
    Updates every time a player move is recorded.
    """

    def __init__(self):
        self.grid        = None
        self.player_pos  = None
        self.goal_pos    = None
        self.enemy_data  = []   # list of {pos, path, color, name}
        self.move_number = 0

    def update(self, grid, player_pos, goal_pos, enemies):
        self.grid       = grid
        self.player_pos = player_pos
        self.goal_pos   = goal_pos
        self.enemy_data = [
            {
                "pos":   e.pos,
                "path":  list(e.path),
                "color": e.color,
                "name":  e.name,
            }
            for e in enemies
        ]
        self.move_number += 1

    def draw(self, surf, font_sm, font_xs, tick, offset_x=0):
        if self.grid is None:
            msg = font_sm.render("Make a move to see A* paths", True, CV_SUBTITLE)
            surf.blit(msg, (offset_x + 30, VIS_H // 2))
            return

        rows = len(self.grid)
        cols = len(self.grid[0])

        # Centre the mini-grid inside the right panel
        grid_w = MINI_CELL * cols
        grid_h = MINI_CELL * rows
        gx0 = offset_x + (PANEL_W - grid_w) // 2
        gy0 = 90

        # ── Draw base grid ────────────────────────────────────────
        for r in range(rows):
            for c in range(cols):
                x = gx0 + c * MINI_CELL
                y = gy0 + r * MINI_CELL
                if self.grid[r][c] == 1:
                    pygame.draw.rect(surf, CV_GRID_WALL, (x, y, MINI_CELL, MINI_CELL))
                    # brick lines
                    mid = MINI_CELL // 2
                    pygame.draw.line(surf, (60, 55, 90), (x+2, y+mid), (x+MINI_CELL-2, y+mid), 1)
                else:
                    col = CV_GRID_FLOOR if (r + c) % 2 == 0 else CV_GRID_FLOOR2
                    pygame.draw.rect(surf, col, (x, y, MINI_CELL, MINI_CELL))
                pygame.draw.rect(surf, CV_GRID_LINE, (x, y, MINI_CELL, MINI_CELL), 1)

                # Coord label inside each cell (very small)
                coord_lbl = font_xs.render(f"{r},{c}", True, (50, 45, 80))
                surf.blit(coord_lbl, (x + 2, y + MINI_CELL - 12))

        # ── Draw enemy A* paths ───────────────────────────────────
        path_colors = [CV_PATH_E1, CV_PATH_E2]
        for ei, ed in enumerate(self.enemy_data):
            path = ed["path"]
            color = ed["color"]
            for step, (pr, pc) in enumerate(path):
                if (pr, pc) == ed["pos"]:
                    continue   # skip enemy's current cell (drawn separately)
                x = gx0 + pc * MINI_CELL
                y = gy0 + pr * MINI_CELL
                alpha = max(20, 140 - step * 18)
                overlay = pygame.Surface((MINI_CELL, MINI_CELL), pygame.SRCALPHA)
                overlay.fill((*color, alpha // 4))
                surf.blit(overlay, (x, y))
                # step number
                step_lbl = font_xs.render(str(step), True, (*color[:3],))
                surf.blit(step_lbl, (x + MINI_CELL//2 - 4, y + 4))
                # dot on path
                cx_ = x + MINI_CELL // 2
                cy_ = y + MINI_CELL // 2
                pygame.draw.circle(surf, color, (cx_, cy_), 4)

            # Draw path line
            if len(path) > 1:
                pts = [(gx0 + c * MINI_CELL + MINI_CELL//2,
                        gy0 + r * MINI_CELL + MINI_CELL//2) for r, c in path]
                pygame.draw.lines(surf, (*color[:3],), False, pts, 2)

        # ── Goal ─────────────────────────────────────────────────
        gr, gc = self.goal_pos
        gx = gx0 + gc * MINI_CELL + MINI_CELL // 2
        gy_ = gy0 + gr * MINI_CELL + MINI_CELL // 2
        pulse = 0.5 + 0.5 * math.sin(tick * 0.004)
        gsz = int(8 + pulse * 3)
        pts = [(gx, gy_-gsz), (gx+gsz, gy_), (gx, gy_+gsz), (gx-gsz, gy_)]
        pygame.draw.polygon(surf, CV_CELL_GOAL, pts)
        pygame.draw.polygon(surf, (255, 255, 200), pts, 1)
        gl = font_xs.render("G", True, (20, 15, 10))
        surf.blit(gl, (gx - gl.get_width()//2, gy_ - gl.get_height()//2))

        # ── Enemies ───────────────────────────────────────────────
        for ei, ed in enumerate(self.enemy_data):
            er, ec = ed["pos"]
            ex = gx0 + ec * MINI_CELL + MINI_CELL // 2
            ey = gy0 + er * MINI_CELL + MINI_CELL // 2
            pulse = 0.5 + 0.5 * math.sin(tick * 0.005 + ei * 2)
            er_sz = int(10 + pulse * 2)
            pygame.draw.circle(surf, ed["color"], (ex, ey), er_sz)
            pygame.draw.circle(surf, (255, 255, 255), (ex, ey), er_sz, 1)
            el = font_xs.render(f"E{ei+1}", True, (20, 15, 10))
            surf.blit(el, (ex - el.get_width()//2, ey - el.get_height()//2))

        # ── Player ────────────────────────────────────────────────
        pr_, pc_ = self.player_pos
        px = gx0 + pc_ * MINI_CELL + MINI_CELL // 2
        py = gy0 + pr_ * MINI_CELL + MINI_CELL // 2
        pulse = 0.5 + 0.5 * math.sin(tick * 0.006)
        pr_sz = int(11 + pulse * 2)
        # glow
        glow_s = pygame.Surface((pr_sz*4, pr_sz*4), pygame.SRCALPHA)
        pygame.draw.circle(glow_s, (*CV_CELL_PLAYER, 50), (pr_sz*2, pr_sz*2), pr_sz*2)
        surf.blit(glow_s, (px - pr_sz*2, py - pr_sz*2))
        pygame.draw.circle(surf, CV_CELL_PLAYER, (px, py), pr_sz)
        pl = font_xs.render("P", True, (20, 15, 10))
        surf.blit(pl, (px - pl.get_width()//2, py - pl.get_height()//2))

        # ── Move counter + enemy distances ────────────────────────
        info_y = gy0 + grid_h + 16
        move_lbl = font_sm.render(f"After move #{self.move_number}", True, CV_TITLE)
        surf.blit(move_lbl, (offset_x + (PANEL_W - move_lbl.get_width()) // 2, info_y))

        for ei, ed in enumerate(self.enemy_data):
            dist = abs(ed["pos"][0] - self.player_pos[0]) + abs(ed["pos"][1] - self.player_pos[1])
            path_len = max(0, len(ed["path"]) - 1)
            txt = font_xs.render(
                f"{ed['name']}: dist={dist}  path_steps={path_len}",
                True, ed["color"]
            )
            surf.blit(txt, (offset_x + 16, info_y + 22 + ei * 16))

        # ── Legend ────────────────────────────────────────────────
        leg_y = info_y + 22 + len(self.enemy_data) * 16 + 10
        items = [
            (CV_CELL_PLAYER, "P = Player"),
            (CV_CELL_GOAL,   "G = Goal"),
            (CV_PATH_E1,     "E1 path (A*)"),
            (CV_PATH_E2,     "E2 path (A*)"),
            (CV_GRID_WALL,   "■ = Wall"),
        ]
        for i, (col, txt) in enumerate(items):
            ix = offset_x + 16 + (i % 3) * 138
            iy = leg_y + (i // 3) * 16
            pygame.draw.rect(surf, col, (ix, iy, 10, 10))
            lt = font_xs.render(txt, True, CV_SUBTITLE)
            surf.blit(lt, (ix + 14, iy - 1))


# ─────────────────────────────────────────────────────────────────
class VisualizerWindow:
    """
    Manages the second pygame window.
    Call .update() after every player move.
    Call .draw() every frame (pass in game tick).
    Call .handle_events() to keep the window responsive.
    """

    def __init__(self):
        # We open the window lazily on first update so the game can init first
        self._screen  = None
        self._clock   = None
        self._font_sm = None
        self._font_xs = None
        self._font_ti = None

        self.ss_vis   = StateSpaceVis()
        self.as_vis   = AStarSearchVis()
        self._tick    = 0
        self._active  = False

    def _ensure_init(self):
        if self._screen is not None:
            return
        self._screen  = pygame.display.set_mode((VIS_W, VIS_H), flags=0, display=0)
        # We can't use set_mode for a second window in standard pygame —
        # instead we'll draw onto a Surface and blit to the already-open display.
        # The caller (main.py) owns display; we own a plain Surface.
        self._surf    = pygame.Surface((VIS_W, VIS_H))
        self._clock   = pygame.time.Clock()
        self._font_sm = pygame.font.SysFont("consolas", 13, bold=True)
        self._font_xs = pygame.font.SysFont("consolas", 11)
        self._font_ti = pygame.font.SysFont("consolas", 16, bold=True)
        self._active  = True

    def init_standalone(self, start_pos):
        """Call once after pygame.init() with the dedicated vis display."""
        self._surf    = pygame.Surface((VIS_W, VIS_H))
        self._font_sm = pygame.font.SysFont("consolas", 13, bold=True)
        self._font_xs = pygame.font.SysFont("consolas", 11)
        self._font_ti = pygame.font.SysFont("consolas", 16, bold=True)
        self._active  = True
        self.ss_vis.reset(start_pos)

    def reset(self, start_pos):
        self.ss_vis.reset(start_pos)
        self.as_vis.move_number = 0
        self.as_vis.grid = None

    def record_move(self, new_pos, game_state, grid, goal_pos, enemies):
        """
        Call from Game.move_player() after every successful player move.
        game_state: "playing" | "win" | "lose"
        """
        self.ss_vis.record_move(new_pos, game_state)
        self.as_vis.update(grid, new_pos, goal_pos, enemies)

    def draw(self, screen, tick):
        """
        Draw the visualiser onto `screen` (a pygame.Surface).
        In standalone mode this IS the pygame display surface.
        """
        self._tick = tick
        surf = screen   # draw directly onto the provided surface

        surf.fill(CV_BG)

        # ── Left panel background ─────────────────────────────────
        pygame.draw.rect(surf, CV_PANEL_BG, (0, 0, PANEL_W, VIS_H))

        # ── Right panel background ────────────────────────────────
        pygame.draw.rect(surf, CV_PANEL_BG, (PANEL_W + DIVIDER, 0, PANEL_W - DIVIDER, VIS_H))

        # ── Divider ───────────────────────────────────────────────
        pygame.draw.rect(surf, CV_DIVIDER, (PANEL_W, 0, DIVIDER, VIS_H))

        # ── Panel titles ──────────────────────────────────────────
        lp_title = self._font_ti.render("STATE SPACE TREE", True, CV_TITLE)
        surf.blit(lp_title, (PANEL_W // 2 - lp_title.get_width() // 2, 14))
        lp_sub = self._font_xs.render("Each node = player position after move", True, CV_SUBTITLE)
        surf.blit(lp_sub, (PANEL_W // 2 - lp_sub.get_width() // 2, 34))
        lp_sub2 = self._font_xs.render("Green=playing  Gold=win  Red=caught", True, CV_SUBTITLE)
        surf.blit(lp_sub2, (PANEL_W // 2 - lp_sub2.get_width() // 2, 50))

        rp_title = self._font_ti.render("A* SEARCH SPACE", True, CV_TITLE)
        surf.blit(rp_title, (PANEL_W + DIVIDER + (PANEL_W - rp_title.get_width()) // 2, 14))
        rp_sub = self._font_xs.render("Enemy A* paths updated after each player move", True, CV_SUBTITLE)
        surf.blit(rp_sub, (PANEL_W + DIVIDER + (PANEL_W - rp_sub.get_width()) // 2, 34))

        # ── Separator lines under titles ──────────────────────────
        pygame.draw.line(surf, CV_DIVIDER, (10, 68), (PANEL_W - 10, 68), 1)
        pygame.draw.line(surf, CV_DIVIDER, (PANEL_W + DIVIDER + 10, 68), (VIS_W - 10, 68), 1)

        # ── Content ───────────────────────────────────────────────
        self.ss_vis.draw(surf, self._font_sm, self._font_xs, tick, offset_x=0)
        self.as_vis.draw(surf, self._font_sm, self._font_xs, tick, offset_x=PANEL_W + DIVIDER)
