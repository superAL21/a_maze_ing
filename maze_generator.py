from typing import Any
from cell import Cell
import time
import random
from random import Random
from collections import deque
"""
MazeGenerator - A reusable maze generation module.

Builds mazes in two modes: "perfect" (a single unique path between any
two points) and "Pac-Man" (multiple loops, no dead ends).

Basic usage
-----------
    from maze_generator import MazeGenerator

    config = {
        "WIDTH": 20,
        "HEIGHT": 12,
        "ENTRY": (0, 0),
        "EXIT": (19, 11),
        "OUTPUT_FILE": "maze.txt",
        "PERFECT": True,
    }
    generator = MazeGenerator(config, seed=42)
    generator.stamp_42()
    generator.generate()

    # For Pac-Man mode (PERFECT=False), also call:
    # generator.add_loops()
    # generator.braid()

Custom parameters
-----------------
The constructor is MazeGenerator(data, seed=None):

    data : dict with the keys
        WIDTH, HEIGHT  -- maze size (int)
        ENTRY, EXIT    -- (x, y) coordinate tuples
        OUTPUT_FILE    -- output file name (str)
        PERFECT        -- True for a perfect maze, False for Pac-Man mode
        SEED           -- optional int

    seed : optional int for reproducible mazes. The same seed always
           produces the same maze. If None, data["SEED"] is used, or a
           random seed if that is absent too.

Accessing the structure
-----------------------
    generator.matrix   -- 2D list of Cell objects (the maze grid). Each
                          Cell has .north, .south, .east, .west
                          (True = closed wall) and .x, .y.
    generator.seed     -- the seed actually used.
    generator.width    -- maze width.
    generator.height   -- maze height.

Accessing a solution
--------------------
    solution = generator.find_path()

    Returns a string of moves ("N", "S", "E", "W") describing the
    shortest path from ENTRY to EXIT, and fills generator.path_cells
    with the Cell objects along that path.

Saving to a file
----------------
    generator.write_file()

    Writes the maze in hexadecimal format to the OUTPUT_FILE from the
    configuration. Note: the in-memory structure (generator.matrix) is
    not necessarily in the same format as the output file.
"""


