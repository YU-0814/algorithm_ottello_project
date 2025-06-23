import time
import copy # deepcopy를 위해 필요
import random

# ▶️ 상수 정의
EMPTY, BLACK, WHITE = 0, 1, -1

# ▶️ Zobrist Hashing을 위한 상수 초기화 (리스트 사용)
ZOBRIST_TABLE = [[[0 for _ in range(2)] for _ in range(8)] for _ in range(8)]
for r in range(8):
    for c in range(8):
        # 0 for BLACK (ZOBRIST_TABLE[r][c][0]), 1 for WHITE (ZOBRIST_TABLE[r][c][1])
        ZOBRIST_TABLE[r][c][0] = random.getrandbits(64) # BLACK 조각 해시
        ZOBRIST_TABLE[r][c][1] = random.getrandbits(64) # WHITE 조각 해시

# ▶️ 전치표 (Transposition Table) - 전역 딕셔너리로 관리
# Key: board_hash (64bit int), Value: (score, best_move, depth, node_type)
# node_type: EXACT, ALPHA, BETA
TT = {} # Transposition Table
TT_EXACT, TT_ALPHA, TT_BETA = 0, 1, 2 # 전치표 노드 타입 정의

# 킬러 무브 - 각 깊이에서 가장 좋은 프루닝 수를 저장
KILLER_MOVES = {}
for d in range(15): # Max search depth + a few extra for safety
    KILLER_MOVES[d] = [(-1, -1), (-1, -1)]

# 히스토리 휴리스틱 - 각 수에 대한 점수를 저장 (리스트 사용)
HISTORY_HEURISTIC = [[0 for _ in range(8)] for _ in range(8)]


# ▶️ 상대 색 반환
def opponent(color):
    return -color

# ▶️ 유효한 수 검사
def is_valid_move(board, row, col, color):
    if not (0 <= row < 8 and 0 <= col < 8): # 보드 범위 검사 추가
        return False
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

# ▶️ 유효한 수 목록 가져오기
def get_valid_moves(board, color):
    moves = []
    for r in range(8):
        for c in range(8):
            if is_valid_move(board, r, c, color):
                moves.append((r, c))
    return moves

# ▶️ 수 실행
def make_move(board, row, col, color):
    new_board = copy.deepcopy(board) # 리스트의 깊은 복사
    new_board[row][col] = color # 새로운 조각 놓기

    directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    for dr, dc in directions:
        r, c = row + dr, col + dc
        count = 0
        temp_flips = []
        while 0 <= r < 8 and 0 <= c < 8 and new_board[r][c] == opponent(color):
            temp_flips.append((r, c))
            r += dr
            c += dc
            count += 1
        if count > 0 and 0 <= r < 8 and 0 <= c < 8 and new_board[r][c] == color:
            for fr, fc in temp_flips:
                new_board[fr][fc] = color
    return new_board

# ▶️ Zobrist 해싱
def hash_board(board):
    h = 0
    for r in range(8):
        for c in range(8):
            if board[r][c] == BLACK:
                h ^= ZOBRIST_TABLE[r][c][0]
            elif board[r][c] == WHITE:
                h ^= ZOBRIST_TABLE[r][c][1]
    return h

# ▶️ 보드 평가 가중치 (리스트 사용)
WEIGHTS = [
    [120, -20, 20, 5, 5, 20, -20, 120],
    [-20, -40, -5, -5, -5, -5, -40, -20],
    [20, -5, 15, 3, 3, 15, -5, 20],
    [5, -5, 3, 3, 3, 3, -5, 5],
    [5, -5, 3, 3, 3, 3, -5, 5],
    [20, -5, 15, 3, 3, 15, -5, 20],
    [-20, -40, -5, -5, -5, -5, -40, -20],
    [120, -20, 20, 5, 5, 20, -20, 120]
]

# ▶️ 보드 평가 함수
def evaluate_strong(board, color):
    score = 0
    num_my_pieces = 0
    num_opponent_pieces = 0

    # 1. 위치 점수 계산
    for r in range(8):
        for c in range(8):
            if board[r][c] == color:
                score += WEIGHTS[r][c]
                num_my_pieces += 1
            elif board[r][c] == opponent(color):
                score -= WEIGHTS[r][c]
                num_opponent_pieces += 1

    # 2. 이동 가능성 (Mobility) 점수
    my_mobility = len(get_valid_moves(board, color))
    opponent_mobility = len(get_valid_moves(board, opponent(color)))
    score += (my_mobility - opponent_mobility) * 10

    # 3. 코너 및 변 제어 점수
    corners = [(0,0), (0,7), (7,0), (7,7)]
    for r, c in corners:
        if board[r][c] == color:
            score += 100
        elif board[r][c] == opponent(color):
            score -= 100
    
    # 4. 조각 수 차이
    piece_diff = num_my_pieces - num_opponent_pieces
    score += piece_diff * 5

    return score

