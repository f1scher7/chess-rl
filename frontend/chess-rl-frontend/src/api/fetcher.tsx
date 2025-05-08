import {ChessRlFile, FileList, SavedGameContent} from "../types/types";


const API_URL = process.env.REACT_APP_API_URL;


export const fetchFileList = async (pathType: string): Promise<FileList> => {
  try {
      const response = await fetch(`${API_URL}/file-list?path_type=${pathType}`);
      return await response.json();
  } catch (e) {
      console.log(e);
      throw e;
  }
};

export const fetchSavedGameContent = async (file: ChessRlFile): Promise<SavedGameContent> => {
    try {
        const response = await fetch(`${API_URL}/saved-game?file=${encodeURIComponent(file.file_name)}`);
        return await response.json();
    } catch (e) {
        console.log(e);
        throw e;
    }
};