class MazeGenerator:
    """Generate mazes in perfect or Pac-Man mode.

    Builds a grid of Cell objects and carves passages with a randomised
    depth-first search. Supports a reproducible seed, a stamped "42"
    pattern, colour themes, optional animation, path solving, and export
    to a file.
    """
    def __init__(self, data: dict[str, Any], seed: int | None = None) -> None:
        """Build the grid and set up seed, theme and configuration.

        Args:
            data: Config dict with WIDTH, HEIGHT, ENTRY, EXIT,
                OUTPUT_FILE, PERFECT and optionally SEED.
            seed: Optional seed for reproducibility. If None, the SEED
                from data is used, or a random one if that is absent.
        """
        self.width: int = data["WIDTH"]
        self.height: int = data["HEIGHT"]
        self.entry: tuple[int, int] = data["ENTRY"]
        self.exit: tuple[int, int] = data["EXIT"]
        self.output_file: str = data['OUTPUT_FILE']
        self.perfect: bool = data['PERFECT']
        self.path_cells: list[Cell] = []
        self.animate: bool = False

        if seed is None:
            seed = data.get("SEED")
        if seed is None:
            seed = random.randint(0, 999999)
        self.seed = seed
        self.rng: Random = Random(seed)

        self.matrix: list[list[Cell]] = []
        for y in range(self.height):
            vertical = []
            for x in range(self.width):
                vertical.append(Cell(x, y))
            self.matrix.append(vertical)

        self.theme = {
                    "Default": {
                        "wall":     ("\033[48;2;76;35;127m  "
                                     "\033[0m"),
                        "path":     ("\033[48;2;177;128;240m  "
                                     "\033[0m"),
                        "solution": "\033[48;2;0;180;216m  "
                                    "\033[0m",
                        "pattern":  ("\033[1;48;2;0;255;65m42\033[0m"),
                        "in":       ("\033[1;48;2;255;255;20m"
                                     "\033[38;2;30;30;30mIN"
                                     "\033[0m"),
                        "exit":     ("\033[1;48;2;255;0;0m"
                                     "\033[38;2;255;255;255mXX\033[0m"),
                    },
                    "Cyberpunk": {
                        "wall":     "\033[48;2;24;18;36m  \033[0m",
                        "path":     "\033[48;2;58;41;87m  \033[0m",
                        "solution": ("\033[48;2;58;41;87m"
                                     "\033[38;2;255;211;0m● \033[0m"),
                        "pattern":  ("\033[1;48;2;255;0;110m"
                                     "\033[38;2;255;255;255m42\033[0m"),
                        "in":       ("\033[1;48;2;0;240;255m"
                                     "\033[38;2;0;0;0mIN\033[0m"),
                        "exit":     ("\033[1;48;2;255;85;0m"
                                     "\033[38;2;255;255;255mXX\033[0m"),
                    },
                    "Barbie": {
                        "wall":     "\033[48;2;190;30;110m  \033[0m",
                        "path":     "\033[48;2;250;205;225m  \033[0m",
                        "solution": ("\033[48;2;250;205;225m"
                                     "\033[38;2;255;105;180m♥ \033[0m"),
                        "pattern":  ("\033[1;48;2;255;105;180m"
                                     "\033[38;2;255;255;255m42\033[0m"),
                        "in":       ("\033[1;48;2;255;180;210m"
                                     "\033[38;2;140;20;80mIN\033[0m"),
                        "exit":     ("\033[1;48;2;226;20;110m"
                                     "\033[38;2;255;255;255mXX\033[0m"),
                    },
                    "Oasis": {
                        "wall":     "\033[48;2;112;46;31m  \033[0m",
                        "path":     "\033[48;2;245;232;208m  \033[0m",
                        "solution": ("\033[48;2;245;232;208m"
                                     "\033[38;2;15;80;105m◆ \033[0m"),
                        "pattern":  ("\033[1;48;2;230;95;45m"
                                     "\033[38;2;0;0;0m42\033[0m"),
                        "in":       ("\033[1;48;2;110;130;70m"
                                     "\033[38;2;255;255;255mIN\033[0m"),
                        "exit":     ("\033[1;48;2;48;30;20m"
                                     "\033[38;2;255;255;255mXX\033[0m"),
                    },
                    "Nebula": {
                        "wall":     "\033[48;2;17;17;27m  \033[0m",
                        "path":     "\033[48;2;49;50;68m  \033[0m",
                        "solution": ("\033[48;2;49;50;68m"
                                     "\033[38;2;148;226;213m✧ \033[0m"),
                        "pattern":  ("\033[1;48;2;203;166;247m"
                                     "\033[38;2;17;17;27m42\033[0m"),
                        "in":       ("\033[1;48;2;166;227;161m"
                                     "\033[38;2;17;17;27mIN\033[0m"),
                        "exit":     ("\033[1;48;2;243;139;168m"
                                     "\033[38;2;17;17;27mXX\033[0m"),
                    },
                    "Arctic": {
                        "wall":     "\033[48;2;20;35;55m  \033[0m",
                        "path":     "\033[48;2;220;232;242m  \033[0m",
                        "solution": ("\033[48;2;220;232;242m"
                                     "\033[38;2;25;70;140m✦ \033[0m"),
                        "pattern":  ("\033[1;48;2;60;220;170m"
                                     "\033[38;2;20;35;55m42\033[0m"),
                        "in":       ("\033[1;48;2;170;185;200m"
                                     "\033[38;2;20;35;55mIN\033[0m"),
                        "exit":     ("\033[1;48;2;190;140;40m"
                                     "\033[38;2;255;255;255mXX\033[0m"),
                    },
        }

        self.apply_theme("Default")

    def apply_theme(self, name: str) -> None:
        """Apply a colour theme by name to the maze display.

        Args:
            name: The theme key (e.g. "Default", "Cyberpunk").
        """
        theme = self.theme[name]
        self.wall_colour = theme["wall"]
        self.path_colour = theme["path"]
        self.solution_colour = theme["solution"]
        self.pattern_colour = theme["pattern"]
        self.in_colour = theme["in"]
        self.exit_colour = theme["exit"]

    def display(self, show_path: bool = False) -> None:
        """Print the maze to the terminal using the current theme.

        Args:
            show_path: If True, highlight the solution path.
        """
        print(f"{self.wall_colour}" * (self.width * 2 + 1))
        for y in range(self.height):
            line_draw = self.wall_colour
            for x in range(self.width):
                cell = self.matrix[y][x]
                if (x, y) == self.entry:
                    line_draw += self.in_colour
                elif (x, y) == self.exit:
                    line_draw += self.exit_colour
                elif show_path and cell in self.path_cells:
                    line_draw += self.solution_colour
                elif cell.pattern:
                    line_draw += self.pattern_colour
                else:
                    line_draw += self.path_colour
                if cell.east:
                    line_draw += self.wall_colour
                else:
                    if x + 1 < self.width:
                        right = self.matrix[y][x + 1]
                    else:
                        right = None
                    if (
                        show_path
                        and cell in self.path_cells
                        and right is not None
                        and right in self.path_cells
                    ):
                        line_draw += self.solution_colour
                    else:
                        line_draw += self.path_colour
            print(line_draw)
            line_draw = self.wall_colour
            for x in range(self.width):
                cell = self.matrix[y][x]
                if cell.south:
                    line_draw += self.wall_colour
                else:
                    if y + 1 < self.height:
                        down = self.matrix[y + 1][x]
                    else:
                        down = None
                    if (
                        show_path
                        and cell in self.path_cells
                        and down is not None
                        and down in self.path_cells
                    ):
                        line_draw += self.solution_colour
                    else:
                        line_draw += self.path_colour
                line_draw += self.wall_colour
            print(line_draw)

    def stamp_42(self) -> None:
        """Mark the cells that form the "42" pattern at the centre.

        If the maze is too small to fit the pattern, prints a warning
        and returns without stamping.

        Raises:
            ValueError: If the entry or exit overlaps the pattern.
        """
        pattern_42 = [
            "#..#..####",
            "#..#.....#",
            "#..#.....#",
            "####..####",
            "...#..#...",
            "...#..#...",
            "...#..####"
            ]

        draw_height = len(pattern_42)
        draw_width = len(pattern_42[0])

        if self.width < draw_width + 4 or self.height < draw_height + 4:
            print(
                "[WARNING] Maze too small to display the 42 pattern."
                "\nIt requires at least 'WIDTH' >= 14 and 'HEIGHT' >= 11."
            )
            time.sleep(3)
            print(
                "\033[38;2;177;128;240m\nGenerating "
                "\033[1;38;2;0;180;216mMAZE"
                "\033[0m\033[38;2;177;128;240m without pattern... \033[0m"
            )
            time.sleep(4)
            return

        offset_x = (self.width - draw_width)//2
        offset_y = (self.height - draw_height)//2

        for pattern_y in range(draw_height):
            for pattern_x in range(draw_width):
                if pattern_42[pattern_y][pattern_x] == "#":
                    coord_x = offset_x + pattern_x
                    coord_y = offset_y + pattern_y
                    if (
                        (coord_x, coord_y) == self.entry
                        or (coord_x, coord_y) == self.exit
                    ):
                        raise ValueError(
                            "Error: Entry or exit"
                            " must not overlap with pattern")

                    else:
                        self.matrix[coord_y][coord_x].pattern = True
                        # self.matrix[coord_y][coord_x].visited = True

    def unvisited_nearby(self, cell: Cell) -> list[Cell]:
        """Return the unvisited, non-pattern neighbours of a cell.

        Args:
            cell: The cell whose neighbours are checked.

        Returns:
            A list of adjacent Cell objects not yet visited.
        """
        neighbours: list[Cell] = []
        candidates = [
            (cell.x-1, cell.y),  # W
            (cell.x, cell.y+1),  # S
            (cell.x+1, cell.y),  # E
            (cell.x, cell.y-1)  # N
        ]
        for (coord_x, coord_y) in candidates:
            if 0 <= coord_x < self.width and 0 <= coord_y < self.height:
                neighbour = self.matrix[coord_y][coord_x]
                if neighbour.visited is False and neighbour.pattern is False:
                    neighbours.append(neighbour)
        return neighbours

    def open_wall(self, cell_a: Cell, cell_b: Cell) -> None:
        """Open the wall between two adjacent cells.

        Determines the relative position of the two cells and sets the
        corresponding walls on both sides to False (open).

        Args:
            cell_a: The first cell.
            cell_b: The second cell, adjacent to cell_a.
        """
        if cell_b.x > cell_a.x:
            cell_a.east = False
            cell_b.west = False
        elif cell_b.x < cell_a.x:
            cell_b.east = False
            cell_a.west = False
        elif cell_b.y > cell_a.y:
            cell_b.north = False
            cell_a.south = False
        elif cell_b.y < cell_a.y:
            cell_b.south = False
            cell_a.north = False

    def generate(self) -> None:
        """Carve the maze using randomised depth-first search.

        Starts at the top-left cell and repeatedly opens walls to
        random unvisited neighbours, backtracking when stuck, until
        every reachable cell is visited. Animates each step if
        self.animate is True.
        """
        initial = self.matrix[0][0]
        initial.visited = True  # visited
        path = [initial]

        while path:
            current = path[-1]
            neighbours = self.unvisited_nearby(current)

            if neighbours:
                chosen_one = self.rng.choice(neighbours)
                self.open_wall(current, chosen_one)
                chosen_one.visited = True
                path.append(chosen_one)
            else:
                path.pop()

            if self.animate:
                print("\033[2J\033[3J\033[H", end="")
                self.display()
                time.sleep(0.018)

    def find_candidates(self) -> list[tuple[Cell, Cell]]:
        """Find all closed walls that could be opened into loops.

        Scans every non-pattern cell and collects the pairs of adjacent
        cells (east and south) that still share a closed wall.

        Returns:
            A list of (cell, neighbour) tuples sharing a closed wall.
        """
        candidates: list[tuple[Cell, Cell]] = []

        for y in range(self.height):
            for x in range(self.width):
                cell = self.matrix[y][x]
                if cell.pattern:
                    continue

                if (x + 1) < self.width:
                    right = self.matrix[y][x + 1]
                    if not right.pattern and cell.east:
                        candidates.append((cell, right))

                if (y + 1) < self.height:
                    down = self.matrix[y + 1][x]
                    if not down.pattern and cell.south:
                        candidates.append((cell, down))

        return candidates

    def block_is_open(self, x: int, y: int) -> bool:
        """Check whether the 3x3 block at (x, y) is fully open.

        Args:
            x: Left column of the 3x3 block.
            y: Top row of the 3x3 block.

        Returns:
            True if no inner wall is closed and no cell is a pattern
            cell, i.e. the block forms a fully open square.
        """
        for dy in range(3):
            for dx in range(3):
                if self.matrix[y + dy][x + dx].pattern:
                    return False

        for dy in range(3):
            for dx in range(2):
                if self.matrix[y + dy][x + dx].east:
                    return False

        for dy in range(2):
            for dx in range(3):
                if self.matrix[y + dy][x + dx].south:
                    return False

        return True

    def has_3x3(self) -> bool:
        """Return whether any fully open 3x3 block exists in the maze.

        Returns:
            True if at least one 3x3 open square is found, else False.
        """
        for y in range(0, self.height - 2):
            for x in range(0, self.width - 2):
                if self.block_is_open(x, y):
                    return True
        return False

    def available_nearby(self, cell: Cell) -> list[Cell]:
        """Return the neighbours reachable from a cell (open walls).

        Args:
            cell: The cell whose open sides are checked.

        Returns:
            A list of adjacent Cell objects connected by an open wall.
        """
        neighbours: list[Cell] = []

        if cell.north is False and 0 <= cell.y - 1 < self.height:
            neighbours.append(self.matrix[cell.y - 1][cell.x])

        if cell.south is False and 0 <= cell.y + 1 < self.height:
            neighbours.append(self.matrix[cell.y + 1][cell.x])

        if cell.east is False and 0 <= cell.x + 1 < self.width:
            neighbours.append(self.matrix[cell.y][cell.x + 1])

        if cell.west is False and 0 <= cell.x - 1 < self.width:
            neighbours.append(self.matrix[cell.y][cell.x - 1])

        return neighbours

    def find_path(self) -> str:
        """Find the shortest path from entry to exit using BFS.

        Fills self.path_cells with the cells along the path.

        Returns:
            A string of moves ("N", "E", "S", "W") from entry to exit.

        Raises:
            ValueError: If no path exists between entry and exit.
        """

        entry_x, entry_y = self.entry
        start = self.matrix[entry_y][entry_x]
        exit_x, exit_y = self.exit
        end = self.matrix[exit_y][exit_x]

        stash: deque[Cell] = deque([start])
        came_from: dict[Cell, Cell | None] = {start: None}

        while stash:
            current = stash.popleft()
            if current is end:
                break
            for neighbour in self.available_nearby(current):
                if neighbour not in came_from:
                    came_from[neighbour] = current
                    stash.append(neighbour)

        if end not in came_from:
            raise ValueError(
                "[WARNING] There's no available path between "
                "'ENTRY' and 'EXIT'. Adjust 'WIDTH' or/and 'HEIGHT'."
                )

        solution: list[str] = []
        cells_for_path: list[Cell] = []
        current_cell = end

        while current_cell is not start:
            cells_for_path.append(current_cell)
            prev = came_from[current_cell]
            if prev is None:
                break
            if current_cell.x > prev.x:
                solution.append("E")
            elif current_cell.x < prev.x:
                solution.append("W")
            elif current_cell.y < prev.y:
                solution.append("N")  # location of current_cell
            elif current_cell.y > prev.y:
                solution.append("S")
            current_cell = prev

        cells_for_path.append(start)
        solution.reverse()
        cells_for_path.reverse()
        self.path_cells = cells_for_path
        result = ("".join(solution))

        return result

    def animate_path(self, time_sleep: float = 0.25) -> None:
        """Animate the solution path cell by cell in the terminal.

        Args:
            time_sleep: Delay in seconds between each step.
        """

        if not self.path_cells:
            self.find_path()

        full_path = self.path_cells.copy()
        print("\033[2J", end="")

        try:
            print("\033[?25l", end="")
            for i in range(1, len(full_path) + 1):
                self.path_cells = full_path[:i]
                print("\033[3J\033[H", end="")
                self.display(show_path=True)
                time.sleep(time_sleep)
        finally:
            self.path_cells = full_path
            print("\033[?25h", end="")

    def add_loops(self) -> None:
        """Open extra walls to create loops (Pac-Man mode).

        Shuffles the candidate walls and opens about 10% of them,
        skipping any change that would create a fully open 3x3 block.
        """

        candidates = self.find_candidates()
        self.rng.shuffle(candidates)
        amount = int(len(candidates) * 0.10)

        knocked_walls = 0

        for (cell_a, cell_b) in candidates:
            if knocked_walls >= amount:
                break
            self.open_wall(cell_a, cell_b)
            if self.has_3x3():
                self.restore_wall(cell_a, cell_b)
            else:
                knocked_walls += 1

    def restore_wall(self, cell_a: Cell, cell_b: Cell) -> None:
        """Close again the wall between two cells.

        The inverse of open_wall: restores both shared walls to True.

        Args:
            cell_a: The first cell.
            cell_b: The second cell, adjacent to cell_a.
        """

        if cell_b.x > cell_a.x:
            cell_a.east = True
            cell_b.west = True
        elif cell_b.x < cell_a.x:
            cell_a.west = True
            cell_b.east = True
        elif cell_b.y > cell_a.y:
            cell_a.south = True
            cell_b.north = True
        elif cell_b.y < cell_a.y:
            cell_a.north = True
            cell_b.south = True

    def braid(self) -> None:
        """Remove dead ends by opening one extra wall each.

        For every non-pattern cell with a single open neighbour (a dead
        end), opens one more wall towards a random valid neighbour so
        the maze becomes fully braided.
        """

        for x in self.matrix:
            for cell in x:
                if cell.pattern:
                    continue
                if len(self.available_nearby(cell)) == 1:
                    candidates: list[Cell] = []

                    if cell.north and cell.y - 1 >= 0:
                        neighbour = self.matrix[cell.y - 1][cell.x]
                        if not neighbour.pattern:
                            candidates.append(neighbour)

                    if cell.south and cell.y + 1 < self.height:
                        neighbour = self.matrix[cell.y + 1][cell.x]
                        if not neighbour.pattern:
                            candidates.append(neighbour)

                    if cell.east and cell.x + 1 < self.width:
                        neighbour = self.matrix[cell.y][cell.x + 1]
                        if not neighbour.pattern:
                            candidates.append(neighbour)

                    if cell.west and cell.x - 1 >= 0:
                        neighbour = self.matrix[cell.y][cell.x - 1]
                        if not neighbour.pattern:
                            candidates.append(neighbour)

                    if candidates:
                        chosen_one = self.rng.choice(candidates)
                        self.open_wall(cell, chosen_one)

    def write_file(self) -> None:
        """Write the maze to the output file in hexadecimal format.

        Each cell becomes one hex digit encoding its closed walls, one
        row per line. After a blank line, the entry, exit and solution
        path are appended on three lines.
        """

        with open(self.output_file, "w") as f:
            for row_y in range(self.height):
                row_y_hexa = ""
                for cell_x in range(self.width):
                    row_y_hexa += self.matrix[row_y][cell_x].hex_value()
                f.write(f"{row_y_hexa}\n")
            f.write("\n")
            entry_x, entry_y = self.entry
            f.write(f"{entry_x},{entry_y}\n")
            exit_x, exit_y = self.exit
            f.write(f"{exit_x},{exit_y}\n")
            f.write(f"{self.find_path()}\n")

    def export_ansi_art(
            self, filename: str = "maze_art.txt",
            show_path: bool = False
            ) -> None:
        """Export the maze as coloured ANSI art to a file.

        Writes the maze using the current theme's ANSI colour codes so
        it can be viewed later with cat in a terminal.

        Args:
            filename: Output file name (default "maze_art.txt").
            show_path: If True, include the solution path.
        """

        try:
            with open(filename, "w", encoding="utf-8-sig") as f:
                f.write(f"{self.wall_colour}" * (self.width * 2 + 1) + "\n")

                for y in range(self.height):
                    line_draw = self.wall_colour
                    for x in range(self.width):
                        cell = self.matrix[y][x]
                        if (x, y) == self.entry:
                            line_draw += self.in_colour
                        elif (x, y) == self.exit:
                            line_draw += self.exit_colour
                        elif show_path and cell in self.path_cells:
                            line_draw += self.solution_colour
                        elif cell.pattern:
                            line_draw += self.pattern_colour
                        else:
                            line_draw += self.path_colour

                        if cell.east:
                            line_draw += self.wall_colour
                        else:
                            if x + 1 < self.width:
                                right = self.matrix[y][x + 1]
                            else:
                                right = None
                            if (
                                show_path
                                and cell in self.path_cells
                                and right is not None
                                and right in self.path_cells
                            ):
                                line_draw += self.solution_colour
                            else:
                                line_draw += self.path_colour
                    f.write(line_draw + "\n")

                    line_draw = self.wall_colour
                    for x in range(self.width):
                        cell = self.matrix[y][x]

                        if cell.south:
                            line_draw += self.wall_colour
                        else:
                            if y + 1 < self.height:
                                down = self.matrix[y + 1][x]
                            else:
                                down = None
                            if (
                                show_path
                                and cell in self.path_cells
                                and down is not None
                                and down in self.path_cells
                            ):
                                line_draw += self.solution_colour
                            else:
                                line_draw += self.path_colour
                        line_draw += self.wall_colour
                    f.write(line_draw + "\n")

            print(
                f"\n\033[1;38;2;166;227;161m[SUCCESS]"
                f" Maze art successfully exported to '{filename}'!\033[0m")
        except Exception as e:
            print(
                f"\n\033[1;38;2;255;50;50m[ERROR]"
                f" Could not save file: {e}\033[0m")
