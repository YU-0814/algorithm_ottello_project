import time
import copy

EMPTY, BLACK, WHITE = 0, 1, -1

def opponent(color):
    return -color

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

def get_valid_moves(board, color):
    return [(r, c) for r in range(8) for c in range(8) if is_valid_move(board, r, c, color)]

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

def evaluate_strong(board, color):
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
    x_squares = [(0,1), (1,0), (1,1), (0,6), (1,6), (1,7), (6,0), (6,1), (7,1), (6,6), (6,7), (7,6)]
    for r, c in x_squares:
        if board[r][c] == color:
            score -= 30
        elif board[r][c] == opponent(color):
            score += 30
    score += 5 * mobility
    return score

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

def ultimate_othello_ai(board, my_color):
    start_time = time.time()
    moves_played = sum(1 for row in board for cell in row if cell != EMPTY)
    depth = 6 if moves_played < 50 else 8
    _, move = minimax(board, depth, float('-inf'), float('inf'), True, my_color, start_time, evaluate_strong)
    return move

def get_valid_coordinate(name):
    while True:
        value = input(f"상대가 둔 수 - {name} 번호 (0~7): ").strip()
        if value.isdigit():
            value = int(value)
            if 0 <= value < 8:
                return value
        print("⚠️  잘못된 입력입니다. 0~7 사이의 숫자를 입력하세요.")

if __name__ == "__main__":
    board = [[EMPTY]*8 for _ in range(8)]
    board[3][3], board[4][4] = WHITE, WHITE
    board[3][4], board[4][3] = BLACK, BLACK

    print("▶️ 궁극 AI 오셀로")
    symbols = {EMPTY: '.', BLACK: 'B', WHITE: 'W'}

    while True:
        color_input = input("당신의 색 (B 또는 W): ").strip().upper()
        my_color = BLACK if color_input == 'B' else WHITE if color_input == 'W' else None
        if my_color is not None:
            break

    if my_color == BLACK:
        print("흑이므로 선공입니다. AI가 먼저 둡니다.")
        my_move = ultimate_othello_ai(board, my_color)
        if my_move:
            board = make_move(board, my_move[0], my_move[1], my_color)
            print(f"내가 둔 첫 수: {my_move}")

    while True:
        print("\n현재 보드:")
        for row in board:
            print(" ".join(symbols[cell] for cell in row))

        enemy_color = opponent(my_color)
        enemy_moves = get_valid_moves(board, enemy_color)

        if enemy_moves:
            row = get_valid_coordinate("행")
            col = get_valid_coordinate("열")
            board = make_move(board, row, col, enemy_color)
            print("상대 수 반영 후:")
            for row in board:
                print(" ".join(symbols[cell] for cell in row))
        else:
            print("상대가 둘 수 있는 곳이 없습니다. 패스합니다.")

        my_moves = get_valid_moves(board, my_color)
        if my_moves:
            my_move = ultimate_othello_ai(board, my_color)
            board = make_move(board, my_move[0], my_move[1], my_color)
            print(f"내가 둔 수: {my_move}")
        else:
            print("둘 수 있는 곳이 없습니다. 패스합니다.")

        print("수 실행 후 보드:")
        for row in board:
            print(" ".join(symbols[cell] for cell in row))

        if not get_valid_moves(board, my_color) and not get_valid_moves(board, opponent(my_color)):
            print("\n🏁 게임 종료!")
            b = sum(r.count(BLACK) for r in board)
            w = sum(r.count(WHITE) for r in board)
            print(f"최종 결과 - 흑: {b}, 백: {w}")
            if b > w:
                print("🎉 흑 승리!")
            elif w > b:
                print("🎉 백 승리!")
            else:
                print("🤝 무승부!")
            break
445