# ▶️ 미니맥스 (Minimax) 알고리즘 (PVS, 알파-베타 프루닝, 전치표, 킬러 무브, 히스토리 휴리스틱 포함)
def minimax(board, depth, alpha, beta, maximizing, color, global_start_time, total_time_limit, current_ply_depth):
    # Time limit check
    if time.time() - global_start_time > total_time_limit:
        return 0, (-1, -1) # 시간 초과 시 0점과 유효하지 않은 수 반환

    board_hash = hash_board(board)

    # Transposition Table check
    if board_hash in TT:
        entry_score, entry_move, entry_depth, entry_type = TT[board_hash]
        if entry_depth >= depth:
            if entry_type == TT_EXACT:
                return entry_score, entry_move
            elif entry_type == TT_ALPHA and entry_score > alpha:
                alpha = entry_score
            elif entry_type == TT_BETA and entry_score < beta:
                beta = entry_score
            if alpha >= beta:
                return entry_score, entry_move

    if depth == 0:
        score = evaluate_strong(board, color)
        TT[board_hash] = (score, (-1, -1), depth, TT_EXACT)
        return score, (-1, -1)

    valid_moves = get_valid_moves(board, color)

    if not valid_moves:
        opponent_moves = get_valid_moves(board, opponent(color))
        if not opponent_moves:
            score_black, score_white = count_pieces(board)
            if score_black > score_white:
                final_score = float('inf') if color == BLACK else float('-inf')
            elif score_white > score_black:
                final_score = float('-inf') if color == BLACK else float('inf')
            else:
                final_score = 0
            TT[board_hash] = (final_score, (-1,-1), depth, TT_EXACT)
            return final_score, (-1,-1)
        else:
            score_pass, move_pass = minimax(board, depth, alpha, beta, not maximizing, opponent(color), global_start_time, total_time_limit, current_ply_depth + 1)
            TT[board_hash] = (score_pass, move_pass, depth, TT_EXACT)
            return score_pass, move_pass

    best_move = (-1, -1)
    
    # ▶️ 무브 오더링: 전치표, 킬러 무브, 히스토리 휴리스틱 순으로 정렬
    ordered_moves = []

    # 1. Transposition table move
    if board_hash in TT and TT[board_hash][1] != (-1, -1):
        tt_move = TT[board_hash][1]
        if tt_move in valid_moves: # Ensure it's still a valid move
            ordered_moves.append(tt_move)
            valid_moves.remove(tt_move) # Remove to avoid duplication

    # 2. Killer moves
    if current_ply_depth in KILLER_MOVES:
        for km in KILLER_MOVES[current_ply_depth]:
            if km != (-1, -1) and km in valid_moves and km not in ordered_moves:
                ordered_moves.append(km)
                valid_moves.remove(km)

    # 3. History heuristic and remaining moves
    sorted_remaining_moves = sorted(valid_moves, key=lambda move: HISTORY_HEURISTIC[move[0]][move[1]], reverse=True)
    ordered_moves.extend(sorted_remaining_moves)

    if maximizing:
        max_eval = float('-inf')
        for move in ordered_moves:
            r, c = move
            new_board = make_move(board, r, c, color)
            
            # PVS (Principal Variation Search) / NegaScout 적용
            if move == ordered_moves[0]:
                evaluation, _ = minimax(new_board, depth - 1, alpha, beta, False, opponent(color), global_start_time, total_time_limit, current_ply_depth + 1)
            else:
                evaluation, _ = minimax(new_board, depth - 1, alpha, alpha + 1, False, opponent(color), global_start_time, total_time_limit, current_ply_depth + 1)
                if alpha < evaluation < beta:
                    evaluation, _ = minimax(new_board, depth - 1, evaluation, beta, False, opponent(color), global_start_time, total_time_limit, current_ply_depth + 1)

            if evaluation > max_eval:
                max_eval = evaluation
                best_move = move
            alpha = max(alpha, evaluation)
            
            if beta <= alpha:
                # Beta cutoff occurred: This move is a candidate for Killer Move
                if move != (-1, -1):
                    if move not in KILLER_MOVES[current_ply_depth]: # Avoid duplicates
                        KILLER_MOVES[current_ply_depth].insert(0, move)
                        KILLER_MOVES[current_ply_depth] = KILLER_MOVES[current_ply_depth][:2]
                    HISTORY_HEURISTIC[r][c] += depth * depth 
                TT[board_hash] = (max_eval, best_move, depth, TT_BETA)
                return max_eval, best_move
        TT[board_hash] = (max_eval, best_move, depth, TT_EXACT)
        return max_eval, best_move
    else: # Minimizing
        min_eval = float('inf')
        for move in ordered_moves:
            r, c = move
            new_board = make_move(board, r, c, color)
            
            # PVS (Principal Variation Search) / NegaScout 적용
            if move == ordered_moves[0]:
                evaluation, _ = minimax(new_board, depth - 1, alpha, beta, True, opponent(color), global_start_time, total_time_limit, current_ply_depth + 1)
            else:
                evaluation, _ = minimax(new_board, depth - 1, beta - 1, beta, True, opponent(color), global_start_time, total_time_limit, current_ply_depth + 1)
                if alpha < evaluation < beta:
                    evaluation, _ = minimax(new_board, depth - 1, alpha, evaluation, True, opponent(color), global_start_time, total_time_limit, current_ply_depth + 1)

            if evaluation < min_eval:
                min_eval = evaluation
                best_move = move
            beta = min(beta, evaluation)
            
            if beta <= alpha:
                # Alpha cutoff occurred: This move is a candidate for Killer Move
                if move != (-1, -1):
                    if move not in KILLER_MOVES[current_ply_depth]: # Avoid duplicates
                        KILLER_MOVES[current_ply_depth].insert(0, move)
                        KILLER_MOVES[current_ply_depth] = KILLER_MOVES[current_ply_depth][:2]
                    HISTORY_HEURISTIC[r][c] += depth * depth
                TT[board_hash] = (min_eval, best_move, depth, TT_ALPHA)
                return min_eval, best_move
        TT[board_hash] = (min_eval, best_move, depth, TT_EXACT)
        return min_eval, best_move

