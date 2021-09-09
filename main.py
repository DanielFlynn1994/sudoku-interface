import numpy as np
import pygame as pg
from pygame.locals import *
import sys

starting_sudoku = np.array([
    [0, 3, 0, 0, 0, 0, 0, 0, 0],
    [0, 4, 0, 0, 5, 0, 0, 1, 0],
    [0, 2, 0, 6, 1, 3, 5, 0, 4],

    [0, 0, 6, 8, 0, 2, 0, 0, 5],
    [0, 1, 8, 7, 0, 0, 3, 0, 0],
    [7, 0, 3, 1, 0, 6, 2, 0, 8],

    [1, 0, 0, 4, 0, 9, 7, 0, 6],
    [9, 0, 0, 3, 7, 8, 4, 0, 1],
    [0, 0, 0, 0, 6, 1, 9, 0, 0]
])

menu_width = 225
grid_height = 630
grid_width = 630
window_width = grid_width + menu_width
window_height = grid_height
square_size = grid_width // 3
cell_size = square_size // 3

white = (255, 255, 255)
black = (0, 0, 0)
yellow = (255, 255, 0)
grey = (120, 120, 120)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)


class Grid:
    def __init__(self, rows, cols, width, height):
        self.rows = rows
        self.cols = cols
        self.width = width
        self.height = height
        # each square is it's own object, and the values are then rendered onto the screen
        self.squares = [[Square(r, c, starting_sudoku[r][c], starting_sudoku[r][c])
                         for c in range(cols)] for r in range(rows)]
        self.buttons = [Button("Restart", 0, grid_width + 25, menu_width - 50, cell_size, white),
                        Button("Check", 2 * cell_size, grid_width + 25, menu_width - 50, cell_size, white),
                        Button("Undo", 4 * cell_size, grid_width + 25, menu_width - 50, cell_size, white),
                        Button("Solve", 6 * cell_size, grid_width + 25, menu_width - 50, cell_size, white)]
        # lists actions to be used with the undo function
        self.action_log = []
        self.time = 0

    # functions relating to mechanics

    # whenever you edit a square it will go through the perform_action function
    def perform_action(self, action):
        self.action_log.append(action)
        # inputs change different values depending on what type of mark the user is
        # trying to do
        if isinstance(action, Centre):
            values = self.squares[action.cell_row][action.cell_col].centre_values
            if action.new_value in values:
                values.remove(action.new_value)
            else:
                values.append(action.new_value)
            values.sort()
            self.squares[action.cell_row][action.cell_col].centre_values = values
        elif isinstance(action, Corner):
            values = self.squares[action.cell_row][action.cell_col].corner_values
            if action.new_value in values:
                values.remove(action.new_value)
            else:
                values.append(action.new_value)
            values.sort()
            self.squares[action.cell_row][action.cell_col].corner_values = values
        else:
            self.squares[action.cell_row][action.cell_col].temp_value = action.new_value

    # Only undoes actions that edit a square's values
    def undo_action(self):
        if self.action_log:
            action = self.action_log[-1]
            self.action_log.pop()
            if isinstance(action, Centre):
                values = self.squares[action.cell_row][action.cell_col].centre_values
                if action.new_value in values:
                    values.remove(action.new_value)
                else:
                    values.append(action.new_value)
                values.sort()
                self.squares[action.cell_row][action.cell_col].centre_values = values
            elif isinstance(action, Corner):
                values = self.squares[action.cell_row][action.cell_col].corner_values
                if action.new_value in values:
                    values.remove(action.new_value)
                else:
                    values.append(action.new_value)
                values.sort()
                self.squares[action.cell_row][action.cell_col].corner_values = values
            else:
                self.squares[action.cell_row][action.cell_col].temp_value = action.old_value
        else:
            pass

    # Checks if a a value for a certain square is valid, used
    # for the solve button
    def valid_placement(self, row, col, number):
        for c in range(9):
            if self.squares[row][c].temp_value == number:
                return False
        for r in range(9):
            if self.squares[r][col].temp_value == number:
                return False
        # the mod 3 is to check which of the 3x3 boxes the number we are checking
        # is in
        square_row = (row // 3) * 3
        square_col = (col // 3) * 3
        for r in range(0, 3):
            for c in range(0, 3):
                if self.squares[square_row + r][square_col + c].temp_value == number:
                    return False
        return True

    def backtracking_solver(self, win, grid):
        for r in range(9):
            for c in range(9):
                # doesnt check the number if the user has typed anything into the square
                if self.squares[r][c].temp_value == 0:
                    for number in range(1, 10):
                        if self.valid_placement(r, c, number):
                            self.squares[r][c].temp_value = number
                            if self.backtracking_solver(win, grid):
                                return True
                            else:
                                self.squares[r][c].temp_value = 0
                    return False
        return True

    # functions relating to GUI
    def draw_grid(self, win):
        for r in range(self.rows):
            for c in range(self.cols):
                self.squares[r][c].draw(win)

        for r in range(self.rows + 1):
            # draws thicker lines for the 3x3 boxes outlines
            if r % 3 == 0:
                pg.draw.line(win, black, (0, r * cell_size), (grid_width, r * cell_size), 2)
                pg.draw.line(win, black, (r * cell_size, 0), (r * cell_size, grid_width), 2)
            else:
                pg.draw.line(win, black, (0, r * cell_size), (grid_width, r * cell_size))
                pg.draw.line(win, black, (r * cell_size, 0), (r * cell_size, grid_width))

        for button in self.buttons:
            button.draw(win)

        # all of this below is to show the time
        seconds = self.time // 1000
        time = format_time(seconds)

        pg.draw.rect(win, black, (grid_width + 25, 8 * cell_size, menu_width - 50, 3 * cell_size // 4), 1)
        font = pg.font.SysFont("Arial", 24)
        text = font.render(time, True, black)
        text_width = text.get_rect().width
        text_height = text.get_rect().height
        win.blit(text, (grid_width + 25 + (menu_width - 50 - text_width) // 2,
                        8 * cell_size + (3 * cell_size // 4 - text_height) // 2))

    # removes the yellow colouring from all squares
    def deselect_all(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.squares[r][c].selected = False

    # checks first if the user has finished the sudoku, then if the inputs they
    # have are correct
    def check_board(self):
        solved = True
        for r in range(self.rows):
            for c in range(self.cols):
                if self.squares[r][c].temp_value == 0:
                    self.squares[r][c].incorrect = True
                    solved = False
                else:
                    value = self.squares[r][c].temp_value
                    self.squares[r][c].temp_value = 0
                    if not self.valid_placement(r, c, value):
                        self.squares[r][c].temp_value = value
                        self.squares[r][c].incorrect = True
                        solved = False
                    self.squares[r][c].temp_value = value
        return solved

    # restarts the sudoku
    def restart_game(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.squares[r][c].temp_value = self.squares[r][c].starting_value
                self.squares[r][c].centre_values = []
                self.squares[r][c].corner_values = []
        self.action_log = []
        self.time = 0

    # when the user clicks the check button, mistakes are highlighted. This function
    # undoes that highlighting
    def reset_highlights(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.squares[r][c].incorrect = False


class Square:
    def __init__(self, row, col, starting_value, temp_value):
        self.row = row
        self.col = col
        # starting value ensures the user can't change the original vales in the squares.
        self.starting_value = starting_value
        self.temp_value = temp_value
        # These are different types of markings players use for potential numbers in a squares.
        self.corner_values = []
        self.centre_values = []
        # these 2 will highlight the squares if they are true
        self.selected = False
        self.incorrect = False

    # draws each of the squares
    def draw(self, win):
        # used with the check function
        if self.incorrect:
            pg.draw.rect(win, red, (self.col * cell_size, self.row * cell_size, cell_size, cell_size))

        # highlights the cell the player is clicked on
        if self.selected:
            pg.draw.rect(win, yellow, (self.col * cell_size, self.row * cell_size, cell_size, cell_size))

        # the values the user has inputted are a different colour to the starting values
        # so that the user knows which ones they have inputted
        if self.starting_value != 0:
            font = pg.font.SysFont("Arial", 48)
            text = font.render(str(self.starting_value), True, grey)
            win.blit(text, ((self.col + 1 / 4) * cell_size, (self.row + 1 / 6) * cell_size))
        elif self.temp_value == 0:
            if self.corner_values:
                font = pg.font.SysFont("Arial", 16)
                corner_values = ''.join(str(i) for i in self.corner_values)
                text = font.render(corner_values, True, blue)
                # the 1/10 adds a bit of space between the values and the borders of the cells
                win.blit(text, ((self.col + 1 / 10) * cell_size, (self.row + 1 / 10) * cell_size))
            if self.centre_values:
                font = pg.font.SysFont("Arial", 16)
                centre_values = ''.join(str(i) for i in self.centre_values)
                text = font.render(centre_values, True, red)
                text_width = text.get_rect().width
                text_height = text.get_rect().height
                win.blit(text, ((self.col + 1 / 2) * cell_size - text_width // 2,
                                (self.row + 1 / 2) * cell_size - text_height // 2))
        else:
            font = pg.font.SysFont("Arial", 48)
            text = font.render(str(self.temp_value), True, black)
            win.blit(text, ((self.col + 1 / 4) * cell_size, (self.row + 1 / 6) * cell_size))


class Button:
    def __init__(self, text, top_loc, left_loc, width, height, colour):
        self.text = text
        self.top_loc = top_loc
        self.left_loc = left_loc
        self.width = width
        self.height = height
        self.colour = colour
        self.selected = False

    def draw(self, win):
        # these are used with the restart and solve functions to avoid misclicks
        text = "You Sure?" if self.selected else self.text
        colour = red if self.selected else self.colour

        pg.draw.rect(win, colour, (self.left_loc, self.top_loc, self.width, self.height))
        pg.draw.rect(win, black, (self.left_loc, self.top_loc, self.width, self.height), 1)
        font = pg.font.SysFont("Arial", 24)
        text = font.render(text, True, black)
        text_width = text.get_rect().width
        text_height = text.get_rect().height
        win.blit(text, (self.left_loc + (self.width - text_width) // 2,
                        self.top_loc + (self.height - text_height) // 2))


class Actions:
    def __init__(self, cell_loc, old_value, new_value, grid_state):
        self.cell_loc = cell_loc
        self.cell_row = cell_loc[0]
        self.cell_col = cell_loc[1]
        self.old_value = old_value
        self.new_value = new_value
        self.grid_state = grid_state


class Centre(Actions):
    def __init__(self, cell_loc, old_value, new_value, grid_state):
        super().__init__(cell_loc, old_value, new_value, grid_state)


class Corner(Actions):
    def __init__(self, cell_loc, old_value, new_value, grid_state):
        super().__init__(cell_loc, old_value, new_value, grid_state)


def update_screen(win, grid):
    win.fill(white)
    grid.draw_grid(win)


def format_time(seconds):
    # every multiple of 3600 seconds is an hour
    hours = seconds // (60 * 60)
    seconds %= (60 * 60)
    # every multiple of 60 seconds is a minute
    minutes = seconds // 60
    seconds %= 60

    hour_str = "0" + str(hours) if hours < 10 else str(hours)
    minute_str = "0" + str(minutes) if minutes < 10 else str(minutes)
    seconds_str = "0" + str(seconds) if seconds < 10 else str(seconds)

    return hour_str + ":" + minute_str + ":" + seconds_str


def main():
    win = pg.display.set_mode((window_width, window_height))
    clock = pg.time.Clock()
    pg.display.set_caption("Sudoku")
    grid = Grid(9, 9, grid_width, grid_height)
    [restart_button, check_button, undo_button, solve_button] = [grid.buttons[i] for i in range(4)]
    restart_loc = [restart_button.left_loc, restart_button.left_loc + restart_button.width,
                   restart_button.top_loc, restart_button.top_loc + restart_button.height]
    check_loc = [check_button.left_loc, check_button.left_loc + check_button.width,
                 check_button.top_loc, check_button.top_loc + check_button.height]
    undo_loc = [undo_button.left_loc, undo_button.left_loc + undo_button.width,
                undo_button.top_loc, undo_button.top_loc + undo_button.height]
    solve_loc = [solve_button.left_loc, solve_button.left_loc + solve_button.width,
                 solve_button.top_loc, solve_button.top_loc + solve_button.height]
    running = True
    update_screen(win, grid)
    square_list = []
    current_square = ()
    shift_pressed = False
    ctrl_pressed = False
    row = 0
    col = 0
    while running:
        clock.tick(60)
        grid.time = pg.time.get_ticks()
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                row = pos[1] // cell_size
                col = pos[0] // cell_size
                # highlights the cell the user clicked on, and clears the highlight of the previous cell
                grid.reset_highlights()
                # holding ctrl allows the user to highlight and input in more than one
                # square at a time
                if current_square and not ctrl_pressed:
                    grid.deselect_all()
                    square_list = []
                current_square = (row, col)
                square_list.append(current_square)
                if 0 <= row <= 8 and 0 <= col <= 8:
                    grid.squares[row][col].selected = True
                if restart_loc[0] <= pos[0] <= restart_loc[1] and restart_loc[2] <= pos[1] <= restart_loc[3]:
                    if restart_button.selected:
                        grid.restart_game()
                    restart_button.selected = not restart_button.selected
                else:
                    restart_button.selected = False
                if check_loc[0] <= pos[0] <= check_loc[1] and check_loc[2] <= pos[1] <= check_loc[3]:
                    if grid.check_board():
                        check_button.text = "Well Done!!"
                        check_button.colour = green
                    else:
                        check_button.text = "Not Quite"
                        check_button.colour = red
                else:
                    check_button.text = "Check"
                    check_button.colour = white
                if undo_loc[0] <= pos[0] <= undo_loc[1] and undo_loc[2] <= pos[1] <= undo_loc[3]:
                    grid.undo_action()
                if solve_loc[0] <= pos[0] <= solve_loc[1] and solve_loc[2] <= pos[1] <= solve_loc[3]:
                    if solve_button.selected:
                        grid.backtracking_solver(win, grid)
                    solve_button.selected = not solve_button.selected
                else:
                    solve_button.selected = False
                update_screen(win, grid)
            if event.type == KEYDOWN:
                key_dic = {pg.K_1: 1, pg.K_2: 2, pg.K_3: 3, pg.K_4: 4, pg.K_5: 5, pg.K_6: 6, pg.K_7: 7, pg.K_8: 8,
                           pg.K_9: 9, K_DELETE: "delete", K_UP: "up", K_LEFT: "left", K_RIGHT: "right", K_DOWN: "down",
                           K_LSHIFT: "left_shift", K_LCTRL: "left_ctrl", K_z : "z"}
                if event.key in key_dic and current_square:
                    rows = [square[0] for square in square_list]
                    cols = [square[1] for square in square_list]
                    squares = [grid.squares[rows[i]][cols[i]] for i in range(len(rows))]
                    key = key_dic[event.key]
                    # only adds the action to the log if they are actually changing the value in the square
                    if key in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                        for i in range(len(square_list)):
                            square = squares[i]
                            if square.starting_value == 0:
                                if ctrl_pressed and square.temp_value == 0:
                                    action = Centre(square_list[i], square.centre_values, key, grid.squares)
                                    grid.perform_action(action)
                                elif shift_pressed and square.temp_value == 0:
                                    action = Corner(square_list[i], square.corner_values, key, grid.squares)
                                    grid.perform_action(action)
                                elif square.temp_value != key and not ctrl_pressed and not shift_pressed:
                                    action = Actions(square_list[i], square.temp_value, key, grid.squares)
                                    grid.perform_action(action)
                    elif key == "delete":
                        for i in range(len(square_list)):
                            square = squares[i]
                            if square.temp_value == 0:
                                if square.corner_values:
                                    for j in range(len(square.corner_values)):
                                        value = square.corner_values[0]
                                        action = Corner(square_list[i], value, value, grid.squares)
                                        grid.perform_action(action)
                                if square.centre_values:
                                    for j in range(len(square.centre_values)):
                                        value = square.centre_values[0]
                                        action = Centre(square_list[i], value, value, grid.squares)
                                        grid.perform_action(action)
                            else:
                                action = Actions(square_list[i], square.temp_value, 0, grid.squares)
                                grid.perform_action(action)
                    elif key == "up":
                        square = squares[0]
                        row -= 1
                        # if the user is on row 0, the mod 9 makes -1 to 8
                        # to place them on the row 8
                        row %= 9
                        square.selected = False
                        grid.squares[row][col].selected = True
                        square_list = [(row, col)]
                    elif key == "down":
                        square = squares[0]
                        row += 1
                        # if the user is on row 8, the mod 9 makes 9 to 0
                        # to place them on the top row
                        row %= 9
                        square.selected = False
                        grid.squares[row][col].selected = True
                        square_list = [(row, col)]
                    elif key == "right":
                        square = squares[0]
                        col += 1
                        # if the user is on col 8, the mod 9 makes 9 to 0
                        # to place them on the rightmost col
                        col %= 9
                        square.selected = False
                        grid.squares[row][col].selected = True
                        square_list = [(row, col)]
                    elif key == "left":
                        square = squares[0]
                        col -= 1
                        # if the user is on col 0, the mod 9 makes -1 to 8
                        # to place them on the leftmost col
                        col %= 9
                        square.selected = False
                        grid.squares[row][col].selected = True
                        square_list = [(row, col)]
                    elif key == "left_shift":
                        # holding shift allows the corner values to be changed
                        shift_pressed = True
                    elif key == "left_ctrl":
                        # holding ctrl allows the centre values to be changed
                        ctrl_pressed = True
                    elif key == "z":
                        # pressing z undoes your last input
                        grid.undo_action()
                    update_screen(win, grid)
            if event.type == KEYUP:
                key_dic = {K_LSHIFT: "left_shift", K_LCTRL: "left_ctrl"}
                if event.key in key_dic:
                    key = key_dic[event.key]
                    if key == "left_shift":
                        shift_pressed = False
                    elif key == "left_ctrl":
                        ctrl_pressed = False
        update_screen(win, grid)


pg.init()
pg.font.init()
main()
