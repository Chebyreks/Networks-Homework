import sys, threading
import socket
import json
import time

class GameInstance:
    def __init__(self, start):
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.game_over = False
        if (start):
            self.my_symbol = "X"
            self.op_symbol = "O"
        else:
            self.my_symbol = "O"
            self.op_symbol = "X"
    
    def print_board(self):
        for row in self.board:
            print(" | ".join(row))
            print("-" * 9)
    
    def process_message(self, message):
        row = message['row']
        column = message['col']
        symbol = message['symbol']
        self.board[row][column] = symbol
        self.print_board()
        if message.get('game_over', True):
            if self.check_draw_condition():
                print("Игра закончилась: Ничья")
            else:
                print("Игра закончилась: Поражение")
            self.game_over = True
        self.current_player = self.my_symbol
        
    def check_win_condition(self):
        for row in self.board:
            if ''.join(row) == "XXX" or ''.join(row) == "OOO":
                return True
        for col in range(3):    
            if all(self.board[row][col] == self.my_symbol for row in range(3)):
                    return True

        if all(self.board[i][i] == self.my_symbol for i in range(3)):
            return True
        if all(self.board[i][2-i] == self.my_symbol for i in range(3)):
            return True
        return False
    
    def check_draw_condition(self):
        if all([self.board[i][j] == self.my_symbol or self.board[i][j] == self.op_symbol for j in range(3) for i in range(3)]):
            return True
        return False
    
    def check_cell(self, row, col):
        return self.board[row][col] == ' ' and (row <= 2 and row >= 0) and (col <= 2 and col >= 0)
    
    def make_move(self, row, col, symbol):
        self.board[row][col] = symbol
        self.print_board()
        self.current_player = self.op_symbol
    def run(self, node, start):
        from P2Pnode import P2Pnode # Костыль лютый
        if (start):
            print("Вы ходите первые (крестики)")
        else:
            print("Вы ходите вторыми (нолики)")
        while not self.game_over:
            if self.current_player == self.my_symbol:
                print("Введите ход в виде ряда и столбца через пробел")
                while True:
                    row, col = map(int, input().split(' '))
                    row -= 1
                    col -= 1
                    if self.check_cell(row, col):
                        break
                    else:
                        print("Неправильная ячейка, попробуй ещё раз")

                self.make_move(row, col, self.my_symbol)
                if self.check_win_condition() or self.check_draw_condition():
                    node.send_message({
                        'row': row, 
                        'col': col, 
                        'symbol': self.my_symbol,
                        'game_over': True
                    })
                    self.game_over = True
                    if self.check_draw_condition():
                        print("Игра закончилась: Ничья")
                    else:    
                        print("Игра закончилась: Победа")
                else:
                    node.send_message({
                        'row': row, 
                        'col': col, 
                        'symbol': self.my_symbol,
                        'game_over': False
                    })
                print("Ждём ход противника")
        node.end_connections()