import time
import copy
import random

# ▶️ 상수 정의
EMPTY, BLACK, WHITE = 0, 1, -1

# ▶️ 상대 색 반환
def opponent(color):
    return -color

# ▶️ 유효한 수 검사
def is_valid_move(board, row, col, color):
    if board[row][col] != EMPTY:
        return False
    directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    for dr, dc in directions:
        r, c = row + dr, col + dc
        count = 0
        while 0 <= r < 8 and 0 <= c < 8 and board[r][c] == opponent(color):
            r += dr
            c += dc
            count += 1
        if count > 0 and 0 <= r < 8 and 0 <= c < 8 and board[r][c] == color:
            return True
    return False

# ▶️ 가능한 모든 수 반환
def get_valid_moves(board, color):
    return [(r, c) for r in range(8) for c in range(8) if is_valid_move(board, r, c, color)]

# ▶️ 수를 실행한 후 보드 반환
def make_move(board, row, col, color):
    new_board = copy.deepcopy(board)
    new_board[row][col] = color
    directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    for dr, dc in directions:
        r, c = row + dr, col + dc
        flips = []
        while 0 <= r < 8 and 0 <= c < 8 and new_board[r][c] == opponent(color):
            flips.append((r, c))
            r += dr
            c += dc
        if 0 <= r < 8 and 0 <= c < 8 and new_board[r][c] == color:
            for fr, fc in flips:
                new_board[fr][fc] = color
    return new_board

# ▶️ 평가 함수 (Minimax용)
POSITION_WEIGHTS = [
    [100, -20, 10, 5, 5, 10, -20, 100],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [10, -2, 0, 0, 0, 0, -2, 10],
    [5, -2, 0, 0, 0, 0, -2, 5],
    [5, -2, 0, 0, 0, 0, -2, 5],
    [10, -2, 0, 0, 0, 0, -2, 10],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [100, -20, 10, 5, 5, 10, -20, 100],
]

def evaluate_strong(board, color):
    score = 0
    my_moves = get_valid_moves(board, color)
    opp_moves = get_valid_moves(board, opponent(color))
    mobility = len(my_moves) - len(opp_moves)
    for r in range(8):
        for c in range(8):
            if board[r][c] == color:
                score += POSITION_WEIGHTS[r][c]
            elif board[r][c] == opponent(color):
                score -= POSITION_WEIGHTS[r][c]
    corners = [(0,0), (0,7), (7,0), (7,7)]
    for r, c in corners:
        if board[r][c] == color:
            score += 100
        elif board[r][c] == opponent(color):
            score -= 100
    score += 5 * mobility
    return score

# ▶️ Minimax 알고리즘
def minimax(board, depth, alpha, beta, maximizing, color, start_time, eval_func):
    if depth == 0 or time.time() - start_time > 9.5:
        return eval_func(board, color), None
    valid_moves = get_valid_moves(board, color if maximizing else opponent(color))
    if not valid_moves:
        return eval_func(board, color), None
    best_move = None
    if maximizing:
        max_eval = float('-inf')
        for move in valid_moves:
            new_board = make_move(board, move[0], move[1], color)
            eval, _ = minimax(new_board, depth-1, alpha, beta, False, color, start_time, eval_func)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in valid_moves:
            new_board = make_move(board, move[0], move[1], opponent(color))
            eval, _ = minimax(new_board, depth-1, alpha, beta, True, color, start_time, eval_func)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

# ▶️ 랜덤 시뮬레이션으로 게임 끝까지 진행
def simulate_random_game(board, current_color):
    simulation_board = copy.deepcopy(board)
    color = current_color
    while True:
        moves = get_valid_moves(simulation_board, color)
        if moves:
            move = random.choice(moves)
            simulation_board = make_move(simulation_board, move[0], move[1], color)
        elif not get_valid_moves(simulation_board, opponent(color)):
            break
        color = opponent(color)
    black_score = sum(cell == BLACK for row in simulation_board for cell in row)
    white_score = sum(cell == WHITE for row in simulation_board for cell in row)
    if black_score > white_score:
        return BLACK
    elif white_score > black_score:
        return WHITE
    else:
        return 0  # 무승부

# ▶️ MCTS 알고리즘
def mcts(board, color, simulations_per_move=50):
    moves = get_valid_moves(board, color)
    if not moves:
        return None
    best_move = None
    best_score = -1
    for move in moves:
        win_count = 0
        for _ in range(simulations_per_move):
            new_board = make_move(board, move[0], move[1], color)
            result = simulate_random_game(new_board, opponent(color))
            if result == color:
                win_count += 1
        win_rate = win_count / simulations_per_move
        if win_rate > best_score:
            best_score = win_rate
            best_move = move
    return best_move

# ▶️ 최종 AI - Minimax + MCTS 혼합형
def ultimate_othello_ai(board, my_color):
    moves_played = sum(cell != EMPTY for row in board for cell in row)
    if moves_played < 20:
        # 초반에는 Minimax
        start_time = time.time()
        _, move = minimax(board, 4, float('-inf'), float('inf'), True, my_color, start_time, evaluate_strong)
        return move
    else:
        # 중반 이후에는 MCTS
        return mcts(board, my_color, simulations_per_move=60)

# ▶️ 콘솔 인터페이스
if __name__ == "__main__":
    board = [[EMPTY] * 8 for _ in range(8)]
    board[3][3], board[4][4] = WHITE, WHITE
    board[3][4], board[4][3] = BLACK, BLACK

    symbols = {EMPTY: '.', BLACK: 'B', WHITE: 'W'}

    print("🟢 오셀로 AI (Minimax + MCTS 혼합형)")
    for row in board:
        print(" ".join(symbols[cell] for cell in row))

    while True:
        color_input = input("당신의 색 (B 또는 W): ").strip().upper()
        my_color = BLACK if color_input == 'B' else WHITE if color_input == 'W' else None
        if my_color is not None:
            break

    while True:
        print("현재 보드:")
        for row in board:
            print(" ".join(symbols[cell] for cell in row))

        try:
            row = int(input("상대 수 - 행 (0~7): "))
            col = int(input("상대 수 - 열 (0~7): "))
            board = make_move(board, row, col, opponent(my_color))
        except:
            print("❌ 잘못된 입력입니다.")
            continue

        print("상대 수 반영 후:")
        for row in board:
            print(" ".join(symbols[cell] for cell in row))

        my_move = ultimate_othello_ai(board, my_color)
        if my_move:
            board = make_move(board, my_move[0], my_move[1], my_color)
            print(f"🤖 AI가 둔 수: {my_move}")
        else:
            print("둘 수 있는 곳이 없어 패스합니다.")

        print("수 실행 후 보드:")4
        
        for row in board:
            print(" ".join(symbols[cell] for cell in row))

        cont = input("계속하려면 Enter, 종료하려면 q 입력: ").strip().lower()
        if cont == 'q':
            break
