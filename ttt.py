"""
Basic 3D Tic Tac Toe with Minimax and Alpha-Beta pruning, using a simple
heuristic to check for possible winning moves or blocking moves if no better
alternative exists.
"""


from colorama import Back, Style, Fore


class Board(object):
    """3D TTT logic and underlying game state object.

    Attributes:
        board (List[List[List[int]]]): 3D array of positions.
        allowed_moves (List[int]): List of currently unoccupied positions.
        difficulty (int): Ply; number of moves to look ahead.
        depth_count (int): Used in conjunction with ply to control depth.
        human_turn (bool): Control whose turn it is.
        human (str): The Human's character.
        ai (str): The AI's character.
        players (tuple): Tuple of the Human and AI's characters.

    Args:
        human_first (Optional[bool]): Whether or no the computer goes second.
        human (Optional[str]): Human's character.
        ai (Optional[str]): AI's character.
        ply (Optional[int]): Number of moves to look ahead.
    """

    winning_combos = (
        [0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11], [12, 13, 14],
        [15, 16, 17], [18, 19, 20], [21, 22, 23], [24, 25, 26],

        [0, 3, 6], [1, 4, 7], [2, 5, 8], [9, 12, 15], [10, 13, 16],
        [11, 14, 17], [18, 21, 24], [19, 22, 25], [20, 23, 26],

        [0, 4, 8], [2, 4, 6], [9, 13, 17], [11, 13, 15], [18, 22, 26],
        [20, 22, 24],

        [0, 9, 18], [1, 10, 19], [2, 11, 20], [3, 12, 21], [4, 13, 22],
        [5, 14, 23], [6, 15, 24], [7, 16, 25], [8, 17, 26],

        [0, 12, 24], [1, 13, 25], [2, 14, 26], [6, 12, 18], [7, 13, 19],
        [8, 14, 20], [0, 10, 20], [3, 13, 23], [6, 16, 26], [2, 10, 18],
        [5, 13, 21], [8, 16, 24], [0, 13, 26], [2, 13, 24], [6, 13, 20],
        [8, 13, 18]
    )

    PLAYER_1 = 'X'
    PLAYER_2 = 'O'

    def __init__(self):
        self.board = Board.create_board()
        self.allowed_moves = list(range(pow(3, 3)))
        self.players = (self.PLAYER_1, self.PLAYER_2)

    def find(self, arr, key):
        """Find a given key in a 3D array.

        Args:
            arr (List[List[List[int]]]]): 3D array to search.
            key (int): Key to find.

        Returns:
            Tuple of the Board, Row, and Column of the key.
        """
        cnt = 0
        for i in range(3):
            for x in range(3):
                for y in range(3):
                    if cnt == key:
                        return (i, x, y)
                    cnt += 1

    def find_combo(self, combo):
        """Given a combination find the coordinates of each part.

        Args:
            combo (List[int]): Winning combination to search for.

        Returns:
            List of the coordinates of the starting, middle, and ending.
        """
        s, m, e = combo
        s = self.find(self.board, s)
        m = self.find(self.board, m)
        e = self.find(self.board, e)
        return s, m, e

    @staticmethod
    def create_board():
        """Create the board with appropriate positions and the like

        Returns:
            3D array with ints for each position.
        """
        cnt = 0
        board = []
        for i in range(3):
            bt = []
            for x in range(3):
                rt = []
                for y in range(3):
                    rt.append(cnt)
                    cnt += 1
                bt.append(rt)
            board.append(bt)
        return board

    def get_moves(self, player):
        """Get the previously made moves for the player.

        Args:
            player (str): Player to retrieve moves of.

        Returns:
            List of the available moves of a player.
        """
        moves = []
        cnt = 0
        for i in range(3):
            for x in range(3):
                for y in range(3):
                    if self.board[i][x][y] == player:
                        moves += [cnt]
                    cnt += 1
        return moves

    def available_combos(self, player):
        """Get the list of available moves and previously made moves.

        Args:
            player (str): Player to find combinations of.

        Returns:
            List of available moves and winning combinations.
        """
        return list(self.allowed_moves) + self.get_moves(player)

    @property
    def complete(self):
        """bool: Whether or not the game is finished or tied."""
        for player in self.players:
            for combo in self.winning_combos:
                combo_avail = True
                for pos in combo:
                    if pos not in self.available_combos(player):
                        combo_avail = False
                if combo_avail:
                    return self.winner is not None
        return True

    @property
    def winning_combo(self):
        """List[int]: List of the winning positions if the game is over."""
        if self.winner:
            positions = self.get_moves(self.winner)
            for combo in self.winning_combos:
                winner = combo
                for pos in combo:
                    if pos not in positions:
                        winner = None
                if winner:
                    return winner
        return None

    @property
    def winner(self):
        """str: The winning player if the game is over."""
        for player in self.players:
            positions = self.get_moves(player)
            for combo in self.winning_combos:
                won = True
                for pos in combo:
                    if pos not in positions:
                        won = False
                if won:
                    return player
        return None

    def find_value(self, key):
        """Retrieve the value of the given position.

        Args:
            key (int): Position to find.

        Returns:
            The value at the given location on the board.
        """
        b, r, c = self.find(self.board, key)
        return self.board[b][r][c]

    def check_available(self, player, enemy):
        """int: Check the number of available wins on the current board
        state."""
        wins = 0
        for combo in self.winning_combos:
            if all([self.find_value(x) == player or self.find_value(x) != enemy for x in combo]):
                wins += 1
        return wins

    def undo_move(self, position):
        """Reverses a move."""
        self.allowed_moves += [position]
        self.allowed_moves.sort()
        i, x, y = self.find(self.board, position)
        self.board[i][x][y] = position

    def move(self, position, player):
        """Initiates a move on the given position.

        Args:
            position (int): Position on board to replace.
            player (str): Player to set piece to.
        """
        self.allowed_moves.remove(position)
        self.allowed_moves.sort()
        i, x, y = self.find(self.board, position)
        self.board[i][x][y] = player

    def display(self):
        """Displays the game's current state in text form.

        Winning combinations are shown in blue, numbers are given to aid
        the player in choosing a move. Red is used to indicate a player has
        made a move on that location.
        """
        cnt = 0
        for i, bd in enumerate(self.board):
            print('{}{}Board #{}{}'.format(Back.WHITE, Fore.BLACK, i + 1, Style.RESET_ALL))
            for line in bd:
                larr = []
                for cell in line:
                    bg = Back.RED
                    if self.winner and cnt in self.winning_combo:
                        bg = Back.BLUE
                    if cell in self.players:
                        s = '{}{:>2}{}'.format(bg, cell * 2, Style.RESET_ALL)
                    else:
                        s = '{:>2}'.format(cell)
                    larr += [s]
                    cnt += 1
                print(' '.join(larr))

