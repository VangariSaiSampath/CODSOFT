// frontend/src/App.js
import React, { useState, useEffect } from 'react';
import './App.css';
// 1. Import the background image
import backgroundImage from './assets/image_2.png';

const App = () => {
  const [board, setBoard] = useState(Array(9).fill(""));
  const [isHumanTurn, setIsHumanTurn] = useState(true); // Human always starts (X)
  const [winnerInfo, setWinnerInfo] = useState({ winner: null, line: [] });
  const [error, setError] = useState(null);

  const lines = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];

  // FUNCTION: Visual Winner Check
  const checkGameOver = (currentBoard) => {
    for (let [a, b, c] of lines) {
      if (currentBoard[a] && currentBoard[a] === currentBoard[b] && currentBoard[a] === currentBoard[c]) {
        return { winner: currentBoard[a], line: [a, b, c] };
      }
    }
    if (!currentBoard.includes("")) return { winner: "Draw", line: [] };
    return { winner: null, line: [] };
  };

  // Human click handler
  const handleClick = async (i) => {
    // Prevent move if square occupied, game over, or not human turn
    if (board[i] || winnerInfo.winner || !isHumanTurn) return;

    // Update board with human move (X)
    const newBoard = [...board];
    newBoard[i] = "X";
    setBoard(newBoard);
    setIsHumanTurn(false); // Relinquish turn to AI

    // Immediate check for human win or draw
    const gameResult = checkGameOver(newBoard);
    setWinnerInfo(gameResult);
  };

  // AI TURN EFFECT (Triggers when turn switches to AI)
  useEffect(() => {
    // Only call AI if it's the AI's turn AND the game isn't already over
    if (!isHumanTurn && !winnerInfo.winner) {
      setError(null);
      fetchMove(board);
    }
  }, [isHumanTurn, winnerInfo, board]);

  const fetchMove = async (currentBoard) => {
    try {
      // Correct API Endpoint and Payload structure
      const response = await fetch("http://localhost:8000/move", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ board: currentBoard }) // Must send the *current* state
      });

      if (!response.ok) {
        throw new Error(`AI API error: ${response.status} - ${response.statusText}`);
      }

      const data = await response.json();

      // If AI found a move, apply it (data.bestMove will be -1 on draws)
      if (data.bestMove !== undefined && data.bestMove !== -1) {
        setBoard(prevBoard => {
          const nextBoard = [...prevBoard];
          nextBoard[data.bestMove] = "O";
          
          // Check if AI move ended the game
          const gameResult = checkGameOver(nextBoard);
          setWinnerInfo(gameResult);
          
          return nextBoard;
        });
      }

      // Restore turn to Human (if game isn't over)
      setIsHumanTurn(true);

    } catch (err) {
      setError("AI is thinking... but the server isn't responding. Check backend!");
      console.error("Fetch failed:", err);
      setIsHumanTurn(true); // Don't block human, though game is now inconsistent
    }
  };

  const resetGame = () => {
    setBoard(Array(9).fill(""));
    setIsHumanTurn(true);
    setWinnerInfo({ winner: null, line: [] });
    setError(null);
  };

  // Determine current status message
  const getStatusMessage = () => {
    if (error) return error;
    if (winnerInfo.winner) {
      return winnerInfo.winner === "Draw" ? "It's a Tie!" : `Unbeatable AI Wins! (Human 'X' vs AI 'O')`;
    }
    return isHumanTurn ? "Your Turn (X)" : "AI is calculating... (O)";
  };

  // 2. Set up the dynamic style for the background
  const appStyle = {
    backgroundImage: `url(${backgroundImage})`,
  };

  return (
    // 3. Apply the dynamic style to the main container
    <div className="App" style={appStyle}>
      <div className="header">
        <h1>AI Tic-Tac-Toe</h1>
        <p className="unbeatable-note">(Play against the AI player)</p>
      </div>

      <div className={`status ${winnerInfo.winner ? 'game-over' : isHumanTurn ? 'human-turn' : 'ai-turn'}`}>
        <h2>{getStatusMessage()}</h2>
      </div>

      <div className="game-board">
        {board.map((value, i) => (
          <button 
            key={i} 
            className={`square ${winnerInfo.line.includes(i) ? 'win-line' : ''}`} 
            onClick={() => handleClick(i)}
            disabled={value || winnerInfo.winner || !isHumanTurn} // Visual hint
          >
            {value && <span className={`piece ${value}`}>{value}</span>}
          </button>
        ))}
      </div>

      {(winnerInfo.winner || error) && (
        <button className="reset-btn" onClick={resetGame}>Reset Game</button>
      )}

      {/* 4. Add the Watermark */}
      <div className="watermark">Developed by Vangari Sai Sampath</div>
    </div>
  );
};

export default App;