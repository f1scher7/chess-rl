import React, { useState } from 'react';
import './Home.css';
import FileListDialog from '../../components/dialogs/fileListDialog/FileListDialog';
import Footer from '../../components/Footer';
import { fetchFileList } from '../../api/fetcher';


const Home: React.FC = () => {
    const [showFileListDialog, setShowFileListDialog] = useState<boolean>(false);
    const [playGameVsAgent, setPlayGameVsAgent] = useState<boolean>(false);
    const [fileList, setFileList] = useState<string[]>([]);

    const handleOpenFileListDialog = async (playGame: boolean) => {
        setPlayGameVsAgent(playGame);
        setShowFileListDialog(true);

        const selectedPathType = playGame ? 'models' : 'games';

        try {
            const data = await fetchFileList(selectedPathType);
            setFileList(data.file_names);
        } catch (e) {
            console.log(e);
        }
    };

    const handleCloseFileListDialog = () => {
        setShowFileListDialog(false);
    };

    return (
        <div className="container-fluid home-bg w-100">
            <div className="row h-75">
                <div className="col">
                    <div className="d-flex flex-column bg-light rounded-3 shadow bg-opacity-75 w-25 h-100 ml-30p mt-5p">
                        <div className="pt-15p text-center">
                            <h1>ChessRl</h1>
                            <img className="mx-auto d-block" src="/assets/chess-rl-logos/chess-rl-logo128.png" alt="ChessRl" />
                        </div>
                        <div className="d-flex flex-column align-items-center pt-20p gap-3">
                            <button className="btn btn-dark w-50 py-2" onClick={() => handleOpenFileListDialog(false)}>See How AI Agents Play</button>
                            <button className="btn btn-dark w-50 py-2" onClick={() => handleOpenFileListDialog(true)}>Play a Game Against AI Agent</button>
                            <a className="w-50" href="https://github.com/f1scher7/chess-rl" target="_blank" rel="noreferrer">
                                <button className="btn btn-dark w-100 py-2">About</button>
                            </a>
                        </div>
                        <div className="mt-auto">
                            <Footer />
                        </div>
                    </div>
                </div>
            </div>

            <FileListDialog
                show={showFileListDialog}
                playGameVsAgent={playGameVsAgent}
                fileList={fileList}
                handleClose={handleCloseFileListDialog}
            />
        </div>
    );
};

export default Home;