class AIPlayer(object):
    def __init__(self, board, piece, ply=3):
        self.board = board
        self.piece = piece
        self.difficulty = ply
        self.depth_count = 0

    def do_turn(self):
        best_score = -1000
        best_move = None
        h = None
        win = False

        for move in self.board.allowed_moves:
            self.board.move(move, self.piece)
            if self.board.complete:
                win = True
                break
            else:
                h = self.think_ahead(self.enemy, -1000, 1000)
                self.depth_count = 0
                if h >= best_score:
                    best_score = h
                    best_move = move
                    self.board.undo_move(move)
                else:
                    self.board.undo_move(move)
                
                # see if it blocks the other player
                self.board.move(move, self.enemy)
                if self.board.complete and self.board.winner == self.enemy:
                    if 1001 >= best_score:
                        best_score = 1001
                        best_move = move
                self.board.undo_move(move)

        if not win:
            self.board.move(best_move, self.piece)

    def think_ahead(self, player, a, b):
        """Recursive Minimax & Alpha-Beta method to find the advisable moves.

        Args:
            a (int): Alpha value.
            b (int): Beta value.

        Returns:
            Alpha or Beta value depending on values of nodes.
        """
        if self.depth_count >= self.difficulty:
            return self.simple_heuristic
        else:
            self.depth_count += 1
            if player == self.piece:
                h = -1000
                for move in self.board.allowed_moves:
                    self.board.move(move, player)
                    if self.board.complete:
                        self.board.undo_move(move)
                        return 1000
                    else:
                        h = self.think_ahead(self.enemy, a, b)
                        if h > a:
                            a = h
                            self.board.undo_move(move)
                        else:
                            self.board.undo_move(move)
                    if a >= b:
                        break
                return a
            else:
                h = 1000
                for move in self.board.allowed_moves:
                    self.board.move(move, player)
                    if self.board.complete:
                        self.board.undo_move(move)
                        return -1000
                    else:
                        h = self.think_ahead(self.piece, a, b)
                        if h < b:
                            b = h
                            self.board.undo_move(move)
                        else:
                            self.board.undo_move(move)
                    if a >= b:
                        break
                return b


    @property
    def simple_heuristic(self):
        """int: Number of spaces available to win for the AI with the number
        of spaces available for the Human to win subtracted. Higher numbers
        are more favorable for the AI."""
        return self.board.check_available(self.piece, self.enemy) - self.board.check_available(self.enemy, self.piece)

    @property
    def enemy(self):
        if self.piece == self.board.PLAYER_1:
            return self.board.PLAYER_2
        else:
            return self.board.PLAYER_1

class HumanPlayer(object):
    def __init__(self, board, piece):
        self.board = board
        self.piece = piece

    def do_turn(self):
        while True:
            position = input('Which position? ')
            while not position.isdigit():
                position = input('Integer required; which position? ')
            position = int(position)
            if position not in self.board.allowed_moves:
                # Try again
                continue

            self.board.move(position, self.piece)
            break

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        '--p1', dest='p1', help='Player 1', type=str, default="h"
    )
    parser.add_argument(
        '--p1-ply', dest='p1_ply', help='Player 1 difficulty', type=int, default=3
    )
    parser.add_argument(
        '--p2', dest='p2', help='Player 2', type=str, default="ai"
    )
    parser.add_argument(
        '--p2-ply', dest='p2_ply', help='Player 2 difficulty', type=int, default=3
    )
    args = parser.parse_args()

    board = Board()

    if args.p1 == "h":
        player1 = HumanPlayer(board, board.PLAYER_1)
    else:
        player1 = AIPlayer(board, board.PLAYER_1, ply=args.p1_ply)

    if args.p2 == "h":
        player2 = HumanPlayer(board, board.PLAYER_2)
    else:
        player2 = AIPlayer(board, board.PLAYER_2, ply=args.p2_ply)

    player1_turn = True
    try:
        while not board.complete:
            board.display()
            if player1_turn:
                player1.do_turn()
            else:
                player2.do_turn()
            # Switch turn
            player1_turn = not player1_turn

        print('{}{} won!'.format(Style.BRIGHT, board.winner))
        board.display()
    except KeyboardInterrupt:
        print('\nWhat? Giving up already?')


