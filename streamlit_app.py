


import streamlit as st
import numpy as np
import random
import time

st.set_page_config(page_title="Streamlit Tetris", layout="centered")
st.title("🟦 Streamlit 테트리스 게임")

# 테트리스 블록 정의
TETROMINOS = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
}
COLORS = {
    'I': '#00FFFF', 'O': '#FFD700', 'T': '#800080', 'S': '#00FF00', 'Z': '#FF0000', 'J': '#0000FF', 'L': '#FFA500'
}

BOARD_WIDTH = 10
BOARD_HEIGHT = 20

def new_board():
    return np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=int)

def new_piece():
    shape = random.choice(list(TETROMINOS.keys()))
    return {
        'shape': shape,
        'matrix': np.array(TETROMINOS[shape]),
        'row': 0,
        'col': BOARD_WIDTH // 2 - len(TETROMINOS[shape][0]) // 2
    }

def rotate_piece(piece):
    piece['matrix'] = np.rot90(piece['matrix'], -1)
    return piece

def collision(board, piece, dr=0, dc=0):
    mat = piece['matrix']
    r, c = piece['row'] + dr, piece['col'] + dc
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            if mat[i, j]:
                if r + i >= BOARD_HEIGHT or c + j < 0 or c + j >= BOARD_WIDTH:
                    return True
                if board[r + i, c + j]:
                    return True
    return False

def merge(board, piece):
    mat = piece['matrix']
    r, c = piece['row'], piece['col']
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            if mat[i, j]:
                board[r + i, c + j] = 1
    return board

def clear_lines(board):
    new_board = board.copy()
    lines = 0
    for i in range(BOARD_HEIGHT):
        if all(new_board[i]):
            new_board[1:i+1] = new_board[0:i]
            new_board[0] = 0
            lines += 1
    return new_board, lines

# 세션 상태 초기화

if 'board' not in st.session_state:
    st.session_state['board'] = new_board()
if 'piece' not in st.session_state:
    st.session_state['piece'] = new_piece()
if 'score' not in st.session_state:
    st.session_state['score'] = 0
if 'gameover' not in st.session_state:
    st.session_state['gameover'] = False
if 'last_tick' not in st.session_state:
    st.session_state['last_tick'] = time.time()

def draw_board(board, piece=None):
    temp_board = board.copy()
    if piece:
        mat = piece['matrix']
        r, c = piece['row'], piece['col']
        for i in range(mat.shape[0]):
            for j in range(mat.shape[1]):
                if mat[i, j]:
                    if 0 <= r + i < BOARD_HEIGHT and 0 <= c + j < BOARD_WIDTH:
                        temp_board[r + i, c + j] = 2
    html = "<div style='line-height:0.7;'>"
    for i in range(BOARD_HEIGHT):
        for j in range(BOARD_WIDTH):
            color = '#222'
            if temp_board[i, j] == 1:
                color = '#888'
            elif temp_board[i, j] == 2:
                color = COLORS[st.session_state['piece']['shape']]
            html += f"<span style='display:inline-block;width:20px;height:20px;background:{color};border:1px solid #333;'></span>"
        html += "<br>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

st.write(f"점수: {st.session_state['score']}")

if st.session_state['gameover']:
    st.error("게임 오버! 새로고침(F5)으로 재시작하세요.")
    draw_board(st.session_state['board'])
    st.stop()

draw_board(st.session_state['board'], st.session_state['piece'])


col1, col2, col3, col4 = st.columns(4)
with col1:
    left = st.button("◀️ 좌")
with col2:
    right = st.button("우 ▶️")
with col3:
    rotate = st.button("🔄 회전")
with col4:
    down = st.button("⬇️ 내리기")

piece = st.session_state['piece']
board = st.session_state['board']

# 버튼 조작
if left and not collision(board, piece, dc=-1):
    piece['col'] -= 1
if right and not collision(board, piece, dc=1):
    piece['col'] += 1
if rotate:
    old_matrix = piece['matrix'].copy()
    piece = rotate_piece(piece)
    if collision(board, piece):
        piece['matrix'] = old_matrix
if down:
    if not collision(board, piece, dr=1):
        piece['row'] += 1
    else:
        board = merge(board, piece)
        board, lines = clear_lines(board)
        st.session_state['score'] += lines * 100
        piece = new_piece()
        if collision(board, piece):
            st.session_state['gameover'] = True
        st.session_state['board'] = board
        st.session_state['piece'] = piece
        st.experimental_rerun()

# 1초마다 자동으로 블록 내리기
now = time.time()
if now - st.session_state['last_tick'] >= 1.0 and not st.session_state['gameover']:
    st.session_state['last_tick'] = now
    if not collision(board, piece, dr=1):
        piece['row'] += 1
    else:
        board = merge(board, piece)
        board, lines = clear_lines(board)
        st.session_state['score'] += lines * 100
        piece = new_piece()
        if collision(board, piece):
            st.session_state['gameover'] = True
        st.session_state['board'] = board
        st.session_state['piece'] = piece
        st.experimental_rerun()

st.session_state['piece'] = piece
st.session_state['board'] = board

# 자동 새로고침(1초마다)
st.experimental_rerun()
