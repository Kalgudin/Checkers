import sys

class CheckersBoard:
    def __init__(self):
        self.board = [[' ' for _ in range(8)] for _ in range(8)]
        self.current_player = 'white'  # 'white' или 'black'
        self.setup_pieces()

    def setup_pieces(self):
        # Белые шашки (снизу)
        white1 = ['бш', ' ', 'бш', ' ', 'бш', ' ', 'бш', ' ']
        white2 = [' ', 'бш', ' ', 'бш', ' ', 'бш', ' ', 'бш']
        self.board[5] = white1.copy()  # строка 3 снизу
        self.board[6] = white2.copy()  # строка 2 снизу
        self.board[7] = white1.copy()  # строка 1 снизу

        # Чёрные шашки (сверху)
        black1 = ['ЧШ', ' ', 'ЧШ', ' ', 'ЧШ', ' ', 'ЧШ', ' ']
        black2 = [' ', 'ЧШ', ' ', 'ЧШ', ' ', 'ЧШ', ' ', 'ЧШ']
        self.board[0] = black2.copy()  # строка 8
        self.board[1] = black1.copy()  # строка 7
        self.board[2] = black2.copy()  # строка 6

    # ----------------------------------------------------------------------
    # Вспомогательные методы для работы с доской и координатами
    # ----------------------------------------------------------------------
    def _coord_to_index(self, pos):
        """Преобразует строку вида 'a1' в (row, col)"""
        col = ord(pos[0]) - ord('a')
        row = 8 - int(pos[1])
        return row, col

    def _index_to_coord(self, row, col):
        """Преобразует (row, col) в строку 'a1'"""
        letter = chr(ord('a') + col)
        number = 8 - row
        return f"{letter}{number}"

    def _is_inside(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def _is_empty(self, row, col):
        return self.board[row][col] == ' '

    def _is_opponent(self, row, col, player):
        piece = self.board[row][col]
        if piece == ' ':
            return False
        if player == 'white':
            return piece in ('ЧШ', 'ЧД')
        else:
            return piece in ('бш', 'бд')

    def _is_king(self, piece):
        return piece in ('бд', 'ЧД')

    def _get_piece_color(self, piece):
        if piece in ('бш', 'бд'):
            return 'white'
        elif piece in ('ЧШ', 'ЧД'):
            return 'black'
        else:
            return None

    def _make_king(self, row, col):
        """Превращает шашку в дамку, если она достигла последней линии"""
        piece = self.board[row][col]
        if piece == 'бш' and row == 0:
            self.board[row][col] = 'бд'
            return True
        elif piece == 'ЧШ' and row == 7:
            self.board[row][col] = 'ЧД'
            return True
        return False

    # ----------------------------------------------------------------------
    # Методы для получения возможных ходов (один шаг)
    # ----------------------------------------------------------------------
    def _get_simple_moves_for_piece(self, row, col, player):
        """Возвращает список (to_row, to_col) для простых ходов (без взятия)"""
        moves = []
        piece = self.board[row][col]
        if piece == ' ':
            return moves
        color = self._get_piece_color(piece)
        if color != player:
            return moves

        # Направления для простых шашек: вперёд (и назад, если дамка)
        directions = []
        if self._is_king(piece):
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        else:
            if player == 'white':
                directions = [(-1, -1), (-1, 1)]  # белые ходят вверх (уменьшение row)
            else:
                directions = [(1, -1), (1, 1)]   # чёрные ходят вниз

        for dr, dc in directions:
            new_r, new_c = row + dr, col + dc
            if self._is_inside(new_r, new_c) and self._is_empty(new_r, new_c):
                moves.append((new_r, new_c))
        return moves

    def _get_captures_for_piece(self, row, col, player):
        """
        Возвращает список возможных взятий для одной шашки.
        Каждый элемент: (to_row, to_col, captured_row, captured_col)
        """
        captures = []
        piece = self.board[row][col]
        if piece == ' ':
            return captures
        color = self._get_piece_color(piece)
        if color != player:
            return captures

        # Направления для взятия (все 4 диагонали для всех)
        # Для простых шашек допустимо и вперёд, и назад (русские шашки)
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:
            # Клетка с шашкой противника
            mid_r, mid_c = row + dr, col + dc
            # Клетка, куда прыгаем
            land_r, land_c = row + 2*dr, col + 2*dc

            if (self._is_inside(mid_r, mid_c) and self._is_inside(land_r, land_c) and
                not self._is_empty(mid_r, mid_c) and self._is_opponent(mid_r, mid_c, player) and
                self._is_empty(land_r, land_c)):

                # Для простой шашки – проверка, что она не бьёт назад, если не дамка?
                # В русских шашках простые бьют и вперёд, и назад, так что всё ок.
                captures.append((land_r, land_c, mid_r, mid_c))

        # Если шашка дамка, нужно добавить длинные взятия
        if self._is_king(piece):
            for dr, dc in directions:
                # Ищем первую шашку противника на диагонали
                r, c = row + dr, col + dc
                while self._is_inside(r, c) and self._is_empty(r, c):
                    r += dr
                    c += dc
                # Если нашли шашку противника
                if self._is_inside(r, c) and self._is_opponent(r, c, player):
                    # За ней должны быть пустые клетки
                    jump_r, jump_c = r + dr, c + dc
                    while self._is_inside(jump_r, jump_c) and self._is_empty(jump_r, jump_c):
                        captures.append((jump_r, jump_c, r, c))
                        jump_r += dr
                        jump_c += dc
        return captures

    def _has_captures(self, player):
        """Есть ли у игрока хотя бы одно взятие на доске"""
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece != ' ' and self._get_piece_color(piece) == player:
                    if self._get_captures_for_piece(r, c, player):
                        return True
        return False

    def get_all_moves(self, player):
        """
        Возвращает список всех возможных ходов (одиночных перемещений).
        Каждый ход: (from_row, from_col, to_row, to_col, captured_row, captured_col)
        captured_* может быть None, если это не взятие.
        """
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece != ' ' and self._get_piece_color(piece) == player:
                    # Простые ходы (только если нет взятий)
                    if not self._has_captures(player):
                        for tr, tc in self._get_simple_moves_for_piece(r, c, player):
                            moves.append((r, c, tr, tc, None, None))
                    # Взятия
                    for tr, tc, cr, cc in self._get_captures_for_piece(r, c, player):
                        moves.append((r, c, tr, tc, cr, cc))
        return moves

    # ----------------------------------------------------------------------
    # Применение ходов
    # ----------------------------------------------------------------------
    def _apply_single_move(self, from_r, from_c, to_r, to_c, cap_r=None, cap_c=None):
        """
        Применяет одно перемещение (с возможным взятием).
        Возвращает True, если ход выполнен.
        """
        piece = self.board[from_r][from_c]
        if piece == ' ':
            return False
        # Перемещаем шашку
        self.board[to_r][to_c] = piece
        self.board[from_r][from_c] = ' '
        # Если было взятие, убираем побитую шашку
        if cap_r is not None and cap_c is not None:
            self.board[cap_r][cap_c] = ' '
        # Превращение в дамку
        self._make_king(to_r, to_c)
        return True

    def _can_continue_captures(self, row, col, player):
        """Может ли шашка на (row, col) продолжать бить (есть ли взятия)"""
        # Временно проверяем, есть ли взятия для этой шашки
        # (нужно учитывать, что шашка могла стать дамкой после предыдущего хода)
        captures = self._get_captures_for_piece(row, col, player)
        return len(captures) > 0

    def _validate_move_sequence(self, seq, player):
        """
        Проверяет корректность последовательности ходов.
        seq – список строк позиций, например ['a3', 'b4', 'd6'].
        Возвращает (bool, message, list_of_steps) где steps – список
        (from_r,from_c, to_r,to_c, cap_r,cap_c) для применения.
        """
        if len(seq) < 2:
            return False, "Необходимо указать как минимум начальную и конечную позицию", []

        # Проверяем, что все позиции корректны
        indices = []
        for pos in seq:
            if len(pos) != 2 or pos[0] not in 'abcdefgh' or pos[1] not in '12345678':
                return False, f"Неверный формат позиции: {pos}", []
            indices.append(self._coord_to_index(pos))

        # Проверяем первый ход
        from_r, from_c = indices[0]
        piece = self.board[from_r][from_c]
        if piece == ' ':
            return False, f"На клетке {seq[0]} нет шашки", []
        if self._get_piece_color(piece) != player:
            return False, f"Это не ваша шашка", []

        # Если у игрока есть взятия, то первый ход обязательно должен быть взятием
        must_capture = self._has_captures(player)
        steps = []
        current_r, current_c = from_r, from_c

        # Временная доска для проверки цепочки (копируем)
        import copy
        temp_board = CheckersBoard()
        temp_board.board = copy.deepcopy(self.board)
        temp_board.current_player = self.current_player

        # Вспомогательная функция для проверки одного шага на временной доске
        def try_step(temp, fr, fc, tr, tc):
            # Находим, есть ли взятие для этого хода
            for cap in temp._get_captures_for_piece(fr, fc, player):
                if cap[0] == tr and cap[1] == tc:
                    return (tr, tc, cap[2], cap[3])  # to, captured
            # Если нет взятия, проверяем простой ход (но если must_capture, то он не подойдёт)
            if not must_capture and (tr, tc) in temp._get_simple_moves_for_piece(fr, fc, player):
                return (tr, tc, None, None)
            return None

        for i in range(len(indices) - 1):
            fr, fc = indices[i]
            tr, tc = indices[i+1]
            # Ход должен начинаться с текущей позиции
            if fr != current_r or fc != current_c:
                return False, f"Ход {i+1} должен начинаться с позиции {temp_board._index_to_coord(current_r, current_c)}", []
            step = try_step(temp_board, fr, fc, tr, tc)
            if step is None:
                return False, f"Недопустимый ход {seq[i]} -> {seq[i+1]}", []
            # Применяем ход на временной доске
            tr, tc, cr, cc = step
            if not temp_board._apply_single_move(fr, fc, tr, tc, cr, cc):
                return False, f"Не удалось применить ход {seq[i]} -> {seq[i+1]}", []
            steps.append((fr, fc, tr, tc, cr, cc))
            current_r, current_c = tr, tc
            # После хода проверяем, можно ли продолжать бить
            # (если это было взятие, то проверяем)
            if cr is not None:
                # Если есть возможность продолжать, а ход не последний – продолжаем
                if i < len(indices) - 2 and not temp_board._can_continue_captures(current_r, current_c, player):
                    return False, f"После хода {seq[i+1]} нет возможности бить дальше, но вы указали следующий ход", []
                # Если это последний ход, но есть возможность бить дальше – ошибка
                if i == len(indices) - 2 and temp_board._can_continue_captures(current_r, current_c, player):
                    return False, f"Шашка на {seq[i+1]} может бить дальше, вы обязаны продолжить", []
            else:
                # Если это не взятие, то цепочка должна состоять из одного хода
                if len(indices) > 2:
                    return False, "Цепочка ходов допустима только для взятий", []
                # Если у игрока были взятия, то простой ход недопустим
                if must_capture:
                    return False, "У вас есть возможность взятия, вы обязаны бить", []

        # Всё корректно
        return True, "OK", steps

    def apply_move_sequence(self, seq, player):
        """Применяет последовательность ходов к реальной доске, меняет игрока."""
        ok, msg, steps = self._validate_move_sequence(seq, player)
        if not ok:
            return False, msg
        for step in steps:
            self._apply_single_move(*step)
        # Меняем игрока
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        return True, "Ход выполнен"

    def has_any_move(self, player):
        """Есть ли у игрока хотя бы один допустимый ход (простой или взятие)"""
        moves = self.get_all_moves(player)
        return len(moves) > 0

    def is_game_over(self):
        """Проверяет, закончена ли игра (у текущего игрока нет ходов)"""
        return not self.has_any_move(self.current_player)

    # ----------------------------------------------------------------------
    # Отображение доски
    # ----------------------------------------------------------------------
    def display(self):
        print("\n    a    b    c    d    e    f    g    h")
        for i, row in enumerate(self.board):
            print(" ", "─" * 41)
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

    # ----------------------------------------------------------------------
    # Методы для совместимости с оригиналом (можно удалить, но оставим)
    # ----------------------------------------------------------------------
    def move_piece(self, from_pos, to_pos):
        """Упрощённое перемещение без проверок (для совместимости)"""
        fr, fc = self._coord_to_index(from_pos)
        tr, tc = self._coord_to_index(to_pos)
        if self.board[fr][fc] == ' ':
            return False
        piece = self.board[fr][fc]
        self.board[fr][fc] = ' '
        self.board[tr][tc] = piece
        return True

    def get_piece_at(self, pos):
        r, c = self._coord_to_index(pos)
        return self.board[r][c]


# ----------------------------------------------------------------------
# Основной игровой цикл
# ----------------------------------------------------------------------
def main():
    board = CheckersBoard()
    print("Добро пожаловать в игру 'Русские шашки'!")
    print("Формат ввода хода: последовательность клеток, разделённых пробелами.")
    print("Примеры:")
    print("  a3 b4     - простой ход")
    print("  a3 c5     - взятие одной шашки")
    print("  a3 c5 e7  - цепочка взятий (обязательно все возможные)")
    print("  quit      - выход из игры")
    print()

    while True:
        board.display()
        player_name = "Белые" if board.current_player == 'white' else "Чёрные"
        print(f"\nХод {player_name}")

        # Проверяем, есть ли ходы у текущего игрока
        if board.is_game_over():
            winner = "Чёрные" if board.current_player == 'white' else "Белые"
            print(f"Игра окончена! {winner} победили (у противника нет ходов).")
            break

        # Запрос ввода
        user_input = input("Ваш ход: ").strip().lower()
        if user_input == 'quit':
            print("Выход из игры.")
            break

        parts = user_input.split()
        # Проверяем, что все части выглядят как координаты
        valid = True
        for p in parts:
            if len(p) != 2 or p[0] not in 'abcdefgh' or p[1] not in '12345678':
                valid = False
                break
        if not valid:
            print("Неверный формат. Используйте буквы a-h и цифры 1-8, например 'a3 b4'.")
            continue

        # Пытаемся применить последовательность
        success, msg = board.apply_move_sequence(parts, board.current_player)
        if success:
            print(msg)
        else:
            print(f"Ошибка: {msg}")

    print("Спасибо за игру!")


if __name__ == "__main__":
    main()