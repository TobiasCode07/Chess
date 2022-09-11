import pygame
from constants import *
from board import Board
from tkinter import *
from pygame import mixer
from _thread import *

mixer.init()

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.selected = None
        self.turn = "w"
        self.board = Board(self.screen)
        self.valid_moves = []
        self.select_frame = None
        self.reset()

    def reset(self):
        self.selected = None
        self.turn = "w"
        self.board = Board(self.screen)
        self.valid_moves = []
        mixer.music.load(GAME_START_PATH)
        mixer.music.play()

    def update(self):
        self.board.draw_board()
        self.draw_valid_moves(self.valid_moves)
        self.draw_select_frame()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select_frame = None
                self.select(row, col)

        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.select_frame = (piece.row, piece.col)
            self.valid_moves = self.board.get_valid_moves(piece, self.turn)
            return True

        self.valid_moves = []
        return False

    def draw_select_frame(self):
        if self.select_frame:
            pygame.draw.rect(self.screen, GREEN, pygame.Rect(self.select_frame[1] * SQUARE_SIZE + INDEX_PADDING, self.select_frame[0] * SQUARE_SIZE + INDEX_PADDING, SQUARE_SIZE, SQUARE_SIZE), 3)

    def _move(self, row, col):
        castle = False
        if self.selected and (row, col) in self.valid_moves:
            if self.board.get_piece(row, col):
                self.board.capture(row, col)
                self.board.move(self.selected, row, col)
                if self.board.is_checkmate("w" if self.turn == "b" else "b"):
                    start_new_thread(self.game_over, (self.turn, "checkmate"))
                    mixer.music.load(CHECKMATE_PATH)
                    mixer.music.play()

                elif self.board.is_stalemate("w" if self.turn == "b" else "b"):
                    start_new_thread(self.game_over, (self.turn, "stalemate"))
                    mixer.music.load(STALEMATE_PATH)
                    mixer.music.play()

                elif self.board.is_check("w" if self.turn == "b" else "b"):
                    mixer.music.load(CHECK_PATH)
                    mixer.music.play()

                else:
                    mixer.music.load(CAPTURE_PATH)
                    mixer.music.play()

            else:
                if (row, col) in self.board.check_for_castles(self.selected):
                    castle = True

                self.board.move(self.selected, row, col)

                if self.board.is_checkmate("w" if self.turn == "b" else "b"):
                    start_new_thread(self.game_over, (self.turn, "checkmate"))
                    mixer.music.load(CHECKMATE_PATH)
                    mixer.music.play()

                elif self.board.is_stalemate("w" if self.turn == "b" else "b"):
                    start_new_thread(self.game_over, (self.turn, "stalemate"))
                    mixer.music.load(STALEMATE_PATH)
                    mixer.music.play()

                elif self.board.is_check("w" if self.turn == "b" else "b"):
                    mixer.music.load(CHECK_PATH)
                    mixer.music.play()

                elif castle:
                    rook = self.board.get_piece(row, col + 1 if col > 4 else col - 2)
                    self.board.move(rook, rook.row, rook.col - 2 if rook.col == 7 else rook.col + 3)
                    mixer.music.load(CASTLE_PATH)
                    mixer.music.play()
                    castle = False

                else:
                    mixer.music.load(MOVE_PATH)
                    mixer.music.play()

            piece = self.board.get_piece(row, col)
            piece.moved = True
            if piece.piece_type == "pawn":
                if piece.row == 0 or piece.row == 7:
                    self.promotion(piece)

            self.selected = None
            self.select_frame = None
            self.change_turn()
        else:
            self.selected = None
            self.select_frame = None
            return False

        return True

    def change_turn(self):
        self.valid_moves = []
        if self.turn == "w":
            self.turn = "b"
        else:
            self.turn = "w"

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.screen, LIGHT_BROWN, (INDEX_PADDING + SQUARE_SIZE * col + SQUARE_SIZE // 2, INDEX_PADDING + SQUARE_SIZE * row + SQUARE_SIZE // 2), 20)

    def reset_win(self, win):
        self.reset()
        win.destroy()

    def game_over(self, winner, type):
        root = Tk()
        root.title("Game over")
        root.iconbitmap(ICON_PATH_ICO)
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width / 2) - (GAME_OVER_WIDTH / 2)
        y = (screen_height / 2) - (GAME_OVER_HEIGHT / 2)
        root.geometry(f"{GAME_OVER_WIDTH}x{GAME_OVER_HEIGHT}+{int(x)}+{int(y)}")

        color = "White" if winner == "w" else "Black"
        if type == "checkmate":
            text = f"{color} has won by checkmate"
        else:
            text = "Draw by stalemate"
        result = Label(root, text=text)
        result.pack(pady=10)

        restart_btn = Button(root, text="New game", command=lambda: self.reset_win(root))
        restart_btn.pack(ipadx=5, ipady=5)

        root.mainloop()

    def change_piece_type(self, piece, choice):
        global root, running
        running = False
        root.destroy()
        piece.piece_type = choice

    def promotion(self, piece):
        global root, running
        running = True
        while running:
            root = Tk()
            root.title("Pawn promotion")
            root.iconbitmap(ICON_PATH_ICO)
            root.resizable(False, False)
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            x = (screen_width/2) - (PROMOTION_WIDTH/2)
            y = (screen_height/2) - (PROMOTION_HEIGHT/2)
            root.geometry(f"{PROMOTION_WIDTH}x{PROMOTION_HEIGHT}+{int(x)}+{int(y)}")

            queen_img = PhotoImage(file=PIECE_PATH.replace("x", f"{piece.color}_queen"))
            rook_img = PhotoImage(file=PIECE_PATH.replace("x", f"{piece.color}_rook"))
            bishop_img = PhotoImage(file=PIECE_PATH.replace("x", f"{piece.color}_bishop"))
            knight_img = PhotoImage(file=PIECE_PATH.replace("x", f"{piece.color}_knight"))

            queen_btn = Button(root, image=queen_img, width=144, height=PROMOTION_HEIGHT, command=lambda: self.change_piece_type(piece, "queen"))
            rook_btn = Button(root, image=rook_img, width=144, height=PROMOTION_HEIGHT, command=lambda: self.change_piece_type(piece, "rook"))
            bishop_btn = Button(root, image=bishop_img, width=144, height=PROMOTION_HEIGHT, command=lambda: self.change_piece_type(piece, "bishop"))
            knight_btn = Button(root, image=knight_img, width=144, height=PROMOTION_HEIGHT, command=lambda: self.change_piece_type(piece, "knight"))

            queen_btn.grid(row=0, column=0)
            rook_btn.grid(row=0, column=1)
            bishop_btn.grid(row=0, column=2)
            knight_btn.grid(row=0, column=3)

            root.mainloop()