import pygame
import math
import heapq
import random
import time
from typing import List, Tuple, Set, Dict, Optional
from enum import Enum

pygame.init()

# Constants
WIDTH, HEIGHT = 1400, 900
GRID_SIZE = 20
ROWS = (HEIGHT - 180) // GRID_SIZE
COLS = WIDTH // GRID_SIZE

BACKGROUND = (10, 10, 20)
SURFACE = (15, 15, 30)
BORDER = (40, 40, 70)
TEXT_PRIMARY = (255, 255, 255)
TEXT_SECONDARY = (200, 200, 220)

# Algorithm Colors - Neon Theme
START_NODE = (0, 255, 153)      
END_NODE = (255, 107, 107)      
PATH_COLOR = (77, 150, 255)    
OPEN_NODE = (255, 217, 61)     
CLOSED_NODE = (157, 78, 221)    
WALL_COLOR = (44, 44, 44)      
EMPTY_NODE = (249, 249, 249)    
EXPLORED_NODE = (100, 200, 255) 

# Button Colors
BUTTON_PRIMARY = (77, 150, 255)
BUTTON_HOVER = (100, 170, 255)
BUTTON_ACTIVE = (50, 120, 220)
BUTTON_DANGER = (255, 107, 107)
BUTTON_DANGER_HOVER = (255, 130, 130)
BUTTON_SUCCESS = (0, 255, 153)

class Algorithm(Enum):
    A_STAR = "A* Algorithm"
    DIJKSTRA = "Dijkstra's Algorithm"
    BFS = "Breadth-First Search"
    DFS = "Depth-First Search"

class ButtonState(Enum):
    NORMAL = 0
    HOVER = 1
    PRESSED = 2
    DISABLED = 3

class Button:
    """Professional button with glow effect"""
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 callback=None, is_danger: bool = False, is_success: bool = False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.is_danger = is_danger
        self.is_success = is_success
        self.state = ButtonState.NORMAL
        self.enabled = True
        self.font = pygame.font.SysFont('Arial', 13, bold=True)
        self.glow_intensity = 0
        self.press_timer = 0  # Add timer for press animation
        
    def draw(self, surface: pygame.Surface):
        """Draw button with glow effect"""
        if not self.enabled:
            color = (80, 80, 80)
            text_color = (120, 120, 120)
            glow_color = (40, 40, 40)
        elif self.state == ButtonState.PRESSED:
            if self.is_danger:
                color = (220, 80, 80)
            elif self.is_success:
                color = (0, 220, 140)
            else:
                color = BUTTON_ACTIVE
            text_color = TEXT_PRIMARY
            glow_color = (150, 190, 255)
            self.glow_intensity = 15
        elif self.state == ButtonState.HOVER:
            if self.is_danger:
                color = BUTTON_DANGER_HOVER
                glow_color = (255, 150, 150)
            elif self.is_success:
                color = (50, 255, 180)
                glow_color = (100, 255, 200)
            else:
                color = BUTTON_HOVER
                glow_color = (150, 190, 255)
            text_color = TEXT_PRIMARY
            self.glow_intensity = min(10, self.glow_intensity + 1)
        else:
            if self.is_danger:
                color = BUTTON_DANGER
                glow_color = (200, 80, 80)
            elif self.is_success:
                color = START_NODE
                glow_color = (100, 255, 180)
            else:
                color = BUTTON_PRIMARY
                glow_color = (100, 150, 220)
            text_color = TEXT_PRIMARY
            self.glow_intensity = max(0, self.glow_intensity - 1)
        
        # Draw glow effect
        if self.glow_intensity > 0:
            glow_rect = self.rect.inflate(self.glow_intensity * 2, self.glow_intensity * 2)
            pygame.draw.rect(surface, glow_color, glow_rect, 1)
        
        # Draw button background
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        
        # Draw button border
        pygame.draw.rect(surface, BORDER, self.rect, 2, border_radius=8)
        
        # Draw text
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        """Check if button was clicked"""
        return self.rect.collidepoint(pos) and self.enabled
        
    def update_state(self, pos: Tuple[int, int]):
        """Update button state based on mouse position"""
        if not self.enabled:
            self.state = ButtonState.DISABLED
        elif self.press_timer > 0:  # Keep pressed state for animation
            self.press_timer -= 1
            self.state = ButtonState.PRESSED
        elif self.rect.collidepoint(pos):
            self.state = ButtonState.HOVER
        else:
            self.state = ButtonState.NORMAL
    
    def trigger_press(self):
        """Trigger button press animation and callback"""
        if self.enabled:
            self.press_timer = 5
            self.state = ButtonState.PRESSED
            if self.callback:
                self.callback()

