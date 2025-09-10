import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Modal, Button } from 'react-bootstrap';
import { fetchSavedGameContent } from '../../../api/fetcher';
import { ChessRlFile } from '../../../models/models';
import '../../../global.css';
import './FileListDialog.css';
import { PieceColor } from '../../../enums';


type FileListDialogProps = {
    show: boolean;
    playGameVsAgent: boolean;
    fileList: string[];
    handleClose: () => void;
};

const FileListDialog: React.FC<FileListDialogProps> = ({ show, playGameVsAgent, fileList, handleClose }: FileListDialogProps) => {
    const navigate = useNavigate();

    const [selectedFile, setSelectedFile] = useState<string>('');
    const [currentPage, setCurrentPage] = useState<number>(1);
    const [selectedColor, setSelectedColor] = useState<string>(PieceColor.White);

    const maxVisiblePages: number = 8;
    const filesPerPage: number = 10;
    const totalPages: number = Math.ceil(fileList.length / filesPerPage);

    const idxOfLastFile: number = currentPage * filesPerPage;
    const idxOfFirstFile: number = idxOfLastFile - filesPerPage;
    const currentFiles: string[] = fileList.slice(idxOfFirstFile, idxOfLastFile);

    const startPage: number = Math.max(1, currentPage - maxVisiblePages);
    const endPage: number = Math.min(totalPages, startPage + maxVisiblePages);

    const handleSelect = async () => {
        if (selectedFile) {
            handleClose();

            if (playGameVsAgent) {
                navigate('/user-play', { state: { userColor: selectedColor, modelFileName: selectedFile } });
            } else {
                try {
                    const file: ChessRlFile = { file_name: selectedFile };
                    const data = await fetchSavedGameContent(file);

                    navigate('/agents-play', { state: { savedGameContent: data } });
                } catch (e) {
                    console.error(e);
                    throw e;
                }
            }
        }
    };

    useEffect(() => {
        if (!show) {
            const timeout = setTimeout(() => {
                setSelectedFile('');
                setCurrentPage(1);
            }, 2000);

            return () => clearTimeout(timeout);
        }
    }, [show]);

    return (
        <Modal
            show={show}
            onHide={handleClose}
            dialogClassName="no-center"
        >
            <Modal.Header closeButton>
                <Modal.Title>
                    {playGameVsAgent ? 'Choose the agent' : 'Choose the agent\'s game'}
                </Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {fileList.length === 0 ? (
                    <p>No files available!</p>
                ) : (
                    <>
                        <ul className="list-group mt-2">
                            {currentFiles.map((fileName, idx) => (
                                <li
                                    key={idx}
                                    className={`list-group-item list-group-item-action list-group-item-light ${fileName === selectedFile ? 'active' : ''}`}
                                    onClick={() => setSelectedFile(fileName)}
                                    style={{ cursor: 'pointer' }}
                                >
                                    {fileName}
                                </li>
                            ))}
                        </ul>
                        <nav className="mt-4">
                            <ul className="pagination justify-content-center">
                                <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
                                    <a className="page-link"
                                        onClick={() => currentPage > 1 && setCurrentPage(currentPage - 1)}
                                        aria-label="Previous">
                                        <span aria-hidden="true">&laquo;</span>
                                        <span className="sr-only">Previous</span>
                                    </a>
                                </li>
                                {Array.from({ length: endPage - startPage + 1 }, (_, i) => {
                                    const page = startPage + i;
                                    return (
                                        <li key={page}
                                            className={`page-item page-idxs ${currentPage === page ? 'active' : ''}`}>
                                            <a className="page-link" onClick={() => setCurrentPage(page)}>
                                                {page}
                                            </a>
                                        </li>
                                    );
                                })}
                                <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
                                    <a className="page-link"
                                        onClick={() => currentPage < totalPages && setCurrentPage(currentPage + 1)}
                                        aria-label="Next">
                                        <span aria-hidden="true">&raquo;</span>
                                        <span className="sr-only">Next</span>
                                    </a>
                                </li>
                            </ul>
                        </nav>

                        {playGameVsAgent ? (
                            <div className="d-flex justify-content-center gap-3">
                                <Button
                                    variant={selectedColor === PieceColor.White ? 'outline-dark' : ''}
                                    onClick={() => setSelectedColor(PieceColor.White)}
                                    className="no-hover"
                                >
                                    White ♘
                                </Button>
                                <Button
                                    variant={selectedColor === PieceColor.Black ? 'outline-dark' : ''}
                                    onClick={() => setSelectedColor(PieceColor.Black)}
                                    className="no-hover"
                                >
                                    Black ♞
                                </Button>
                            </div>
                        ) : null}
                    </>
                )}
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={handleClose}>
                    Close
                </Button>
                <Button variant="dark" onClick={handleSelect}>
                    Select
                </Button>
            </Modal.Footer>
        </Modal>
    );
};

export default FileListDialog;
