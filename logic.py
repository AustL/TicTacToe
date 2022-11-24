from enum import IntEnum
from enum import Enum
import machine

# Constants
NAUGHT_COLOUR = (242, 235, 211)
CROSS_COLOUR = (84, 84, 84)
DRAW_COLOUR = (10, 10, 100)


class Human:
    def __init__(self):
        self.name = 'Bob'
        self.score = 0

    def think(self, block):
        """Changes the state of a block

        :param block: The block to change
        :type block: Block
        :return: True if valid move and False if invalid move
        :rtype: bool
        """
        if block.state == State.EMPTY:
            block.set_state(TURN.value)
            TURN.switch()
            return True

        print(f'{self.name}, that is an invalid location!')
        return False

    def reward(self):
        self.score += 3

    def punish(self):
        self.score -= 1

    def draw(self):
        self.score += 1


class Player(Enum):
    HUMAN = Human()
    COMPUTER = machine.Machine()

    def switch(self):
        if self == Player.HUMAN:
            return Player.COMPUTER
        return Player.HUMAN

    def get_offset(self):
        if self == Player.HUMAN:
            return -2
        return 0


class State(IntEnum):
    """Enum representing the state of each block
    """
    NAUGHT = -1
    CROSS = 1
    EMPTY = 0

    def __repr__(self):
        return self.get_symbol()

    def get_colour(self):
        """Getter for the colour of each state

        :return: Colour of naughts/crosses
        :rtype: tuple
        """
        if self == State.NAUGHT:
            return NAUGHT_COLOUR
        elif self == State.CROSS:
            return CROSS_COLOUR

        return DRAW_COLOUR

    def get_symbol(self):
        """Getter for the symbol of each state

        :return: Symbol representing each state
        :rtype: str
        """
        if self == State.NAUGHT:
            return 'o'
        elif self == State.CROSS:
            return '×'

        return ' '

    def get_offset(self):
        """Getter for the y-offset needed for the symbol to be centred

        :return: Pixels to offset by
        :rtype: int
        """
        if self == State.NAUGHT:
            return -25
        elif self == State.CROSS:
            return -5


class Win(Enum):
    """Enum representing the states of each game condition (win, draw and not ended)
    """
    NAUGHT_WIN = 'Naughts win!'
    CROSS_WIN = 'Crosses win!'
    NOT_END = False
    DRAW = 'Draw!'

    def __eq__(self, other):
        return self.name == other.name

    def get_colour(self):
        """Getter for the colour of each state

        :return: Colour of each state
        :rtype: tuple
        """
        if self == Win.NAUGHT_WIN:
            return NAUGHT_COLOUR
        elif self == Win.CROSS_WIN:
            return CROSS_COLOUR

        return DRAW_COLOUR

    def get_symbol(self):
        """Getter for the symbol of each state

        :return: Symbol representing each state
        :rtype: str
        """
        if self == Win.NAUGHT_WIN:
            return 'o'
        elif self == Win.CROSS_WIN:
            return '×'

        return ' '

    def get_offset(self):
        """Getter for the y-offset needed for the symbol to be centred

        :return: Pixels to offset by
        :rtype: int
        """
        if self == Win.NAUGHT_WIN:
            return -140
        elif self == Win.CROSS_WIN:
            return -80

        return 0


class Turn(Enum):
    """Enum representing whose turn it is
    """
    NAUGHT = State.NAUGHT
    CROSS = State.CROSS

    def switch(self):
        """Switches whose turn it is
        """
        global TURN

        if self == Turn.NAUGHT:
            TURN = Turn.CROSS
        elif self == Turn.CROSS:
            TURN = Turn.NAUGHT

    def __eq__(self, other):
        return self.name == other.name


def check_end(array):
    """Checks the game state

    :param array:
    :type array: list
    :return: Returns game states: naughts win, crosses win, draw and not ended
    :rtype: Win
    """
    columns = [[], [], []]

    for row in array:
        total = sum(row)
        if total == 3:
            return Win.CROSS_WIN
        elif total == -3:
            return Win.NAUGHT_WIN
        for i, x in enumerate(row):
            try:
                columns[i].append(x)
            except IndexError as e:
                print('Error')

    for row in columns:
        total = sum(row)
        if total == 3:
            return Win.CROSS_WIN
        elif total == -3:
            return Win.NAUGHT_WIN

    if array[0][0] + array[1][1] + array[2][2] == 3 or array[0][2] + array[1][1] + array[2][0] == 3:
        return Win.CROSS_WIN
    elif array[0][0] + array[1][1] + array[2][2] == -3 or array[0][2] + array[1][1] + array[2][0] == -3:
        return Win.NAUGHT_WIN

    for row in array:
        if State.EMPTY in row:
            return Win.NOT_END

    return Win.DRAW


# Holds whose turn it is
TURN = Turn.CROSS
