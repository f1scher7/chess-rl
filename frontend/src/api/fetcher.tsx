import { ChessRlFile, FileList, SavedGameContent } from '../models/models';


const API_URL = process.env.REACT_APP_API_URL;


export const fetchFileList = async (pathType: string): Promise<FileList> => {
    try {
        const response = await fetch(`${API_URL}/file-list?path_type=${pathType}`);
        return await response.json();
    } catch (e) {
        console.error(e);
        throw e;
    }
};

export const fetchSavedGameContent = async (file: ChessRlFile): Promise<SavedGameContent> => {
    try {
        const response = await fetch(`${API_URL}/saved-game?file=${encodeURIComponent(file.file_name)}`);
        return await response.json();
    } catch (e) {
        console.error(e);
        throw e;
    }
};

export const fetchAgentMove = async (modelFileName: string, fen: string) => {
    try {
        const response = await fetch(`${API_URL}/play-vs-agent?model_file_name=${modelFileName}&fen=${encodeURIComponent(fen)}`);
        return await response.json();
    } catch (e) {
        console.error(e);
        throw e;
    }
};


