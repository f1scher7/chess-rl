import React from 'react';
import { Chess } from 'chess.js';
import { Outcome, PieceColor } from '../enums';


export const onDrop = (
    game: Chess,
    setFen: (fen: string) => void,
    setMoves: React.Dispatch<React.SetStateAction<string[]>>,
    sourceSquare: string,
    targetSquare: string,
): boolean => {
    try {
        const move = game.move({
            from: sourceSquare,
            to: targetSquare,
            promotion: 'q',
        });

        if (move) {
            const moveString: string = move.from + move.to + (move.promotion ? move.promotion : '');

            setFen(game.fen());
            setMoves((prev: string[]) => [...prev, moveString]);

            return true;
        }

        return false;
    } catch (e) {
        console.error(e);
        return false;
    }
};

export const isGameOver = (game: Chess): string => {
    if (game.isGameOver()) {
        if (game.isCheckmate()) {
            return game.turn() === 'b' ? PieceColor.White : PieceColor.Black;
        } else if (game.isStalemate() || game.isDraw() || game.isThreefoldRepetition() || game.isInsufficientMaterial()) {
            return Outcome.Draw;
        }
    }

    return '';
};

export const resetBoard = (
    gameRef: React.RefObject<Chess>,
    setFen: React.Dispatch<React.SetStateAction<string>>,
    setMoves: React.Dispatch<React.SetStateAction<string[]>>,
    setGroupedMoves: React.Dispatch<React.SetStateAction<string[][]>>,
    setCurrMoveIdx: React.Dispatch<React.SetStateAction<number>>,
    setIsAgentTurn:  React.Dispatch<React.SetStateAction<boolean>>,
    userColor: string,
): void => {
    gameRef.current = new Chess();
    setFen(gameRef.current.fen());
    setMoves([]);
    setGroupedMoves([]);
    setCurrMoveIdx(-1);
    setIsAgentTurn(userColor === PieceColor.Black);
};
