from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Tuple
import math

app = FastAPI()

# Enable CORS: CRITICAL FOR FRONTEND <-> BACKEND COMMUNICATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, set this to your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GameState(BaseModel):
    board: List[str] # Valid entries: "X", "O", ""

# DEFINITIVE CHECKER (HUMAN VISUALS vs AI LOGIC)
def check_winner(board: List[str]) -> Tuple[Optional[str], List[int]]:
    win_cond = [(0,1,2), (3,4,5), (6,7,8), # rows
                (0,3,6), (1,4,7), (2,5,8), # cols
                (0,4,8), (2,4,6)]           # diags
    for a, b, c in win_cond:
        if board[a] == board[b] == board[c] and board[a] != "":
            return board[a], [a, b, c]
    if "" not in board: return "Tie", []
    return None, []

# TRUE INVINCIBLE MINIMAX WITH ALPHA-BETA PRUNING
# AI is "O" (maximizing), Human is "X" (minimizing)
def minimax(board: List[str], depth: int, alpha: float, beta: float, is_maximizing: bool) -> int:
    winner, _ = check_winner(board)
    if winner == "O": return 10 - depth  # AI wins faster, better score
    if winner == "X": return depth - 10  # Human wins faster, worse AI score
    if winner == "Tie": return 0         # Tie is 0

    if is_maximizing: # AI (O) Turn
        best_score = -math.inf
        for i in range(9):
            if board[i] == "":
                board[i] = "O"
                score = minimax(board, depth + 1, alpha, beta, False)
                board[i] = ""
                best_score = max(score, best_score)
                alpha = max(alpha, score)
                if beta <= alpha: break
        return best_score
    else: # Human (X) Turn
        best_score = math.inf
        for i in range(9):
            if board[i] == "":
                board[i] = "X"
                score = minimax(board, depth + 1, alpha, beta, True)
                board[i] = ""
                best_score = min(score, best_score)
                beta = min(beta, score)
                if beta <= alpha: break
        return best_score

@app.post("/move")
def get_best_move(state: GameState):
    board = state.board
    best_score = -math.inf
    best_move = -1
    
    # Analyze all immediate options
    for i in range(9):
        if board[i] == "":
            board[i] = "O" # Simulate AI move
            score = minimax(board, 0, -math.inf, math.inf, False) # Look ahead
            board[i] = "" # Undo simulation
            
            if score > best_score:
                best_score = score
                best_move = i
                
    # If the board is full and no valid move is found, best_move will be -1
    return {"bestMove": best_move}

# Optional root endpoint for checking server status
@app.get("/")
def read_root():
    return {"status": "Unbeatable Tic-Tac-Toe AI Backend is operational."}