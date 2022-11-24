import itertools
import pickle
import logic
import random

# TODO: combine game state dictionaries
# Game state dictionary
GAMESTATES = {}
SAVECOUNT = 0


def update_pickle():
    """Updates the pickle file with the game state dictionaries
    """
    global GAMESTATES

    for c in itertools.product((0, -1, 1), repeat=9):
        if c.count(0) == 0:
            continue

        diff = c.count(1) - c.count(-1)
        indices = [i for i, x in enumerate(c) if x == 0] * 2
        if diff == 0 or diff == 1:
            GAMESTATES[c] = indices

    with open('GAMESTATES.pickle', 'wb') as f:
        pickle.dump((GAMESTATES, SAVECOUNT), f, protocol=pickle.HIGHEST_PROTOCOL)

    print('UPDATED')


def load_pickle():
    """Loads the game state dictionary from the pickle file
    """
    global GAMESTATES, SAVECOUNT

    with open('GAMESTATES.pickle', 'rb') as f:
        GAMESTATES, SAVECOUNT = pickle.load(f)


def save_pickle():
    """Saves the game state dictionary into a pickle file
    """
    global SAVECOUNT

    SAVECOUNT += 1
    print(f'Saved: {SAVECOUNT}')

    with open('GAMESTATES.pickle', 'wb') as f:
        pickle.dump((GAMESTATES, SAVECOUNT), f, protocol=pickle.HIGHEST_PROTOCOL)


def prepare_data(arr):
    """Convert blocks to numbers

    :param arr: Array to convert
    :type arr: list of game.Block
    :return: Values of blocks in array
    :rtype: tuple of int
    """
    return tuple(map(lambda x: x.state.value, arr))


class Machine:
    def __init__(self):
        self.played = {}

    def think(self, blocks):
        """Change the state of the block using game state dictionary

        :param blocks: Blocks to change
        :type blocks: list of game.Block
        """
        state = prepare_data(blocks)
        choice = random.choice(GAMESTATES[state])

        blocks[choice].set_state(logic.TURN.value)
        logic.TURN.switch()

        self.played[state] = choice

    def reward(self):
        """Reward the machine for a win
        """
        for state in self.played:
            GAMESTATES[state] = GAMESTATES[state] + [self.played[state]] * 3

        self.played = {}

    def punish(self):
        """Punish the machine for a loss
        """
        for state in self.played:
            GAMESTATES[state].remove(self.played[state])
            if len(GAMESTATES[state]) == 0:
                GAMESTATES[state] = [i for i, x in enumerate(state) if x == 0]

        self.played = {}

    def draw(self):
        """Reward the machine slightly for a draw
        """
        for state in self.played:
            GAMESTATES[state] = GAMESTATES[state] + [self.played[state]]

        self.played = {}


if __name__ == '__main__':
    update_pickle()
    load_pickle()
