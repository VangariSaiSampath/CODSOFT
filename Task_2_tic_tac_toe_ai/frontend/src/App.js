import React, { useState, useEffect } from 'react';
import './App.css';
import backgroundImage from './assets/image_2.png';

const App = () => {
  const [board, setBoard] = useState(Array(9).fill(""));
  const [isHumanTurn, setIsHumanTurn] = useState(true); // Human always starts (X)
  const [winnerInfo, setWinnerInfo] = useState({ winner: null, line: [] });
  const [error, setError] = useState(null);

  const lines = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];

  const checkGameOver = (currentBoard) => {
    for (let [a, b, c] of lines) {
      if (currentBoard[a] && currentBoard[a] === currentBoard[b] && currentBoard[a] === currentBoard[c]) {
        return { winner: currentBoard[a], line: [a, b, c] };
      }
    }
    if (!currentBoard.includes("")) return { winner: "Draw", line: [] };
    return { winner: null, line: [] };
  };

  const handleClick = async (i) => {
    if (board[i] || winnerInfo.winner || !isHumanTurn) return;

    const newBoard = [...board];
    newBoard[i] = "X";
    setBoard(newBoard);
    setIsHumanTurn(false); 

    const gameResult = checkGameOver(newBoard);
    setWinnerInfo(gameResult);
  };

  useEffect(() => {
    if (!isHumanTurn && !winnerInfo.winner) {
      setError(null);
      fetchMove(board);
    }
  }, [isHumanTurn, winnerInfo, board]);

  const fetchMove = async (currentBoard) => {
    try {
      const response = await fetch("https://task-2-tic-tac-toe-ai.onrender.com", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ board: currentBoard }) 
      });

      if (!response.ok) {
        throw new Error(`AI API error: ${response.status} - ${response.statusText}`);
      }

      const data = await response.json();

      if (data.bestMove !== undefined && data.bestMove !== -1) {
        setBoard(prevBoard => {
          const nextBoard = [...prevBoard];
          nextBoard[data.bestMove] = "O";
          
          const gameResult = checkGameOver(nextBoard);
          setWinnerInfo(gameResult);
          
          return nextBoard;
        });
      }

      setIsHumanTurn(true);

    } catch (err) {
      setError("AI is thinking... but the server isn't responding. Check backend!");
      console.error("Fetch failed:", err);
      setIsHumanTurn(true); 
    }
  };

  const resetGame = () => {
    setBoard(Array(9).fill(""));
    setIsHumanTurn(true);
    setWinnerInfo({ winner: null, line: [] });
    setError(null);
  };

  const getStatusMessage = () => {
    if (error) return error;
    if (winnerInfo.winner) {
      return winnerInfo.winner === "Draw" ? "It's a Tie!" : `Unbeatable AI Wins! (Human 'X' vs AI 'O')`;
    }
    return isHumanTurn ? "Your Turn (X)" : "AI is calculating... (O)";
  };

  const appStyle = {
    backgroundImage: `url(${backgroundImage})`,
  };

  return (
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
            disabled={value || winnerInfo.winner || !isHumanTurn} 
          >
            {value && <span className={`piece ${value}`}>{value}</span>}
          </button>
        ))}
      </div>

      {(winnerInfo.winner || error) && (
        <button className="reset-btn" onClick={resetGame}>Reset Game</button>
      )}

      {/* Watermark */}
      <div className="watermark">Developed by Vangari Sai Sampath</div>
    </div>
  );
};

export default App;
