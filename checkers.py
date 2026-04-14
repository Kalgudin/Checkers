



class CheckersBoard:
    def __init__(self):
        self.board = [[' ' for _ in range(8)] for _ in range(8)]
        self.setup_pieces()

    def setup_pieces(self):
        white1 = ['бш', ' ', 'бш', ' ', 'бш', ' ', 'бш', ' ']
        white2 = [' ', 'бш', ' ', 'бш', ' ', 'бш', ' ', 'бш']
        self.board[5] = white1.copy()
        self.board[6] = white2.copy()
        self.board[7] = white1.copy()

        black1 = ['ЧШ', ' ', 'ЧШ', ' ', 'ЧШ', ' ', 'ЧШ', ' ']
        black2 = [' ', 'ЧШ', ' ', 'ЧШ', ' ', 'ЧШ', ' ', 'ЧШ']
        self.board[0] = black2.copy()
        self.board[1] = black1.copy()
        self.board[2] = black2.copy()


    def display(self):
        print("\n    a    b    c    d    e    f    g    h")
        for i, row in enumerate(self.board):
            print(" ","─"*41)
            print(f"{8 - i}", end=" ")
            for cell in row:
                print(f"│", end=" ")
                if cell == ' ':
                    print("  ", end=" ")
                else:
                    print(cell, end=" ")
            print(f"│{8 - i}")

        print(" ", "─" * 41)
        print("    a    b    c    d    e    f    g    h")

    def move_piece(self, from_pos, to_pos):
        from_col = ord(from_pos[0]) - ord('a')
        from_row = 8 - int(from_pos[1])
        to_col = ord(to_pos[0]) - ord('a')
        to_row = 8 - int(to_pos[1])


        if self.board[from_row][from_col] == '  ':
            return False

        piece = self.board[from_row][from_col]
        self.board[from_row][from_col] = '  '
        self.board[to_row][to_col] = piece
        return True

    def get_piece_at(self, pos):
        col = ord(pos[0]) - ord('a')
        row = 8 - int(pos[1])
        return self.board[row][col]



board = CheckersBoard()
board.display()