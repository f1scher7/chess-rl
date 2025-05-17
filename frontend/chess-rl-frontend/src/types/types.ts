export type ChessRlFile = {
    file_name: string;
}

export type FileList = {
    file_names: string[];
};

export type SavedGameContent = {
    white_elo: number;
    black_elo: number;
    result: string;
    moves: string[];
}