class Dropdown:
    """Dropdown menu for algorithm selection"""
    def __init__(self, x: int, y: int, width: int, height: int, options: List[str]):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_option = options[0]
        self.is_open = False
        self.font = pygame.font.SysFont('Arial', 12)
        self.option_rects = []
        
    def draw(self, surface: pygame.Surface):
        """Draw dropdown menu"""
        # Draw main button
        pygame.draw.rect(surface, BUTTON_PRIMARY, self.rect, border_radius=6)
        pygame.draw.rect(surface, BORDER, self.rect, 2, border_radius=6)
        
        # Draw text
        text_surface = self.font.render(self.selected_option, True, TEXT_PRIMARY)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
        # Draw dropdown arrow
        arrow_size = 5
        arrow_x = self.rect.right - 15
        arrow_y = self.rect.centery
        if self.is_open:
            pygame.draw.polygon(surface, TEXT_PRIMARY, [
                (arrow_x, arrow_y - arrow_size),
                (arrow_x - arrow_size, arrow_y + arrow_size),
                (arrow_x + arrow_size, arrow_y + arrow_size)
            ])
        else:
            pygame.draw.polygon(surface, TEXT_PRIMARY, [
                (arrow_x - arrow_size, arrow_y - arrow_size),
                (arrow_x + arrow_size, arrow_y - arrow_size),
                (arrow_x, arrow_y + arrow_size)
            ])
        
        # Draw options if open
        if self.is_open:
            self.option_rects = []
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(
                    self.rect.x, 
                    self.rect.y + self.rect.height * (i + 1),
                    self.rect.width,
                    self.rect.height
                )
                self.option_rects.append(option_rect)
                
                # Draw option background
                color = BUTTON_HOVER if option == self.selected_option else BUTTON_PRIMARY
                pygame.draw.rect(surface, color, option_rect, border_radius=6)
                pygame.draw.rect(surface, BORDER, option_rect, 1, border_radius=6)
                
                # Draw option text
                option_text = self.font.render(option, True, TEXT_PRIMARY)
                option_text_rect = option_text.get_rect(center=option_rect.center)
                surface.blit(option_text, option_text_rect)
                
    def handle_event(self, event) -> bool:
        """Handle dropdown events, return True if selection changed"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return False
            elif self.is_open:
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(event.pos):
                        old_option = self.selected_option
                        self.selected_option = self.options[i]
                        self.is_open = False
                        return old_option != self.selected_option  # Return True only if changed
                self.is_open = False
        return False

class Node:
    """Grid node for pathfinding algorithms"""
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.x = col * GRID_SIZE
        self.y = row * GRID_SIZE + 180
        self.color = EMPTY_NODE
        self.neighbors = []
        self.is_wall = False
        self.is_start = False
        self.is_end = False
        self.g_score = float("inf")
        self.f_score = float("inf")
        self.came_from = None
        self.visited = False
        
    def get_pos(self) -> Tuple[int, int]:
        return self.row, self.col
        
    def reset(self):
        """Reset node to default state"""
        if not self.is_start and not self.is_end and not self.is_wall:
            self.color = EMPTY_NODE
            self.g_score = float("inf")
            self.f_score = float("inf")
            self.came_from = None
            self.visited = False
        
    def make_start(self):
        self.is_start = True
        self.is_end = False
        self.is_wall = False
        self.color = START_NODE
        
    def make_end(self):
        self.is_start = False
        self.is_end = True
        self.is_wall = False
        self.color = END_NODE
        
    def make_wall(self):
        if not self.is_start and not self.is_end:
            self.is_wall = True
            self.color = WALL_COLOR
            
    def make_open(self):
        if not self.is_start and not self.is_end:
            self.color = OPEN_NODE
            
    def make_closed(self):
        if not self.is_start and not self.is_end:
            self.color = CLOSED_NODE
            
    def make_path(self):
        if not self.is_start and not self.is_end:
            self.color = PATH_COLOR
            
    def make_explored(self):
        if not self.is_start and not self.is_end and not self.is_wall:
            self.color = EXPLORED_NODE
            
    def draw(self, win):
        """Draw node with smooth borders"""
        pygame.draw.rect(win, self.color, (self.x, self.y, GRID_SIZE, GRID_SIZE), border_radius=2)
        pygame.draw.rect(win, BORDER, (self.x, self.y, GRID_SIZE, GRID_SIZE), 1, border_radius=2)
        
    def update_neighbors(self, grid):
        """Find valid neighbors"""
        self.neighbors = []
        directions = [
            (self.row - 1, self.col),
            (self.row + 1, self.col),
            (self.row, self.col - 1),
            (self.row, self.col + 1),
        ]
        
        for row, col in directions:
            if 0 <= row < ROWS and 0 <= col < COLS and not grid[row][col].is_wall:
                self.neighbors.append(grid[row][col])
                
    def __lt__(self, other):
        return self.f_score < other.f_score


class PathFinderVisualizer:
    """Main application"""
    def __init__(self):
        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pathfinding Visualizer - Professional Edition")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont('Arial', 28, bold=True)
        self.font_subtitle = pygame.font.SysFont('Arial', 14)
        self.font_small = pygame.font.SysFont('Arial', 12)
        
        # Grid setup
        self.grid = self.make_grid()
        self.start_node = None
        self.end_node = None
        
        # State
        self.drawing_walls = False
        self.running_algorithm = False
        self.algorithm_finished = False
        self.animation_speed = 15
        self.path_length = 0
        self.nodes_explored = 0
        self.selected_algorithm = Algorithm.A_STAR
        
        # Setup buttons and dropdown
        self.setup_buttons()
        
    def setup_buttons(self):
        """Create UI buttons and dropdown"""
        button_y = 50
        button_height = 35
        button_spacing = 10
        
        self.buttons = {
            'start_algo': Button(20, button_y, 130, button_height, "▶ Start Algorithm", 
                               self.start_algorithm, is_success=True),
            'clear_board': Button(160, button_y, 120, button_height, "🗑 Clear Board", 
                                self.clear_board, is_danger=True),
            'random_maze': Button(290, button_y, 140, button_height, "🎲 Random Maze", 
                                self.generate_random_maze, is_success=True),
            'speed_up': Button(430, button_y, 100, button_height, "⚡ Speed +", 
                             self.speed_up),
            'speed_down': Button(540, button_y, 100, button_height, "🐢 Speed -", 
                               self.speed_down),
        }
        
        # Algorithm dropdown
        algorithm_options = [algo.value for algo in Algorithm]
        self.algorithm_dropdown = Dropdown(660, button_y, 150, button_height, algorithm_options)
        
    def make_grid(self) -> List[List[Node]]:
        """Create grid"""
        grid = []
        for row in range(ROWS):
            grid.append([])
            for col in range(COLS):
                grid[row].append(Node(row, col))
        return grid
        
    def draw_grid(self):
        """Draw grid lines"""
        for row in range(ROWS + 1):
            pygame.draw.line(self.win, BORDER, (0, row * GRID_SIZE + 180), 
                           (WIDTH, row * GRID_SIZE + 180), 1)
        for col in range(COLS + 1):
            pygame.draw.line(self.win, BORDER, (col * GRID_SIZE, 180), 
                           (col * GRID_SIZE, HEIGHT), 1)
            
    def draw_ui(self):
        """Draw professional UI panel"""
        # Background
        pygame.draw.rect(self.win, SURFACE, (0, 0, WIDTH, 180))
        pygame.draw.line(self.win, BORDER, (0, 180), (WIDTH, 180), 3)
        
        # Title
        title = self.font_title.render("Pathfinding Visualizer", True, TEXT_PRIMARY)
        self.win.blit(title, (20, 10))
        
        # Developer name
        dev_text = self.font_small.render("Created by Yash And Nishant", True, TEXT_SECONDARY)
        self.win.blit(dev_text, (WIDTH - 250, 15))
        
        # Draw buttons
        for button in self.buttons.values():
            button.draw(self.win)
            
        # Draw algorithm dropdown
        self.algorithm_dropdown.draw(self.win)
        
        # Status
        status_y = 100
        if self.running_algorithm:
            status_text = f"Status: Running {self.selected_algorithm.value}..."
            status_color = OPEN_NODE
        elif self.algorithm_finished:
            status_text = f"✓ Path Found! Length: {self.path_length} | Explored: {self.nodes_explored} nodes"
            status_color = START_NODE
        else:
            status_text = "Status: Ready - Left Click: Place Start/End & Draw Walls | Right Click: Erase"
            status_color = TEXT_SECONDARY
            
        status = self.font_small.render(status_text, True, status_color)
        self.win.blit(status, (20, status_y))
        
        # Instructions
        instructions = f"Speed: {self.animation_speed}x | Grid: {ROWS}x{COLS} | Algorithm: {self.selected_algorithm.value}"
        instr_text = self.font_small.render(instructions, True, TEXT_SECONDARY)
        self.win.blit(instr_text, (20, status_y + 25))
        
    def draw(self):
        """Draw everything"""
        self.win.fill(BACKGROUND)
        
        # Draw nodes
        for row in self.grid:
            for node in row:
                node.draw(self.win)
                
        # Draw grid
        self.draw_grid()
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.update()
        
    def get_clicked_node(self, pos: Tuple[int, int]) -> Optional[Node]:
        """Get node at mouse position"""
        x, y = pos
        
        if y < 180:
            return None
            
        row = (y - 180) // GRID_SIZE
        col = x // GRID_SIZE
        
        if 0 <= row < ROWS and 0 <= col < COLS:
            return self.grid[row][col]
        return None
        
    def reset_grid(self, keep_walls: bool = False):
        """Reset grid"""
        for row in self.grid:
            for node in row:
                if keep_walls:
                    if not node.is_wall:
                        node.reset()
                else:
                    node.reset()
                    node.is_wall = False
                    
        self.running_algorithm = False
        self.algorithm_finished = False
        self.path_length = 0
        self.nodes_explored = 0
        
        if self.start_node:
            self.start_node.make_start()
        if self.end_node:
            self.end_node.make_end()
            
    def clear_board(self):
        """Clear entire board - removes walls, start, and end nodes"""
        for row in self.grid:
            for node in row:
                node.is_start = False
                node.is_end = False
                node.is_wall = False
                node.color = EMPTY_NODE
                node.g_score = float("inf")
                node.f_score = float("inf")
                node.came_from = None
                node.visited = False
        
        self.start_node = None
        self.end_node = None
        self.running_algorithm = False
        self.algorithm_finished = False
        self.path_length = 0
        self.nodes_explored = 0
        print("✓ Board completely cleared")
        
    def start_algorithm(self):
        """Start selected algorithm"""
        if self.running_algorithm or self.algorithm_finished:
            print("✗ Algorithm already running or finished. Click 'Reset Path' first!")
            return
            
        if not self.start_node:
            print("✗ Please place a start node first!")
            return
            
        if not self.end_node:
            print("✗ Please place an end node first!")
            return
        
        for button in self.buttons.values():
            button.enabled = False
        
        if self.selected_algorithm == Algorithm.A_STAR:
            self.a_star_algorithm()
        elif self.selected_algorithm == Algorithm.DIJKSTRA:
            self.dijkstra_algorithm()
        elif self.selected_algorithm == Algorithm.BFS:
            self.bfs_algorithm()
        elif self.selected_algorithm == Algorithm.DFS:
            self.dfs_algorithm()
        
        for button in self.buttons.values():
            button.enabled = True
            
    def speed_up(self):
        """Increase speed"""
        self.animation_speed = min(50, self.animation_speed + 5)
        print(f"Speed: {self.animation_speed}x")
        
    def speed_down(self):
        """Decrease speed"""
        self.animation_speed = max(1, self.animation_speed - 5)
        print(f"Speed: {self.animation_speed}x")
        
    def generate_random_maze(self):
        """Generate random maze"""
        self.clear_board()
        
        # Generate random walls
        for row in self.grid:
            for node in row:
                if random.random() < 0.25:  # 25% chance of wall
                    node.make_wall()
        
        # Ensure start and end are placed
        if not self.start_node:
            start = self.grid[1][1]
            start.make_start()
            self.start_node = start
            
        if not self.end_node:
            end = self.grid[ROWS - 2][COLS - 2]
            end.make_end()
            self.end_node = end
        
        print("✓ Random maze generated")
    
    def heuristic(self, node1: Node, node2: Node) -> float:
        """Manhattan distance"""
        x1, y1 = node1.get_pos()
        x2, y2 = node2.get_pos()
        return abs(x1 - x2) + abs(y1 - y2)
        
    def reconstruct_path(self, current: Node):
        """Reconstruct path"""
        path_length = 0
        while current.came_from:
            current = current.came_from
            if not current.is_start:
                current.make_path()
                path_length += 1
            self.draw()
            self.clock.tick(self.animation_speed * 2)
            
        return path_length
        
    def a_star_algorithm(self):
        """A* algorithm"""
        if not self.start_node or not self.end_node:
            return False
            
        self.reset_grid(keep_walls=True)
        self.running_algorithm = True
        self.algorithm_finished = False
        
        self.start_node.g_score = 0
        self.start_node.f_score = self.heuristic(self.start_node, self.end_node)
        
        open_set = []
        heapq.heappush(open_set, (self.start_node.f_score, 0, self.start_node))
        open_set_hash = {self.start_node}
        
        counter = 0
        
        for row in self.grid:
            for node in row:
                node.update_neighbors(self.grid)
                
        while open_set:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                    
            current = heapq.heappop(open_set)[2]
            open_set_hash.remove(current)
            
            if current == self.end_node:
                self.path_length = self.reconstruct_path(current)
                self.algorithm_finished = True
                self.running_algorithm = False
                print(f"✓ A* Path found! Length: {self.path_length}, Nodes explored: {self.nodes_explored}")
                return True
                
            for neighbor in current.neighbors:
                temp_g_score = current.g_score + 1
                
                if temp_g_score < neighbor.g_score:
                    neighbor.came_from = current
                    neighbor.g_score = temp_g_score
                    neighbor.f_score = temp_g_score + self.heuristic(neighbor, self.end_node)
                    
                    if neighbor not in open_set_hash:
                        counter += 1
                        heapq.heappush(open_set, (neighbor.f_score, counter, neighbor))
                        open_set_hash.add(neighbor)
                        neighbor.make_open()
                        self.nodes_explored += 1
                        
            self.draw()
            self.clock.tick(self.animation_speed)
            
            if current != self.start_node:
                current.make_closed()
                
        self.running_algorithm = False
        self.algorithm_finished = True
        print("✗ A* No path found!")
        return False
        
    def dijkstra_algorithm(self):
        """Dijkstra's algorithm"""
        if not self.start_node or not self.end_node:
            return False
            
        self.reset_grid(keep_walls=True)
        self.running_algorithm = True
        self.algorithm_finished = False
        
        self.start_node.g_score = 0
        
        open_set = []
        heapq.heappush(open_set, (self.start_node.g_score, 0, self.start_node))
        open_set_hash = {self.start_node}
        
        counter = 0
        
        for row in self.grid:
            for node in row:
                node.update_neighbors(self.grid)
                
        while open_set:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                    
            current = heapq.heappop(open_set)[2]
            open_set_hash.remove(current)
            
            if current == self.end_node:
                self.path_length = self.reconstruct_path(current)
                self.algorithm_finished = True
                self.running_algorithm = False
                print(f"✓ Dijkstra Path found! Length: {self.path_length}, Nodes explored: {self.nodes_explored}")
                return True
                
            for neighbor in current.neighbors:
                temp_g_score = current.g_score + 1
                
                if temp_g_score < neighbor.g_score:
                    neighbor.came_from = current
                    neighbor.g_score = temp_g_score
                    
                    if neighbor not in open_set_hash:
                        counter += 1
                        heapq.heappush(open_set, (neighbor.g_score, counter, neighbor))
                        open_set_hash.add(neighbor)
                        neighbor.make_open()
                        self.nodes_explored += 1
                        
            self.draw()
            self.clock.tick(self.animation_speed)
            
            if current != self.start_node:
                current.make_closed()
                
        self.running_algorithm = False
        self.algorithm_finished = True
        print("✗ Dijkstra No path found!")
        return False
        
    def bfs_algorithm(self):
        """Breadth-First Search algorithm"""
        if not self.start_node or not self.end_node:
            return False
            
        self.reset_grid(keep_walls=True)
        self.running_algorithm = True
        self.algorithm_finished = False
        
        queue = [self.start_node]
        visited = {self.start_node}
        self.start_node.visited = True
        
        for row in self.grid:
            for node in row:
                node.update_neighbors(self.grid)
                
        while queue:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                    
            current = queue.pop(0)
            
            if current == self.end_node:
                self.path_length = self.reconstruct_path(current)
                self.algorithm_finished = True
                self.running_algorithm = False
                print(f"✓ BFS Path found! Length: {self.path_length}, Nodes explored: {self.nodes_explored}")
                return True
                
            for neighbor in current.neighbors:
                if neighbor not in visited:
                    neighbor.came_from = current
                    visited.add(neighbor)
                    queue.append(neighbor)
                    neighbor.make_open()
                    self.nodes_explored += 1
                    
            self.draw()
            self.clock.tick(self.animation_speed)
            
            if current != self.start_node:
                current.make_closed()
                
        self.running_algorithm = False
        self.algorithm_finished = True
        print("✗ BFS No path found!")
        return False
        
    def dfs_algorithm(self):
        """Depth-First Search algorithm"""
        if not self.start_node or not self.end_node:
            return False
            
        self.reset_grid(keep_walls=True)
        self.running_algorithm = True
        self.algorithm_finished = False
        
        stack = [self.start_node]
        visited = {self.start_node}
        self.start_node.visited = True
        
        for row in self.grid:
            for node in row:
                node.update_neighbors(self.grid)
                
        while stack:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                    
            current = stack.pop()
            
            if current == self.end_node:
                self.path_length = self.reconstruct_path(current)
                self.algorithm_finished = True
                self.running_algorithm = False
                print(f"✓ DFS Path found! Length: {self.path_length}, Nodes explored: {self.nodes_explored}")
                return True
                
            for neighbor in current.neighbors:
                if neighbor not in visited:
                    neighbor.came_from = current
                    visited.add(neighbor)
                    stack.append(neighbor)
                    neighbor.make_open()
                    self.nodes_explored += 1
                    
            self.draw()
            self.clock.tick(self.animation_speed)
            
            if current != self.start_node:
                current.make_closed()
                
        self.running_algorithm = False
        self.algorithm_finished = True
        print("✗ DFS No path found!")
        return False
        
    def run(self):
        """Main loop"""
        running = True
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            # Update button states
            for button in self.buttons.values():
                button.update_state(mouse_pos)
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if clicking on dropdown or dropdown options
                    if self.algorithm_dropdown.rect.collidepoint(mouse_pos):
                        if self.algorithm_dropdown.handle_event(event):
                            # Update selected algorithm
                            for algo in Algorithm:
                                if algo.value == self.algorithm_dropdown.selected_option:
                                    self.selected_algorithm = algo
                                    break
                        continue
                    
                    # Check if clicking on dropdown options while open
                    if self.algorithm_dropdown.is_open:
                        for i, rect in enumerate(self.algorithm_dropdown.option_rects):
                            if rect.collidepoint(mouse_pos):
                                self.algorithm_dropdown.handle_event(event)
                                for algo in Algorithm:
                                    if algo.value == self.algorithm_dropdown.selected_option:
                                        self.selected_algorithm = algo
                                        break
                                continue
                    
                    # Check button clicks
                    button_clicked = False
                    for button in self.buttons.values():
                        if button.is_clicked(mouse_pos):
                            button.trigger_press()  # Use new trigger_press method
                            button_clicked = True
                            break
                    
                    if button_clicked or self.running_algorithm:
                        continue
                    
                    # Grid interaction (only if not running algorithm)
                    if not self.running_algorithm:
                        # Left click on grid
                        if event.button == 1:
                            node = self.get_clicked_node(mouse_pos)
                            if node:
                                if not self.start_node and not node.is_end:
                                    node.make_start()
                                    self.start_node = node
                                elif not self.end_node and not node.is_start:
                                    node.make_end()
                                    self.end_node = node
                                elif node != self.start_node and node != self.end_node:
                                    node.make_wall()
                                    
                        # Right click on grid
                        elif event.button == 3:
                            node = self.get_clicked_node(mouse_pos)
                            if node:
                                node.reset()
                                node.is_wall = False
                                if node == self.start_node:
                                    self.start_node = None
                                elif node == self.end_node:
                                    self.end_node = None
                        
            # Continuous dragging (only for grid, not UI)
            if not self.running_algorithm:
                if pygame.mouse.get_pressed()[0] and mouse_pos[1] >= 180:
                    node = self.get_clicked_node(mouse_pos)
                    if node and node != self.start_node and node != self.end_node:
                        node.make_wall()
                        
                elif pygame.mouse.get_pressed()[2] and mouse_pos[1] >= 180:
                    node = self.get_clicked_node(mouse_pos)
                    if node:
                        node.reset()
                        node.is_wall = False
                        if node == self.start_node:
                            self.start_node = None
                        elif node == self.end_node:
                            self.end_node = None
                        
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()


