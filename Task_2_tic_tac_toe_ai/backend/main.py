from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Tuple
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GameState(BaseModel):
    board: List[str] 

def check_winner(board: List[str]) -> Tuple[Optional[str], List[int]]:
    win_cond = [(0,1,2), (3,4,5), (6,7,8), 
                (0,3,6), (1,4,7), (2,5,8), 
                (0,4,8), (2,4,6)]           
    for a, b, c in win_cond:
        if board[a] == board[b] == board[c] and board[a] != "":
            return board[a], [a, b, c]
    if "" not in board: return "Tie", []
    return None, []


def minimax(board: List[str], depth: int, alpha: float, beta: float, is_maximizing: bool) -> int:
    winner, _ = check_winner(board)
    if winner == "O": return 10 - depth  
    if winner == "X": return depth - 10  
    if winner == "Tie": return 0         

    if is_maximizing: 
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
    else: 
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
    
    for i in range(9):
        if board[i] == "":
            board[i] = "O" 
            score = minimax(board, 0, -math.inf, math.inf, False) 
            board[i] = "" 
            
            if score > best_score:
                best_score = score
                best_move = i
                
    return {"bestMove": best_move}

@app.get("/")
def read_root():
    return {"status": "Unbeatable Tic-Tac-Toe AI Backend is operational."}
