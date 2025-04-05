def get_offset_move(move):
    if move.promotion:
        return 225 + (move.promotion - 2)  # move.promotion - 2 = skip pawn

    from_square = move.from_square  # idx of square
    to_square = move.to_square  # idx of square

    from_square_row, from_square_col = divmod(from_square, 8)
    to_square_row, to_square_col = divmod(to_square, 8)

    delta_row = to_square_row - from_square_row  # the min-max of delta_row is [-7, 7]
    delta_col = to_square_col - from_square_col  # the min-max of delta_col is [-7, 7]

    delta_row += 7  # avoid negative nums -> [0, 14]
    delta_col += 7  # avoid negative nums -> [0, 14]

    return delta_row * 15 + delta_col


def get_move_idx(move):
    from_square = move.from_square

    move_offset = get_offset_move(move=move)

    return from_square * 73 + move_offset  # we have 73 because each square can have 4762 / 64 = 74.4 (73 idx)