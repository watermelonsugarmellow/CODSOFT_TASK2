import random

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:         
    tk = None

LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
         (0, 3, 6), (1, 4, 7), (2, 5, 8),
         (0, 4, 8), (2, 4, 6)]
HUMAN, AI = "X", "O"


def check_winner(board):
    for line in LINES:
        a, b, c = line
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a], line
    return None


def free_squares(board):
    return [i for i, v in enumerate(board) if v == " "]


def minimax(board, player, depth, max_depth, alpha, beta, pruning, stats):
    stats["nodes"] += 1
    result = check_winner(board)
    if result:
        return 10 - depth if result[0] == AI else depth - 10
    moves = free_squares(board)
    if not moves or depth >= max_depth:
        return 0

    if player == AI:
        best = -float("inf")
        for m in moves:
            board[m] = AI
            best = max(best, minimax(board, HUMAN, depth + 1, max_depth, alpha, beta, pruning, stats))
            board[m] = " "
            if pruning:
                alpha = max(alpha, best)
                if beta <= alpha:
                    break
        return best
    best = float("inf")
    for m in moves:
        board[m] = HUMAN
        best = min(best, minimax(board, AI, depth + 1, max_depth, alpha, beta, pruning, stats))
        board[m] = " "
        if pruning:
            beta = min(beta, best)
            if beta <= alpha:
                break
    return best


def choose_move(board, level="Hard", pruning=True):
    stats = {"nodes": 0}
    moves = free_squares(board)
    if level == "Easy":
        return random.choice(moves), stats

    max_depth = 2 if level == "Medium" else 9
    best_score, best_moves = -float("inf"), []
    for m in moves:
        board[m] = AI
        score = minimax(board, HUMAN, 1, max_depth, -float("inf"), float("inf"), pruning, stats)
        board[m] = " "
        if score > best_score:
            best_score, best_moves = score, [m]
        elif score == best_score:
            best_moves.append(m)
    return random.choice(best_moves), stats      


class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        root.title("Tic-Tac-Toe AI")
        self.board = [" "] * 9
        self.game_over = False
        self.score = {"You": 0, "AI": 0, "Draws": 0}

        top = ttk.Frame(root, padding=8)
        top.pack()
        ttk.Label(top, text="Difficulty:").grid(row=0, column=0)
        self.level = ttk.Combobox(top, values=["Easy", "Medium", "Hard"], width=8, state="readonly")
        self.level.set("Hard")
        self.level.grid(row=0, column=1, padx=4)
        ttk.Label(top, text="First move:").grid(row=0, column=2)
        self.first = ttk.Combobox(top, values=["You", "AI"], width=6, state="readonly")
        self.first.set("You")
        self.first.grid(row=0, column=3, padx=4)

        grid = ttk.Frame(root, padding=8)
        grid.pack()
        self.buttons = []
        for i in range(9):
            b = tk.Button(grid, text=" ", width=4, height=1, font=("Helvetica", 32, "bold"),
                          command=lambda i=i: self.human_move(i))
            b.grid(row=i // 3, column=i % 3, padx=2, pady=2)
            self.buttons.append(b)
        self.default_bg = self.buttons[0].cget("bg")

        self.status = tk.StringVar()
        self.info = tk.StringVar()
        self.scoreboard = tk.StringVar()
        ttk.Label(root, textvariable=self.status, font=("Helvetica", 13, "bold")).pack()
        ttk.Label(root, textvariable=self.info).pack()
        ttk.Label(root, textvariable=self.scoreboard).pack(pady=4)

        bottom = ttk.Frame(root, padding=8)
        bottom.pack()
        ttk.Button(bottom, text="New game", command=self.new_game).pack()

        self.update_score()
        self.new_game()

    def update_score(self):
        s = self.score
        self.scoreboard.set(f"You: {s['You']}    AI: {s['AI']}    Draws: {s['Draws']}")

    def new_game(self):
        self.board = [" "] * 9
        self.game_over = False
        for b in self.buttons:
            b.config(text=" ", state="normal", bg=self.default_bg)
        self.info.set("")
        if self.first.get() == "AI":
            self.status.set("AI is thinking...")
            self.root.after(300, self.ai_move)
        else:
            self.status.set("Your turn (X)")

    def human_move(self, i):
        if self.game_over or self.board[i] != " ":
            return
        self.place(i, HUMAN)
        if not self.finish_if_over():
            self.status.set("AI is thinking...")
            self.root.after(300, self.ai_move)

    def ai_move(self):
        if self.game_over:
            return
        move, stats = choose_move(self.board, self.level.get(), pruning=True)
        self.place(move, AI)
        if self.level.get() != "Easy":
            self.info.set(f"AI searched {stats['nodes']:,} positions (with alpha-beta pruning)")
        else:
            self.info.set("Easy mode: AI picked a random square")
        if not self.finish_if_over():
            self.status.set("Your turn (X)")

    def place(self, i, player):
        self.board[i] = player
        self.buttons[i].config(text=player, fg="#c0392b" if player == HUMAN else "#2471a3")

    def finish_if_over(self):
        result = check_winner(self.board)
        if result:
            player, line = result
            for i in line:
                self.buttons[i].config(bg="#a9dfbf")
            self.status.set("You win!" if player == HUMAN else "AI wins!")
            self.score["You" if player == HUMAN else "AI"] += 1
        elif not free_squares(self.board):
            self.status.set("It's a draw!")
            self.score["Draws"] += 1
        else:
            return False
        self.game_over = True
        self.update_score()
        return True


if __name__ == "__main__":
    if tk is None:
        raise SystemExit("Tkinter is not installed. On Ubuntu: sudo apt install python3-tk")
    app_root = tk.Tk()
    TicTacToeApp(app_root)
    app_root.mainloop()