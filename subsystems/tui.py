from .logging import Logger
import pygame

class TextUserInterface:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont('Arial', 24)
        self.text_color = (255, 255, 255)  # White color
        self.background_color = (0, 0, 0)    # Black color

        # 


        self.height = screen.get_height() // self.font.render("ABC", True, self.text_color).get_height()  # Calculate how many lines can fit on the screen
        self.width = screen.get_width() // (self.font.render("ABCDE", True, self.text_color).get_width()//5)   # Calculate how many characters can fit on a line

        self.lines = [""] * self.height  # Initialize empty lines

        self.lines[0] = "Welcome to the Text User Interface!"  # Initial message
        self.lines[1] = ">"  # Initial message

        self.current_line = 1  # Start at the second line for user input
        self.input_aktive = False
        self.input_buffer = ""

        self.logger = Logger()

        self.logger.log(0,"TUI init successful.")
        self.logger.log(0,f"TUI DATA:\nHeight:{self.height}\nWidth:{self.width}\nInput?:{self.input_aktive}")

        

    def draw_text(self, text, position):
        text_surface = self.font.render(text, True, self.text_color)
        text_rect = text_surface.get_rect(topleft=position)
        pygame.draw.rect(self.screen, self.background_color, text_rect.inflate(10, 10))  # Background for better visibility
        self.screen.blit(text_surface, text_rect)

    def print_line(self, text, line_number = None):
        if line_number is None:
            line_number = self.current_line
            self.current_line += 1  # Move to the next line for the next input
        self.lines[line_number] = self.lines[line_number] + text  # Truncate text if it's too long

        self.update()

    def update(self):
        # This method can be expanded to include more complex UI updates
        for idx, line in enumerate(self.lines):
            self.draw_text(line, (10, idx * self.font.get_height() + 10))
        
        pygame.display.flip()
