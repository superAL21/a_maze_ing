class Cell:
    """A single cell of the maze grid.

    Each cell knows which of its four walls are closed and stores its
    position, whether it has been visited during generation, and whether
    it belongs to the "42" pattern.
    """

    def __init__(self, x: int, y: int) -> None:
        """Initialise a cell with all four walls closed.

        Args:
            x: The column (horizontal position) of the cell.
            y: The row (vertical position) of the cell.
        """
        self.north: bool = True  # True = closed.
        self.south: bool = True
        self.west: bool = True
        self.east: bool = True
        self.visited: bool = False
        self.pattern: bool = False
        self.x: int = x
        self.y: int = y

    def hex_value(self) -> str:
        """Encode the cell's closed walls as a hexadecimal digit.

        Each wall maps to a bit (North=1, East=2, South=4, West=8); a
        closed wall sets its bit. The sum is returned as a lowercase
        hex digit.

        Returns:
            A single lowercase hexadecimal character ('0'-'f').
        """
        value = 0
        if self.north is True:
            value += 1
        if self.south is True:
            value += 4
        if self.east is True:
            value += 2
        if self.west is True:
            value += 8
        hexa_value = format(value, 'x')

        return hexa_value
