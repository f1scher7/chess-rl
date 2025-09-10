import React, { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';
import { SavedGameContent } from '../../models/models';
import '../../global.css';
import './ChessBoardPage.css';
import { generateGroupedMoves, retrieveEpisodeNumFromModelFileName } from '../../utils/utils';
import { isGameOver, onDrop, resetBoard } from '../../services/chessService';
import GameOverDialog from '../../components/dialogs/gameOverDialog';
import { GameOverResultText, PieceColor } from '../../enums';
import { fetchAgentMove } from '../../api/fetcher';


type ChessBoardPageProps = {
    isView: boolean;
};

const ChessBoardPage: React.FC<ChessBoardPageProps> = ({ isView }: ChessBoardPageProps) => {
    const location = useLocation();
    const navigate = useNavigate();

    const savedGameContent: SavedGameContent = location.state?.savedGameContent;
    const userColor: string = location.state?.userColor;
    const modelFileName: string = location.state?.modelFileName;

    const gameRef = useRef<Chess>(new Chess());
    const moveListSliderRef = useRef<HTMLDivElement | null>(null);
    const [fen, setFen] = useState<string>(gameRef.current.fen());
    const [moves, setMoves] = useState<string[]>(isView && savedGameContent ? savedGameContent.moves : []);
    const [groupedMoves, setGroupedMoves] = useState<string[][]>(isView && savedGameContent ? generateGroupedMoves(savedGameContent.moves) : []);
    const [currMoveIdx, setCurrMoveIdx] = useState<number>(-1);
    const [isAgentTurn, setIsAgentTurn] = useState<boolean>(!isView && userColor === PieceColor.Black);
    const [gameResult, setGameResult] = useState<string>('');
    const [gameResultText, setGameResultText] = useState<string>('');
    const [showGameOverDialog, setShowGameOverDialog] = useState<boolean>(false);

    const episodesPlayedByAgent: string = retrieveEpisodeNumFromModelFileName(modelFileName, isView);

    const incrMoveIdx = (isArrowListener: boolean): void => {
        if (currMoveIdx === -1) {
            setCurrMoveIdx(1);
        } else if ((currMoveIdx < moves.length && (isView || isArrowListener)) || (currMoveIdx <= moves.length && !isView && !isArrowListener)) {
            setCurrMoveIdx(currMoveIdx + 1);
        }
    };

    const handleDrop = (source: string, target: string): boolean => {
        const isLegalMove: boolean = onDrop(gameRef.current, setFen, setMoves, source, target);

        if (isLegalMove) {
            setGameResult(isGameOver(gameRef.current));
            incrMoveIdx(false);
            setIsAgentTurn(true);
        }

        return isLegalMove;
    };
    
    const handleCloseGameOverDialog = () => {
        setShowGameOverDialog(false);
    };

    useEffect(() => {
        if ((!savedGameContent && isView) || (!modelFileName && !userColor && !isView)) {
            navigate('/');
        }
    }, [savedGameContent, isView, navigate]);

    useEffect(() => {
        const game = new Chess();

        for (let i = 0; i < currMoveIdx; i++) {
            game.move(moves[i]);
        }

        setGroupedMoves(generateGroupedMoves(moves));

        gameRef.current = game;
        setFen(game.fen());
    }, [currMoveIdx]);

    useEffect(() => {
        (async () => {
            if (isAgentTurn && !gameResult && !isView) {
                try {
                    const data = await fetchAgentMove(modelFileName, fen);
                    if (data.move_str) {
                        setMoves((prev) => [...prev, data.move_str]);
                        incrMoveIdx(false);
                        setIsAgentTurn(false);
                    }
                } catch (e) {
                    console.error(e);
                    throw e;
                }
            }
        })();
    }, [isAgentTurn]);

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'ArrowLeft') {
                if (currMoveIdx === -1) {
                    setCurrMoveIdx(0);
                } else if (currMoveIdx > 0) {
                    setCurrMoveIdx(currMoveIdx - 1);
                }

            } else if (e.key === 'ArrowRight') {
                incrMoveIdx(true);
            }
        };

        window.addEventListener('keydown', handleKeyDown);

        return () => {
            window.removeEventListener('keydown', handleKeyDown);
        };
    }, [currMoveIdx]);

    useEffect(() => {
        if(moveListSliderRef.current) {
            const activeLi = moveListSliderRef.current.querySelector('.active');
            if (activeLi instanceof HTMLElement) {
                activeLi.scrollIntoView({
                    behavior: 'auto',
                    block: 'nearest',
                });
            }
        }
    }, [currMoveIdx, groupedMoves]);

    useEffect(() => {
        if (gameResult && !isView) {
            if (gameResult === 'draw') {
                setGameResultText(GameOverResultText.Draw);
            } else if (gameResult === userColor) {
                setGameResultText(GameOverResultText.Win);
            } else if (gameResult !== userColor) {
                setGameResultText(GameOverResultText.Lose);
            }

            setShowGameOverDialog(true);
        }
    }, [gameResult]);

    return (
        <div className="container-fluid home-bg d-flex align-items-center justify-content-center">
            <div className="row bg-light bg-opacity-75 rounded-3 shadow w-75">
                <div className="col-8 d-flex flex-column" style={{ height: '95vh' }}>
                    <div className="flex-column text-center mt-4">
                        {isView ? (
                            <>
                                <h2>Agents&apos; game</h2>
                                <h4>Result: {savedGameContent?.result}</h4>
                            </>
                        ) : (
                            <h2>Try to beat the Agent!</h2>
                        )}
                    </div>
                    <div className="d-flex flex-column flex-grow-1 align-items-center justify-content-center w-75 h-75 mt-1p mx-auto">
                        <div className="align-items-start w-100">
                            {isView ? (
                                <h5>Agent: Andrzej ({savedGameContent?.black_elo})</h5>
                            ) : (
                                <h5>{`Agent (${episodesPlayedByAgent} episodes played)`}</h5>
                            )}
                        </div>
                        <Chessboard
                            position={fen}
                            isDraggablePiece={({ piece }): boolean => {
                                if (isView) {
                                    return false;
                                } else {
                                    return piece.startsWith(userColor[0]);
                                }
                            }}
                            onPieceDrop={handleDrop}
                            boardOrientation={userColor === PieceColor.Black ? PieceColor.Black : PieceColor.White}
                            customDarkSquareStyle={{ backgroundColor: 'rgb(46, 51, 54, 0.5)' }}
                            customLightSquareStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.5)' }}
                        />
                        <div className="align-items-start w-100 mt-2">
                            {isView ? (
                                <h5>Agent: Kazimierz ({savedGameContent?.white_elo})</h5>
                            ) : (
                                <h5>You (+inf elo)</h5>
                            )}
                        </div>
                    </div>
                </div>
                <div className="col-4 d-flex align-items-center" style={{ height: '95vh' }}>
                    <div className="moves-div d-flex flex-column justify-content-center w-100 h-100">
                        <h4 className="mt-20p">Moves</h4>
                        {moves.length !== 0 ? (
                            <>
                                <div className="move-list" ref={moveListSliderRef}>
                                    {groupedMoves.map((pairOfMoves, pairIdx) => (
                                        <ul key={pairIdx} className="d-flex list-group list-group-horizontal">
                                            <li className="list-group-item">
                                                {pairIdx + 1}.
                                            </li>
                                            {pairOfMoves.map((move, moveIdx) => (
                                                <li key={moveIdx}
                                                    className={`list-group-item ${
                                                        (pairIdx * 2 === currMoveIdx - 1 && moveIdx === 0) ||
                                                        (pairIdx * 2 + 1 === currMoveIdx - 1 && moveIdx === 1) ? 'active' : ''
                                                    }`}
                                                    onClick={() => setCurrMoveIdx(pairIdx * 2 + moveIdx + 1)}
                                                    style={{ cursor: 'pointer' }}
                                                >
                                                    {move}
                                                </li>
                                            ))}
                                        </ul>
                                    ))}
                                </div>
                                <div className="d-flex w-100 mt-4">
                                    <button
                                        className={`btn btn-dark w-25 ${currMoveIdx < 1 ? 'disabled' : ''}`}
                                        onClick={() => setCurrMoveIdx(currMoveIdx - 1)}
                                    >
                                        Prev move
                                    </button>
                                    <button
                                        className={`btn btn-dark w-25 ms-2 ${currMoveIdx === moves.length ? 'disabled' : ''}`}
                                        onClick={() => incrMoveIdx(false)}
                                    >
                                        Next move
                                    </button>
                                </div>
                            </>
                        ) : (
                            <h5>No moves</h5>
                        )}
                    </div>
                </div>
            </div>
            <GameOverDialog
                show={showGameOverDialog}
                resultText={gameResultText}
                handleReset={() => resetBoard(gameRef, setFen, setMoves, setGroupedMoves, setCurrMoveIdx, setIsAgentTurn, userColor)}
                handleClose={handleCloseGameOverDialog}
            />
        </div>
    );
};

export default ChessBoardPage;
