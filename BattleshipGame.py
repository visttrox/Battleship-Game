import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton,
    QMessageBox, QHBoxLayout, QLabel, QVBoxLayout,
    QMessageBox
)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon

class BattleshipGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Морской бой")
        self.width = 700
        self.height = 800
        self.setGeometry(100, 100, self.width, self.height)
        self.setFixedSize(self.width, self.height)
        self.setStyleSheet("background-color: rgb(56, 176, 245);")
        self.setWindowIcon(QIcon('icon.ico'))

        self.grid_size = 8
        self.computer_moves = []
        self.game = False
        self.ship_place = False
        self.ship_delete = False
        self.computer_direction_horizon = None
        self.player_grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.computer_grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.ships = {1: 3, 2: 2, 3: 1}
        self.new_ships = {1: 3, 2: 2, 3: 1}

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.computer_turn)
        self.initUI()
        self.place_ships(self.computer_grid)
        
    def initUI(self):
        self.layout = QHBoxLayout()
        self.layout_player = QVBoxLayout()
        self.buttons_ship = QHBoxLayout()
        self.buttons_ships_list = []
        for ship in self.ships:
            button = QPushButton()
            button.setFixedSize(int(self.width*0.15), int(self.height*0.1))
            button.setText(str(ship)+' кораблей \n'+'осталось: '+str(self.ships[ship]))
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgb(23, 101, 145);
                    color: white; 
                    border-radius: 15%;
                } 
                QPushButton:hover {
                    background-color: rgb(14, 63, 92);
                } 
                QPushButton:disabled {
                    background-color: rgb(61, 127, 166);
                }
            """)
            if self.ships[ship] <= 0:
                button.setEnabled(False)
            button.clicked.connect(lambda checked, size=ship: self.place_ship_mode(size))
            self.buttons_ships_list.append(button)
            self.buttons_ship.addWidget(button)
        
        self.delete_button = QPushButton()
        self.delete_button.setFixedSize(int(self.width*0.2), int(self.height*0.1))
        self.delete_button.setText('Удалить Корабль')
        self.delete_button.setEnabled(False)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: rgb(23, 101, 145); 
                color: white; 
                border-radius: 25%;
            } 
            QPushButton:hover {
                background-color: rgb(14, 63, 92);
            }
            QPushButton:disabled {
                background-color: rgb(61, 127, 166);   
            }
        """)
        self.delete_button.clicked.connect(self.delete_ship_mode)
        self.buttons_ship.addWidget(self.delete_button)

        self.start_button = QPushButton()
        self.start_button.setFixedSize(int(self.width*0.15), int(self.height*0.1))
        self.start_button.setText('Запуск')
        self.start_button.setEnabled(False)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: rgb(29, 145, 19); 
                color: white; 
                border-radius: 25%;
            } 
            QPushButton:hover {
                background-color: rgb(42, 199, 28);
            }
            QPushButton:disabled {
                background-color: rgb(61, 127, 166);   
            }
        """)
        self.start_button.clicked.connect(self.start_game)
        self.buttons_ship.addWidget(self.start_button)

        self.player_grid_layout = QGridLayout()
        self.player_grid_layout.setSpacing(0)
        self.player_buttons = [[None] * self.grid_size for _ in range(self.grid_size)]
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                button = QPushButton()
                size = min(int(self.width*0.1), int(self.height*0.1))
                button.setFixedSize(size, size)
                button.setStyleSheet("""
                    QPushButton {
                        background-color: rgb(45, 141, 196);
                    } 
                    QPushButton:hover {
                        background-color: Purple;
                    }
                """)
                button.setEnabled(False)
                self.player_buttons[i][j] = button
                self.player_grid_layout.addWidget(button, i, j)

        self.layout_player.addLayout(self.buttons_ship)
        self.layout_player.addLayout(self.player_grid_layout)
        self.layout.addLayout(self.layout_player)

        self.layout_computer = QVBoxLayout()
        self.computer_grid_layout = QGridLayout()
        self.computer_grid_layout.setSpacing(0)
        self.computer_buttons = [[None] * self.grid_size for _ in range(self.grid_size)]
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                button = QPushButton()
                size = min(int(self.width*0.1), int(self.height*0.1))
                button.setFixedSize(size, size)
                button.setStyleSheet("""
                    QPushButton {
                        background-color: rgb(45, 141, 196);
                    } 
                    QPushButton:hover {
                        background-color: rgb(58, 196, 45);
                    }
                """)
                button.clicked.connect(lambda checked, x=i, y=j: self.player_turn(x, y))
                self.computer_buttons[i][j] = button
                button.hide()
                self.computer_grid_layout.addWidget(button, i, j)
        
        self.layout_computer.addLayout(self.computer_grid_layout)
        self.layout.addLayout(self.layout_computer)
        self.setLayout(self.layout)

    def resizeEvent(self, event):
        self.width = self.size().width()
        self.height = self.size().height()
        if self.game:
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    size = min(int(self.width*0.08), int(self.height*0.08))
                    self.player_buttons[i][j].setFixedSize(size, size)
                    self.computer_buttons[i][j].setFixedSize(size, size)
        else:
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    size = min(int(self.width*0.1), int(self.height*0.1))
                    self.player_buttons[i][j].setFixedSize(size, size)
                    self.computer_buttons[i][j].setFixedSize(size, size)
        for button in self.buttons_ships_list:
            button.setFixedSize(int(self.width*0.15), int(self.height*0.1))
        self.delete_button.setFixedSize(int(self.width*0.2), int(self.height*0.1))
        self.start_button.setFixedSize(int(self.width*0.15), int(self.height*0.1))

    def place_ship_mode(self, size):
        if self.ship_place:
            self.ship_place = False
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    self.player_buttons[i][j].setEnabled(False)
                    try:
                        self.player_buttons[i][j].disconnect()
                    except:
                        pass
            if self.ship_parts:
                self.button_ship_delete(self.ship_parts[0][0], self.ship_parts[0][1])
                self.new_ships[self.size_ship]+=1
            else:
                for number in self.new_ships:
                    if self.new_ships[number] > 0:
                        self.buttons_ships_list[number-1].setEnabled(True)
                        self.buttons_ships_list[number-1].setStyleSheet("""
                        QPushButton {
                            background-color: rgb(23, 101, 145);
                            color: white; 
                            border-radius: 15%;
                        } 
                        QPushButton:hover {
                            background-color: rgb(14, 63, 92);
                        } 
                        QPushButton:disabled {
                            background-color: rgb(61, 127, 166);
                        }
                    """)
                self.delete_button.setEnabled(True)
        else:
            self.ship_place = True
            self.ship_parts = []
            self.delete_button.setEnabled(False)
            for button in self.buttons_ships_list:
                if self.buttons_ships_list[size-1] != button:
                    button.setEnabled(False)
                else:
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: rgb(14, 63, 92);
                            color: white; 
                            border-radius: 15%;
                        } 
                        QPushButton:hover {
                            background-color: rgb(14, 63, 92);
                        } 
                        QPushButton:disabled {
                            background-color: rgb(61, 127, 166);
                        }
                    """)
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if self.player_grid[i][j] == 0:
                        self.player_buttons[i][j].setEnabled(True)
                        self.player_buttons[i][j].clicked.connect(lambda checked, size=size, x=i, y=j: self.button_place_ship(size, x, y))

    def button_place_ship(self, size, x, y):
        if not self.ship_parts:
            self.ship_parts.append((x, y))
            self.player_buttons[x][y].setEnabled(False)
            self.player_buttons[x][y].setStyleSheet("background-color: purple;")
            self.player_grid[x][y] = 1
        elif len(self.ship_parts) == 1:
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            for direct in directions:
                if (direct[0]+x, direct[1]+y) == self.ship_parts[0]:
                    self.ship_parts.append((x, y))
                    self.player_buttons[x][y].setEnabled(False)
                    self.player_buttons[x][y].setStyleSheet("background-color: purple;")
                    self.player_grid[x][y] = 1
                    self.computer_direction_horizon = self.ship_parts[0][0] != self.ship_parts[1][0]
        else:
            if self.computer_direction_horizon:
                directions = [(1, 0), (-1, 0)]
            else:
                directions = [(0, 1), (0, -1)]
            for direct in directions:
                for ship in self.ship_parts:
                    if (direct[0]+x, direct[1]+y) == ship:
                        self.ship_parts.append((x, y))
                        self.player_buttons[x][y].setEnabled(False)
                        self.player_buttons[x][y].setStyleSheet("background-color: purple;")
                        self.player_grid[x][y] = 1
                        self.computer_direction_horizon = self.ship_parts[0][0] != self.ship_parts[1][0]
        if len(self.ship_parts) >= size:
            self.ship_place = False
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    self.player_buttons[i][j].setEnabled(False)
                    try:
                        self.player_buttons[i][j].disconnect()
                    except:
                        pass
            self.new_ships[size] -= 1
            self.buttons_ships_list[size-1].setText(str(size)+' кораблей \n'+'осталось: '+str(self.new_ships[size]))
            for number in self.new_ships:
                if self.new_ships[number] > 0:
                    self.buttons_ships_list[number-1].setEnabled(True)
                    self.buttons_ships_list[number-1].setStyleSheet("""
                        QPushButton {
                            background-color: rgb(23, 101, 145);
                            color: white; 
                            border-radius: 15%;
                        } 
                        QPushButton:hover {
                            background-color: rgb(14, 63, 92);
                        } 
                        QPushButton:disabled {
                            background-color: rgb(61, 127, 166);
                        }
                    """)
                elif size == number:
                    self.buttons_ships_list[number-1].setEnabled(False)
                    self.buttons_ships_list[number-1].setStyleSheet("""
                        QPushButton {
                            background-color: rgb(127, 190, 227);
                            color: white; 
                            border-radius: 15%;
                        } 
                        QPushButton:hover {
                            background-color: rgb(14, 63, 92);
                        } 
                        QPushButton:disabled {
                            background-color: rgb(61, 127, 166);
                        }
                    """)
            self.computer_direction_horizon = None
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
            for ship in self.ship_parts:
                self.player_buttons[ship[0]][ship[1]].setStyleSheet("background-color: Green;")
                for direct in directions:
                    neighbor_x = ship[0] + direct[0]
                    neighbor_y = ship[1] + direct[1]
                    if 0 <= neighbor_x < self.grid_size and 0 <= neighbor_y < self.grid_size:
                        if self.player_grid[neighbor_x][neighbor_y] <= 0:
                            self.player_grid[neighbor_x][neighbor_y] -= 2
            self.ship_parts = []
            if sum(self.new_ships.values()) <= 0:
                self.start_button.setEnabled(True)
            self.delete_button.setEnabled(True)

    def delete_ship_mode(self):
        if self.ship_delete:
            self.ship_delete = False
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if self.player_grid[i][j] == 1:
                        self.player_buttons[i][j].setStyleSheet("background-color: Green;")
                        self.player_buttons[i][j].setEnabled(False)
                        try:
                            self.player_buttons[i][j].disconnect()
                        except:
                            pass
            self.delete_button.setStyleSheet("""
                QPushButton {
                    background-color: rgb(23, 101, 145); 
                    color: white; 
                    border-radius: 25%;
                } 
                QPushButton:hover {
                    background-color: rgb(14, 63, 92);
                }
                QPushButton:disabled {
                    background-color: rgb(61, 127, 166);   
                }
            """)
            for number in self.new_ships:
                if self.new_ships[number] > 0:
                    self.buttons_ships_list[number-1].setEnabled(True)
                    self.buttons_ships_list[number-1].setStyleSheet("""
                    QPushButton {
                        background-color: rgb(23, 101, 145);
                        color: white; 
                        border-radius: 15%;
                    } 
                    QPushButton:hover {
                        background-color: rgb(14, 63, 92);
                    } 
                    QPushButton:disabled {
                        background-color: rgb(61, 127, 166);
                    }
                """)
        else:
            self.ship_delete = True
            self.delete_button.setStyleSheet("""
                QPushButton {
                    background-color: rgb(14, 63, 92); 
                    color: white; 
                    border-radius: 25%;
                } 
                QPushButton:hover {
                    background-color: rgb(14, 63, 92);
                }
                QPushButton:disabled {
                    background-color: rgb(61, 127, 166);   
                }
            """)
            for button in self.buttons_ships_list:
                button.setEnabled(False) 
                button.setStyleSheet("""
                    QPushButton {
                        background-color: rgb(23, 101, 145);
                        color: white; 
                        border-radius: 15%;
                    } 
                    QPushButton:hover {
                        background-color: rgb(14, 63, 92);
                    } 
                    QPushButton:disabled {
                        background-color: rgb(61, 127, 166);
                    }
                """)
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if self.player_grid[i][j] == 1:
                        self.player_buttons[i][j].setStyleSheet("background-color: rgb(16, 74, 10);")
                        self.player_buttons[i][j].setEnabled(True)
                        self.player_buttons[i][j].clicked.connect(lambda checked, x=i, y=j: self.button_ship_delete(x, y))

    def button_ship_delete(self, x, y):
        self.ship_delete = False
        self.size_ship = 0
        self.delete_ship(x, y)
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.player_grid[i][j] == 1:
                    self.player_buttons[i][j].setStyleSheet("background-color: Green;")
                    self.player_buttons[i][j].setEnabled(False)
                    try:
                        self.player_buttons[i][j].disconnect()
                    except:
                        pass
        self.new_ships[self.size_ship] += 1
        self.buttons_ships_list[self.size_ship-1].setText(str(self.size_ship)+' кораблей \n'+'осталось: '+str(self.new_ships[self.size_ship]))
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: rgb(23, 101, 145); 
                color: white; 
                border-radius: 25%;
            } 
            QPushButton:hover {
                background-color: rgb(14, 63, 92);
            }
            QPushButton:disabled {
                background-color: rgb(61, 127, 166);   
            }
        """)
        for number in self.new_ships:
            if self.new_ships[number] > 0:
                self.buttons_ships_list[number-1].setEnabled(True)
                self.buttons_ships_list[number-1].setStyleSheet("""
                QPushButton {
                    background-color: rgb(23, 101, 145);
                    color: white; 
                    border-radius: 15%;
                } 
                QPushButton:hover {
                    background-color: rgb(14, 63, 92);
                } 
                QPushButton:disabled {
                    background-color: rgb(61, 127, 166);
                }
            """)
        if self.new_ships == self.ships:
            self.delete_button.setEnabled(False)

    def delete_ship(self, x, y):
        self.size_ship += 1
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        self.player_buttons[x][y].setStyleSheet("""
        QPushButton {
            background-color: rgb(45, 141, 196);
        } 
        QPushButton:hover {
            background-color: Purple;
        }
        """)
        try:
            self.player_buttons[x][y].disconnect()
        except:
            pass
        self.player_buttons[x][y].setEnabled(False)
        self.player_grid[x][y] = 0
        for direct in directions:
            neighbor_x = x + direct[0]
            neighbor_y = y + direct[1]
            if 0 <= neighbor_x < self.grid_size and 0 <= neighbor_y < self.grid_size:
                if self.player_grid[neighbor_x][neighbor_y] <= -2:
                    self.player_grid[neighbor_x][neighbor_y] += 2
                elif self.player_grid[neighbor_x][neighbor_y] == 1:
                    self.delete_ship(neighbor_x, neighbor_y)

    def start_game(self):
        self.game = True
        self.width = 1200
        self.height = 800
        self.setGeometry(100, 100, self.width, self.height)
        self.setFixedSize(self.width, self.height)
        for buttons in self.computer_buttons:
            for button in buttons:
                button.show()
        for button in self.buttons_ships_list:
            button.hide()
        self.delete_button.hide()
        self.start_button.hide()
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.player_grid[i][j] <= -2:
                    self.player_grid[i][j] = 0
        

    def place_ships(self, grid):
        for size, count in self.ships.items():
            for _ in range(count):
                self.place_ship_randomly(grid, size)

    def place_ship_randomly(self, grid, size):
        placed = False
        while not placed:
            orientation = random.choice(['horizontal', 'vertical'])
            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)

            if orientation == 'horizontal':
                if y + size <= self.grid_size and all(grid[x][y + i] == 0 for i in range(size)) and self.check_adjacent(grid, x, y, size, orientation):
                    for i in range(size):
                        grid[x][y + i] = 1
                    placed = True
            else:
                if x + size <= self.grid_size and all(grid[x + i][y] == 0 for i in range(size)) and self.check_adjacent(grid, x, y, size, orientation):
                    for i in range(size):
                        grid[x + i][y] = 1
                    placed = True

    def check_adjacent(self, grid, x, y, size, orientation):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for i in range(size):
            if orientation == 'horizontal':
                check_x, check_y = x, y + i
            else:
                check_x, check_y = x + i, y
            for dx, dy in directions:
                adj_x, adj_y = check_x + dx, check_y + dy
                if 0 <= adj_x < self.grid_size and 0 <= adj_y < self.grid_size:
                    if grid[adj_x][adj_y] == 1:
                        return False
        return True

    def player_turn(self, x, y):
        if self.computer_grid[x][y] == 1:
            self.computer_buttons[x][y].setStyleSheet("background-color: red;")
            self.computer_grid[x][y] = -1
            self.check_sink(self.computer_grid, x, y, self.computer_buttons)
            self.computer_buttons[x][y].setEnabled(False)
            if self.check_game_over(self.computer_grid):
                self.end_game("Вы выиграли!")
        else:
            self.computer_buttons[x][y].setStyleSheet("background-color: blue;")
            self.computer_grid[x][y] = -2
            for buttons in self.computer_buttons:
                for button in buttons:
                    button.setEnabled(False)
            self.timer.start()

    def computer_turn(self):
        self.timer.stop()
        x, y = -1, -1
        while True:
            if not self.computer_moves:
                x, y = random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
            elif self.computer_direction_horizon == None:
                directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                selection = random.choice(directions)
                x, y = self.computer_moves[0][0] + selection[0], self.computer_moves[0][1]+selection[1]
            else:
                selection = random.choice(self.computer_moves)
                if self.computer_direction_horizon:
                    directions = [1,-1]
                    x, y = selection[0] + random.choice(directions), selection[1]
                else:
                    directions = [1,-1]
                    x, y = selection[0], selection[1] + random.choice(directions)
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                if self.player_grid[x][y] >= 0:
                    if self.player_grid[x][y] == 1:
                        self.player_buttons[x][y].setStyleSheet("background-color: red;")
                        self.player_grid[x][y] = -1
                        self.computer_moves.append([x, y])
                        if len(self.computer_moves) == 2:
                            self.computer_direction_horizon = self.computer_moves[0][0] != self.computer_moves[1][0]
                        if self.check_sink(self.player_grid, x, y, self.player_buttons):
                            self.computer_moves = []
                            self.computer_direction_horizon = None
                            if self.check_game_over(self.player_grid):
                                self.end_game("Компьютер выиграл!")
                        self.timer.start()
                    else:
                        self.player_buttons[x][y].setStyleSheet("background-color: blue;")
                        self.player_grid[x][y] = -2
                        for buttons in self.computer_buttons:
                            for button in buttons:
                                button.setEnabled(True)
                    break


    def check_sink(self, grid, x, y, buttons):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        ship_parts = []
        for dx, dy in directions:
            nx, ny = x, y
            while 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                if grid[nx][ny] == 1:
                    return False
                if grid[nx][ny] == -1:
                    if not (nx, ny) in ship_parts:
                        ship_parts.append((nx, ny))
                    nx += dx
                    ny += dy
                else:
                    break
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for ship in ship_parts:
            buttons[ship[0]][ship[1]].setStyleSheet("background-color: rgb(0, 0, 139);")
            for direct in directions:
                neighbor_x = ship[0] + direct[0]
                neighbor_y = ship[1] + direct[1]
                if 0 <= neighbor_x < self.grid_size and 0 <= neighbor_y < self.grid_size:
                    if grid[neighbor_x][neighbor_y] == 0:
                        buttons[neighbor_x][neighbor_y].setStyleSheet("background-color: blue;")
                        grid[neighbor_x][neighbor_y] = -2
                        buttons[neighbor_x][neighbor_y].setEnabled(False)
        return True
        

    def check_game_over(self, grid):
        return all(cell != 1 for row in grid for cell in row)

    def end_game(self, message):
        self.messege_box = QMessageBox()
        self.messege_box.setWindowTitle('Конец')
        self.messege_box.setText(message)
        self.messege_box.setStyleSheet("""
        QMessageBox {
            background-color: #f0f0f0;
            border: 2px solid #0078d7; 
        }
        QMessageBox QLabel {
            color: #333;
            font-size: 14px;
        }
        QMessageBox QPushButton {
            background-color: #0078d7;
            color: white;
        }
        QMessageBox QPushButton:hover {
        }
        """)
        self.messege_box.setWindowIcon(QIcon('icon.ico'))
        self.messege_box.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = BattleshipGame()
    game.show()
    sys.exit(app.exec_())