import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Modal, Button } from 'react-bootstrap';
import { fetchSavedGameContent } from "../../api/fetcher";
import { ChessRlFile } from "../../types/types";
import '../../global.css';
import './FileListDialog.css';


type FileListDialogProps = {
    show: boolean;
    playGameVsAgent: boolean;
    fileList: string[];
    handleClose: () => void;
};

const FileListDialog: React.FC<FileListDialogProps> = ({ show, playGameVsAgent, fileList, handleClose }) => {
    const navigate = useNavigate();

    const [selectedFile, setSelectedFile] = useState<string>("");
    const [currentPage, setCurrentPage] = useState<number>(1);

    const filesPerPage: number = 10;
    const idxOfLastFile: number = currentPage * filesPerPage;
    const idxOfFirstFile: number = idxOfLastFile - filesPerPage;
    const currentFiles: string[] = fileList.slice(idxOfFirstFile, idxOfLastFile);
    const totalPages: number = Math.ceil(fileList.length / filesPerPage);

    const handleSelect = async () => {
      if (selectedFile) {
          handleClose();

          if (playGameVsAgent) {
              const userColor = 'white';

              navigate("/user-play", { state: { userColor: userColor } });
          } else {
              try {
                  const file: ChessRlFile = { file_name: selectedFile };
                  const data = await fetchSavedGameContent(file);

                  navigate("/agents-play", { state: { savedGameContent: data } })
              } catch(e) {
                  console.log(e);
                  throw e;
              }
          }
      }
    };

    useEffect(() => {
        if (!show) {
            setSelectedFile("");
            setCurrentPage(1);
        }
    }, [show]);

    return (
        <Modal show={show} onHide={handleClose} dialogClassName="no-center">
            <Modal.Header closeButton>
                <Modal.Title>
                    {playGameVsAgent ? "Choose the agent" : "Choose the agent's game"}
                </Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {fileList.length === 0 ? (
                    <p>No files available!</p>
                ) : (
                    <>
                        <ul className="list-group mt-4">
                            {currentFiles.map((fileName, idx) => (
                                <li
                                    key={idx}
                                    className={`list-group-item list-group-item-action list-group-item-light ${fileName === selectedFile ? 'active' : ''}`}
                                    onClick={() => setSelectedFile(fileName)}
                                    style={{ cursor: "pointer" }}
                                >
                                    {fileName}
                                </li>
                            ))}
                        </ul>
                        <nav className="mt-4">
                            <ul className="pagination justify-content-center">
                                {Array.from({ length: totalPages }, (_, i) => (
                                    <li key={i} className={`page-item ${currentPage === i + 1 ? 'active' : ''}`}>
                                        <a className="page-link" onClick={() => setCurrentPage(i + 1)} style={{ cursor: 'pointer' }}>
                                            {i + 1}
                                        </a>
                                    </li>
                                ))}
                            </ul>
                        </nav>
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
