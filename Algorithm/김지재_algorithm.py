import numpy as np
import time

class OthelloGame:
    EMPTY, BLACK, WHITE = 0, 1, 2
    DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),          (0, 1),
                  (1, -1),  (1, 0), (1, 1)]

    def __init__(self):
        self.board = np.zeros((8, 8), dtype=int)
        self.board[3, 3] = self.board[4, 4] = self.WHITE
        self.board[3, 4] = self.board[4, 3] = self.BLACK
        self.current_player = self.BLACK

    def in_bounds(self, x, y):
        return 0 <= x < 8 and 0 <= y < 8

    def get_opponent(self, player):
        return self.BLACK if player == self.WHITE else self.WHITE

    def is_valid_move(self, x, y, player):
        if self.board[x, y] != self.EMPTY:
            return False
        opponent = self.get_opponent(player)
        for dx, dy in self.DIRECTIONS:
            nx, ny = x + dx, y + dy
            has_opponent_between = False
            while self.in_bounds(nx, ny) and self.board[nx, ny] == opponent:
                nx += dx
                ny += dy
                has_opponent_between = True
            if has_opponent_between and self.in_bounds(nx, ny) and self.board[nx, ny] == player:
                return True
        return False

    def get_valid_moves(self, player):
        return [(i, j) for i in range(8) for j in range(8) if self.is_valid_move(i, j, player)]

    def apply_move(self, x, y, player):
        self.board[x, y] = player
        opponent = self.get_opponent(player)
        for dx, dy in self.DIRECTIONS:
            nx, ny = x + dx, y + dy
            path = []
            while self.in_bounds(nx, ny) and self.board[nx, ny] == opponent:
                path.append((nx, ny))
                nx += dx
                ny += dy
            if path and self.in_bounds(nx, ny) and self.board[nx, ny] == player:
                for px, py in path:
                    self.board[px, py] = player

    def count_flippable(self, x, y, player):
        opponent = self.get_opponent(player)
        count = 0
        for dx, dy in self.DIRECTIONS:
            nx, ny = x + dx, y + dy
            line = []
            while self.in_bounds(nx, ny) and self.board[nx, ny] == opponent:
                line.append((nx, ny))
                nx += dx
                ny += dy
            if line and self.in_bounds(nx, ny) and self.board[nx, ny] == player:
                count += len(line)
        return count

    def select_best_move(self, player):
        moves = self.get_valid_moves(player)
        if not moves:
            return None

        corner_positions = {(0,0), (0,7), (7,0), (7,7)}
        edge_positions = set([(0, i) for i in range(8)] + [(7, i) for i in range(8)] +
                             [(i, 0) for i in range(8)] + [(i, 7) for i in range(8)])

        def move_score(x, y):
            score = 0
            if (x, y) in corner_positions:
                score += 100
            elif (x, y) in edge_positions:
                score += 10
            score += self.count_flippable(x, y, player)
            return score

        best_move = max(moves, key=lambda move: move_score(*move))
        return best_move

    def count_stones(self):
        black = np.sum(self.board == self.BLACK)
        white = np.sum(self.board == self.WHITE)
        return black, white

    def print_board(self):
        print("  A B C D E F G H")
        for i in range(8):
            row = [".", "B", "W"]
            print(f"{i+1} " + " ".join(row[self.board[i, j]] for j in range(8)))

    def is_game_over(self):
        return not self.get_valid_moves(self.BLACK) and not self.get_valid_moves(self.WHITE)

    def play_turn(self):
        start_time = time.time()
        moves = self.get_valid_moves(self.current_player)
        if not moves:
            print(f"Player {self.current_player} has no valid moves. Turn skipped.")
            self.current_player = self.get_opponent(self.current_player)
            return
        move = self.select_best_move(self.current_player)
        if move:
            x, y = move
            self.apply_move(x, y, self.current_player)
        self.current_player = self.get_opponent(self.current_player)
        if time.time() - start_time > 10:
            raise TimeoutError("Algorithm exceeded time limit.")

    def play_game(self):
        while not self.is_game_over():
            self.print_board()
            self.play_turn()
        self.print_board()
        black, white = self.count_stones()
        print("Game Over.")
        print(f"Black: {black}, White: {white}")
        if black > white:
            print("Black wins!")
        elif white > black:
            print("White wins!")
        else:
            print("It's a tie!")

if __name__ == "__main__":
    game = OthelloGame()
    game.play_game()