# ▶️ 보드 조각 개수 세기
def count_pieces(board):
    black_count = 0
    white_count = 0
    for r in range(8):
        for c in range(8):
            if board[r][c] == BLACK:
                black_count += 1
            elif board[r][c] == WHITE:
                white_count += 1
    return black_count, white_count

# ▶️ 문자열 <-> 수 변환 헬퍼 함수
def string_to_move(s):
    try:
        col_char = s[0].upper()
        col = ord(col_char) - ord('A')
        # 행은 1부터 8까지이므로 1을 빼서 0-7 인덱스로 변환
        row = int(s[1]) - 1 
        if not (0 <= row < 8 and 0 <= col < 8):
            raise ValueError
        return row, col
    except (IndexError, ValueError):
        return -1, -1 # 잘못된 입력

def move_to_string(row, col):
    if row == -1 and col == -1:
        return "PASS"
    # 행을 1을 더해서 1-8 숫자로 변환
    return f"{chr(ord('A') + col)}{row + 1}"

# ▶️ 메인 AI 함수
def ultimate_othello_ai(board, color, depth_limit=4, time_limit=10.0):
    global TT, KILLER_MOVES, HISTORY_HEURISTIC

    # Clear TT, Killer Moves, History Heuristic for a new AI turn (or new game)
    # Reset should ideally happen at the start of a new game.
    # For a turn-based AI, clearing these on each call might be too aggressive
    # and lose valuable information. If the intent is for persistent learning
    # across a single game, then these global clears should be moved
    # to a game initialization function. For this example, let's keep them
    # here as a common practice for independent AI calls, though it might
    # reduce effectiveness in a continuous game.
    TT.clear()
    for d in range(len(KILLER_MOVES)):
        KILLER_MOVES[d] = [(-1, -1), (-1, -1)]
    # HISTORY_HEURISTIC은 리스트의 리스트이므로 초기화 방식 변경
    for r in range(8):
        for c in range(8):
            HISTORY_HEURISTIC[r][c] = 0

    global_start_time = time.time()
    
    score, best_move = minimax(board, depth_limit, float('-inf'), float('inf'), True, color, global_start_time, time_limit, 0)
    
    if best_move == (-1, -1):
        valid_moves = get_valid_moves(board, color)
        if valid_moves:
            return random.choice(valid_moves) # Fallback to a random move if AI can't find a "best" one
        return None # No valid moves (pass)
    
    return best_move

