import pygame
import os
import logic
import machine

# Centre window on screen
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Constants (size and colour)
BLOCK = 150
GAP = 10
BORDER = 50
WIN_SIZE = 3 * BLOCK + 2 * GAP + 2 * BORDER

BLOCK_COLOUR = (20, 189, 172)
BACKGROUND_COLOUR = (13, 161, 146)


class Button:
    def __init__(self, x, y, width, height, human_colour, computer_colour, computer=False, onclick=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.human_color = human_colour
        self.computer_colour = computer_colour
        self.human = logic.Player.HUMAN

        if onclick:
            self.onclick = onclick
            self.font = pygame.font.Font('sourcesanspro.ttf', 100)
            self.text = self.font.render('Play', 1, (100, 100, 100))
        else:
            self.onclick = self.switch
            self.font = pygame.font.Font('sourcesanspro.ttf', 40)
            self.text = self.font.render('Human', 1, (200, 200, 200))

        if computer:
            self.switch()

        self.text_rect = self.text.get_rect()
        self.text_rect.center = (self.x + self.width // 2, self.y + self.height // 2 + self.human.get_offset())

    def draw(self):
        if self.human == logic.Player.HUMAN:
            pygame.draw.rect(tictactoe.win, self.human_color, (self.x, self.y, self.width, self.height))
        else:
            pygame.draw.rect(tictactoe.win, self.computer_colour, (self.x, self.y, self.width, self.height))
        tictactoe.win.blit(self.text, self.text_rect)

    def switch(self):
        self.human = self.human.switch()
        if self.human == logic.Player.HUMAN:
            self.font = pygame.font.Font('sourcesanspro.ttf', 40)
            self.text = self.font.render('Human', 1, (200, 200, 200))
        else:
            self.font = pygame.font.Font('sourcesanspro.ttf', 30)
            self.text = self.font.render('Computer', 1, (200, 200, 200))

        self.text_rect = self.text.get_rect()
        self.text_rect.center = (self.x + self.width // 2, self.y + self.height // 2 + self.human.get_offset())

        return False

    def click(self, location):
        x, y = location
        if self.x < x < self.x + self.width and self.y < y < self.y + self.height:
            if self.onclick():
                return True

        return False


class Block:
    """Class representing each block
    :param rect: A tuple representing the block's location and size (x, y, width, height)
    :type rect: tuple
    """

    def __init__(self, rect):
        self.rect = rect
        self.state = logic.State.EMPTY  # Block is initialised empty

    def draw(self):
        """Draws the block to the Pygame window
        """
        pygame.draw.rect(tictactoe.win, BLOCK_COLOUR, self.rect)
        if self.state != logic.State.EMPTY:
            text = tictactoe.symbol_font.render(self.state.get_symbol(), 1, self.state.get_colour())
            text_rect = text.get_rect()
            text_rect.center = (self.rect[0] + self.rect[2] // 2,
                                self.rect[1] + self.rect[3] // 2 + self.state.get_offset())
            tictactoe.win.blit(text, text_rect)

    def clicked(self, location):
        """Check if a mouse click was inside a rectangle

        :param location: Position of mouse click
        :type location: tuple
        :return: Returns True if inside block and False if not
        :rtype: bool
        """
        x, y = location
        if self.rect[0] < x < self.rect[0] + self.rect[2] and self.rect[1] < y < self.rect[1] + self.rect[3]:
            return True
        return False

    def set_state(self, state):
        """Setter for the state of each block

        :param state: State to set
        :type state: logic.State
        """
        self.state = state


class GameHandler:
    """Represents all game objects
    """
    blocks = []
    buttons = []
    player1 = logic.Player.COMPUTER
    player2 = logic.Player.COMPUTER
    automated = False
    winner = None

    def __init__(self):
        pygame.init()
        self.win = pygame.display.set_mode((WIN_SIZE, WIN_SIZE))
        pygame.display.set_caption('Tic Tac Toe')

        self.symbol_font = pygame.font.Font('sourcesanspro.ttf', 200)
        self.medium_symbol_font = pygame.font.Font('sourcesanspro.ttf', 400)
        self.large_symbol_font = pygame.font.Font('sourcesanspro.ttf', 600)
        self.text_font = pygame.font.Font('sourcesanspro.ttf', 50)

        self.reset()

    def click(self, player, location=None):
        """Changes the block that was clicked on each mouse click

        :param location: Position of the mouse click
        :type location: tuple
        :param player: Player to move
        :type player: logic.Human or machine.Machine
        """
        if type(player) == logic.Human:
            for block in self.blocks:
                if block.clicked(location):
                    player.think(block)
        elif type(player) == machine.Machine:
            player.think(self.blocks)

        self.winner = logic.check_end(self.array())
        if self.winner != logic.Win.NOT_END:
            if self.winner == logic.Win.CROSS_WIN:
                self.player1.reward()
                self.player2.punish()
            elif self.winner == logic.Win.NAUGHT_WIN:
                self.player1.punish()
                self.player2.reward()
            else:
                self.player1.draw()
                self.player2.draw()

            return True

    def array(self):
        """Converts the blocks into an 2 dimensional state array

        :return: 3 x 3 list of State objects
        :rtype: list of logic.State
        """
        blocks = [self.blocks[:3], self.blocks[3:6], self.blocks[6:]]
        return [[(lambda x: x.state)(block) for block in row] for row in blocks]

    def end(self):
        """End screen loop and reset
        """
        self.win.fill(BACKGROUND_COLOUR)

        text = self.text_font.render(self.winner.value, 1, self.winner.get_colour())
        text_rect = text.get_rect()
        text_rect.center = (WIN_SIZE // 2, WIN_SIZE // 2 + 150)

        if self.winner != logic.Win.DRAW:
            symbol = self.large_symbol_font.render(self.winner.get_symbol(), 1, self.winner.get_colour())
            symbol_rect = symbol.get_rect()
            symbol_rect.center = (WIN_SIZE // 2, WIN_SIZE // 2 + self.winner.get_offset())
            self.win.blit(symbol, symbol_rect)

        else:
            naught_win = logic.Win.NAUGHT_WIN
            cross_win = logic.Win.CROSS_WIN

            naught_offset = naught_win.get_offset() + 20
            cross_offset = cross_win.get_offset()

            naught = self.medium_symbol_font.render(naught_win.get_symbol(), 1, naught_win.get_colour())
            cross = self.medium_symbol_font.render(cross_win.get_symbol(), 1, cross_win.get_colour())

            naught_rect = naught.get_rect()
            cross_rect = cross.get_rect()

            naught_rect.center = (WIN_SIZE // 2 + 100, WIN_SIZE // 2 + naught_offset)
            cross_rect.center = (WIN_SIZE // 2 - 100, WIN_SIZE // 2 + cross_offset)

            self.win.blit(naught, naught_rect)
            self.win.blit(cross, cross_rect)

        self.win.blit(text, text_rect)

        run = True
        while run:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    machine.save_pickle()
                    run = False
                    pygame.quit()
                    quit()

                elif e.type == pygame.KEYDOWN:
                    run = False

            pygame.display.update()

    def reset(self):
        """Resets the GameHandler to play again
        """
        self.win.fill(BLOCK_COLOUR)
        pygame.draw.rect(self.win, BACKGROUND_COLOUR, (BORDER, BORDER, WIN_SIZE - 2 * BORDER, WIN_SIZE - 2 * BORDER))

        # Instantiate all blocks in an array
        self.blocks = []
        for x in range(3):
            for y in range(3):
                self.blocks.append(Block((BLOCK * x + GAP * x + BORDER, BLOCK * y + GAP * y + BORDER, BLOCK, BLOCK)))

        logic.TURN = logic.Turn.CROSS
        self.player1 = logic.Player.COMPUTER
        self.player2 = logic.Player.COMPUTER
        self.winner = None

        if not self.automated:
            self.buttons = []

    def set_players(self):
        self.player1 = self.buttons[0].human.value
        self.player2 = self.buttons[1].human.value

        if isinstance(self.player1, machine.Machine) and isinstance(self.player2, machine.Machine):
            self.automated = True

        return True

    def draw(self):
        """Draws all blocks
        """
        self.win.fill(BACKGROUND_COLOUR)

        for block in self.blocks:
            block.draw()

        pygame.display.update()

    def gameloop(self):
        """Main game loop
        """
        clock = pygame.time.Clock()

        run = True
        while run:
            clock.tick(10)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    machine.save_pickle()
                    run = False
                    pygame.quit()
                    quit()

                if e.type == pygame.MOUSEBUTTONDOWN:
                    if logic.TURN.name == 'CROSS':
                        if type(self.player1) == logic.Human:
                            if self.click(self.player1, pygame.mouse.get_pos()):
                                self.winner = logic.Win.CROSS_WIN
                                run = False
                    else:
                        if type(self.player2) == logic.Human:
                            if self.click(self.player2, pygame.mouse.get_pos()):
                                self.winner = logic.Win.NAUGHT_WIN
                                run = False

                if e.type == pygame.KEYDOWN:
                    if logic.TURN.name == 'CROSS':
                        if type(self.player1) == machine.Machine:
                            if self.click(self.player1):
                                self.winner = logic.Win.CROSS_WIN
                                run = False
                    else:
                        if type(self.player2) == machine.Machine:
                            if self.click(self.player2):
                                self.winner = logic.Win.NAUGHT_WIN
                                run = False

            if self.automated:
                if logic.TURN.name == 'CROSS':
                    if type(self.player1) == machine.Machine:
                        if self.click(self.player1):
                            self.winner = logic.Win.CROSS_WIN
                            run = False
                else:
                    if type(self.player2) == machine.Machine:
                        if self.click(self.player2):
                            self.winner = logic.Win.NAUGHT_WIN
                            run = False

            self.draw()

    def menu(self):
        if self.automated:
            self.set_players()
            return

        self.buttons.append(Button(WIN_SIZE // 2 - 210, WIN_SIZE // 2 - 180, 150, 80, (0, 150, 50), (200, 50, 0), True))
        self.buttons.append(Button(WIN_SIZE // 2 + 60, WIN_SIZE // 2 - 180, 150, 80, (0, 150, 50), (200, 50, 0), True))
        self.buttons.append(Button(WIN_SIZE // 2 - 210, WIN_SIZE // 2 - 70, 420, 250, (0, 150, 50), (0, 150, 50),
                                   False, self.set_players))

        run = True
        while run:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    machine.save_pickle()
                    run = False
                    pygame.quit()
                    quit()

                if e.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttons:
                        if button.click(pygame.mouse.get_pos()):
                            run = False

                if e.type == pygame.KEYDOWN:
                    run = False

            for button in self.buttons:
                button.draw()

            pygame.display.update()

    def run(self, count):
        self.menu()

        self.gameloop()

        if self.automated:
            self.reset()
            self.set_players()
            self.gameloop()
            self.reset()

        else:
            self.end()
            self.reset()

        if count % 100 == 0:
            machine.save_pickle()

    def main(self):
        for i in range(10000):
            self.run(i)


if __name__ == '__main__':
    machine.load_pickle()
    tictactoe = GameHandler()
    tictactoe.main()
