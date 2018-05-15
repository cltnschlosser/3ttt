"""
Basic 3D Tic Tac Toe with Minimax and Alpha-Beta pruning, using a simple
heuristic to check for possible winning moves or blocking moves if no better
alternative exists.
"""


from colorama import Back, Style, Fore
import random
from time import time

DEFEND = 1001
LOSE = -1000
WIN = 1000
TIE = 0


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
        self.allowed_moves = list(range(9))
        self.moves = 0
        self.players = (self.PLAYER_1, self.PLAYER_2)

    @staticmethod
    def create_board():
        """Create the board with appropriate positions and the like

        Returns:
            3D array with ints for each position.
        """
        return list(range(27))

    def get_moves(self, player):
        """Get the previously made moves for the player.

        Args:
            player (str): Player to retrieve moves of.

        Returns:
            List of the available moves of a player.
        """
        moves = []
        for i in range(27):
            if self.board[i] == player:
                moves.append(i)
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
        return self.board[key]

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
        self.allowed_moves.append(position)
        if position < 18:
            self.allowed_moves.remove(position + 9)
        self.moves -= 1
        self.allowed_moves.sort()
        self.board[position] = position

    def move(self, position, player):
        """Initiates a move on the given position.

        Args:
            position (int): Position on board to replace.
            player (str): Player to set piece to.
        """
        self.allowed_moves.remove(position)
        if position < 18:
            self.allowed_moves.append(position + 9)
        self.moves += 1
        self.allowed_moves.sort()
        self.board[position] = player

    def display(self):
        """Displays the game's current state in text form.

        Winning combinations are shown in blue, numbers are given to aid
        the player in choosing a move. Red is used to indicate a player has
        made a move on that location.
        """
        cnt = 0
        for i in range(3):
            print('{}{}Board #{}{}'.format(Back.WHITE, Fore.BLACK, i + 1, Style.RESET_ALL))
            for row in range(3):
                larr = []
                for col in range(3):
                    cell_position = i*9 + row*3 + col
                    cell = self.board[cell_position]
                    bg = Back.RED
                    if self.winner and (cell_position in self.winning_combo):
                        bg = Back.BLUE
                    if cell in self.players:
                        s = '{}{:>2}{}'.format(bg, cell * 2, Style.RESET_ALL)
                    else:
                        s = '{:>2}'.format(cell)
                    larr.append(s)
                print(' '.join(larr))

class AIPlayer(object):
    def __init__(self, board, piece, ply=3):
        self.board = board
        self.piece = piece
        self.difficulty = ply
        self.depth_count = 0
        self.nodes_examined = 0
        self.total_nodes_examined = 0

    def do_turn(self):
        best_score = 2*LOSE
        best_depth = 0
        best_move = None

        # check if we can win
        for move in self.board.allowed_moves:
            self.board.move(move, self.piece)
            if self.board.complete:
                return
            self.board.undo_move(move)

        # check if we can block
        for move in self.board.allowed_moves:
            self.board.move(move, self.enemy)
            if self.board.complete and self.board.winner == self.enemy:
                self.board.undo_move(move)
                self.board.move(move, self.piece)
                return
            self.board.undo_move(move)

        # Find optimal move
        for move in self.board.allowed_moves:
            self.board.move(move, self.piece)
            h, depth = self.think_ahead(self.enemy, 2*LOSE, WIN, 0)
            self.total_nodes_examined += self.nodes_examined
            # print()
            # print(move)
            # print(depth)
            # print(self.nodes_examined)
            # print(self.total_nodes_examined)
            # print(h)
            self.depth_count = 0
            self.nodes_examined = 0
            if h > best_score or (h == best_score and best_score == LOSE and depth > best_depth):
                best_score = h
                best_move = move
                best_depth = depth
            self.board.undo_move(move)

            # Short circuit on a win
            if best_score == WIN:
                break

        self.board.move(best_move, self.piece)

    def think_ahead(self, player, a, b, h_depth):
        """Recursive Minimax & Alpha-Beta method to find the advisable moves.

        Args:
            a (int): Alpha value.
            b (int): Beta value.

        Returns:
            Alpha or Beta value depending on values of nodes.
        """
        self.nodes_examined += 1
        if self.depth_count >= self.difficulty:
            return (self.simple_heuristic, self.depth_count)
        else:
            self.depth_count += 1

            if player == self.piece:
                h = LOSE
                for move in self.board.allowed_moves:
                    self.board.move(move, player)
                    if self.board.complete:
                        if self.board.winner == player:
                            self.board.undo_move(move)
                            self.depth_count -= 1
                            return (WIN, self.depth_count + 1)
                        else:
                            self.board.undo_move(move)
                            self.depth_count -= 1
                            return (TIE, self.depth_count + 1)
                    else:
                        h, depth = self.think_ahead(self.enemy, a, b, h_depth)
                        if h > a:
                            a = h
                            h_depth = depth
                            self.board.undo_move(move)
                        else:
                            self.board.undo_move(move)
                    if a >= b:
                        break
                self.depth_count -= 1
                return (a, h_depth)
            else:
                h = WIN
                for move in self.board.allowed_moves:
                    self.board.move(move, player)
                    if self.board.complete:
                        if self.board.winner == player:
                            self.board.undo_move(move)
                            self.depth_count -= 1
                            return (LOSE, self.depth_count + 1)
                        else:
                            self.board.undo_move(move)
                            self.depth_count -= 1
                            return (TIE, self.depth_count + 1)
                    else:
                        h, depth = self.think_ahead(self.piece, a, b, h_depth)
                        if h < b:
                            b = h
                            h_depth = depth
                            self.board.undo_move(move)
                        else:
                            self.board.undo_move(move)
                    if a >= b:
                        break
                self.depth_count -= 1
                return (b, h_depth)

    @property
    def simple_heuristic(self):
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

class RandomPlayer(object):
    def __init__(self, board, piece):
        self.board = board
        self.piece = piece

    def do_turn(self):
        self.board.move(random.choice(self.board.allowed_moves), self.piece)

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
    elif args.p1 == "ai":
        player1 = AIPlayer(board, board.PLAYER_1, ply=args.p1_ply)
    else:
        player1 = RandomPlayer(board, board.PLAYER_1)

    if args.p2 == "h":
        player2 = HumanPlayer(board, board.PLAYER_2)
    elif args.p2 == "ai":
        player2 = AIPlayer(board, board.PLAYER_2, ply=args.p2_ply)
    else:
        player2 = RandomPlayer(board, board.PLAYER_2)

    player1_turn = True
    try:
        while not board.complete:
            board.display()
            start_time = time()
            if player1_turn:
                print("{}Player X{}".format(Style.BRIGHT, Style.RESET_ALL))
                player1.do_turn()
            else:
                print("{}Player O{}".format(Style.BRIGHT, Style.RESET_ALL))
                player2.do_turn()
            print("Time: " + str(time() - start_time))
            # Switch turn
            player1_turn = not player1_turn

        print('{}{} won!{}'.format(Style.BRIGHT, board.winner, Style.RESET_ALL))
        board.display()
        print('Moves: ' + str(board.moves))
    except KeyboardInterrupt:
        print('\nWhat? Giving up already?')