# ▶️ 메인 실행 블록 (스크립트 직접 실행 시 동작)
if __name__ == "__main__":
    # 📌 보드 초기화 (Python 리스트의 리스트로 변경)
    board = [[EMPTY for _ in range(8)] for _ in range(8)]
    board[3][3], board[4][4] = WHITE, WHITE
    board[3][4], board[4][3] = BLACK, BLACK

    symbols = {EMPTY: ' .', BLACK: ' B', WHITE: ' W'} # 공백을 추가하여 정렬 맞추기

    # **여기부터 수정된 부분입니다.**
    def print_board(board):
        print("  A B C D E F G H") # Column headers (열 헤더)
        for r_idx, row_list in enumerate(board):
            # 행 번호를 1부터 8까지 표시하고, 각 셀 앞에 공백을 추가하여 정렬
            print(f"{r_idx + 1} {''.join(symbols[cell] for cell in row_list)}")

    print("🟢 오셀로 AI (순수 Python + 직관적인 인터페이스)")
    print("초기 보드:")
    print_board(board) # Use the new print_board function

    my_color = None
    while my_color is None:
        color_input = input("당신의 색 (B 또는 W): ").strip().upper()
        if color_input == 'B':
            my_color = BLACK
        elif color_input == 'W':
            my_color = WHITE
        else:
            print("잘못된 입력입니다. 'B' 또는 'W'를 입력해주세요.")

    current_player = BLACK # 흑돌이 먼저 시작

    # 📌 게임 루프 시작
    while True:
        print("\n현재 보드:")
        print_board(board) # Use the new print_board function

        black_score, white_score = count_pieces(board)
        print(f"점수: 흑 {black_score}, 백 {white_score}")

        valid_moves_current_player = get_valid_moves(board, current_player)
        
        # ▶️ 게임 종료 조건 체크
        if not valid_moves_current_player:
            valid_moves_opponent = get_valid_moves(board, opponent(current_player))
            if not valid_moves_opponent:
                print("게임 종료! 양쪽 모두 둘 수 있는 수가 없습니다.")
                if black_score > white_score:
                    print("흑 승리!")
                elif white_score > black_score:
                    print("백 승리!")
                else:
                    print("무승부!")
                break
            else:
                print(f"플레이어 {symbols[current_player].strip()}는 둘 수 있는 곳이 없어 턴을 패스합니다.") # 공백 제거
                current_player = opponent(current_player)
                continue

        move = None
        if current_player == my_color:
            while True:
                valid_moves_str = [move_to_string(r, c) for r, c in valid_moves_current_player]
                # 사용자 입력 프롬프트 업데이트
                user_input = input(f"수를 입력해주세요 (예: A1, H8). 유효한 수: {valid_moves_str}: ").strip()
                row, col = string_to_move(user_input)
                if (row, col) in valid_moves_current_player: # 유효한 수인지 확인
                    move = (row, col)
                    break
                else:
                    print("❌ 유효하지 않은 수이거나 잘못된 형식입니다. 다시 입력해주세요 (예: A1, B2).")
        else: # AI 턴
            print(f"AI의 차례 ({symbols[current_player].strip()})") # 공백 제거
            start_time_ai = time.time()
            ai_move = ultimate_othello_ai(board, current_player, depth_limit=4, time_limit=10.0) # 깊이와 시간 제한 전달
            end_time_ai = time.time()

            if ai_move:
                move = ai_move
                print(f"🤖 AI가 둔 수: {move_to_string(move[0], move[1])} (계산 시간: {end_time_ai - start_time_ai:.2f} 초)")
            else:
                print("AI가 둘 수 있는 곳이 없어 패스합니다.")
                # AI가 수를 찾지 못했으나 실제 유효한 수가 있는 경우 (매우 드물겠지만)
                # 첫 번째 유효한 수로 강제 진행하거나, 무작위 선택
                if valid_moves_current_player:
                    move = random.choice(valid_moves_current_player)
                    print(f"🤖 AI가 무작위 유효한 수로 대체: {move_to_string(move[0], move[1])}")
                else:
                    move = None # 정말 둘 곳이 없음 (패스)
        
        if move:
            board = make_move(board, move[0], move[1], current_player)
        
        current_player = opponent(current_player) # 턴 넘기기