if __name__ == "__main__":
    print("=" * 70)
    print("PATHFINDING VISUALIZER - PROFESSIONAL EDITION")
    print("=" * 70)
    print("\n📋 INSTRUCTIONS:")
    print("  1. Left Click: Place Start (Green) and End (Red) nodes")
    print("  2. Left Click & Drag: Draw walls (Black)")
    print("  3. Right Click: Erase nodes/walls")
    print("  4. Select Algorithm: Use dropdown to choose pathfinding algorithm")
    print("  5. Click 'Start Algorithm': Run selected algorithm")
    print("  6. Click 'Random Maze': Generate random maze")
    print("  7. Use Speed buttons to adjust animation speed")
    print("  8. Click 'Reset Path': Keep walls, clear path")
    print("  9. Click 'Remove Start/End': Remove start or end nodes")
    print("  10. Click 'Clear Board': Remove everything")
    print("\n🎨 COLOR LEGEND:")
    print("  🟢 Green (#00FF99): Start node")
    print("  🔴 Red (#FF6B6B): End node")
    print("  ⬛ Black (#2C2C2C): Walls")
    print("  🟡 Yellow (#FFD93D): Open nodes (to explore)")
    print("  🟣 Purple (#9D4EDD): Closed nodes (already explored)")
    print("  🔵 Blue (#4D96FF): Final path")
    print("  ⚪ White (#F9F9F9): Empty nodes")
    print("\n🔢 ALGORITHMS:")
    print("  • A* Algorithm: Most efficient, uses heuristic")
    print("  • Dijkstra's Algorithm: Guarantees shortest path")
    print("  • BFS (Breadth-First Search): Explores level by level")
    print("  • DFS (Depth-First Search): Explores depth first")
    print("\n" + "=" * 70 + "\n")
    
    visualizer = PathFinderVisualizer()
    visualizer.run()
