export function retrieveEpisodeNumFromModelFileName(filename: string | undefined, isView: boolean): string {
    if (filename && !isView) {
        const match: RegExpMatchArray | null = filename?.match(/episodes(\d+)/);
        if (match) {
            return match[1];
        }
    }

    return '-1';
}

export function generateGroupedMoves(moves: string[] | undefined): string[][] {
    if (moves) {
        const groupedMoves: string[][] = [];

        for (let i = 0; i < moves.length; i += 2) {
            groupedMoves.push(moves.slice(i, i + 2));
        }

        return groupedMoves;
    }

    return [];
}
