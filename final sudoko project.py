import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import time
import os

# ---------------- Sudoku Solver ----------------
def valid(board, num, pos):
    for j in range(9):
        if board[pos[0]][j] == num and pos[1] != j:
            return False
    for i in range(9):
        if board[i][pos[1]] == num and pos[0] != i:
            return False 
    box_x = pos[1] // 3
    box_y = pos[0] // 3
    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if board[i][j] == num and (i, j) != pos:
                return False
    return True

def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None

def solve(board):
    find = find_empty(board)
    if not find:
        return True
    else:
        row, col = find
    for num in range(1, 10):
        if valid(board, num, (row, col)):
            board[row][col] = num
            if solve(board):
                return True
            board[row][col] = 0
    return False

# ---------------- Sudoku Generator ----------------
def fill_diagonal_boxes(board):
    """Fill diagonal 3x3 boxes with random numbers (helps puzzle generation)."""
    for k in range(0, 9, 3):
        nums = list(range(1, 10))
        random.shuffle(nums)
        for i in range(3):
            for j in range(3):
                board[k+i][k+j] = nums.pop()

def generate_puzzle(difficulty="Medium"):
    board = [[0 for _ in range(9)] for _ in range(9)]
    fill_diagonal_boxes(board)
    solve(board)  # create a fully solved board

    if difficulty == "Easy":
        attempts = 35
    elif difficulty == "Hard":
        attempts = 55
    else:
        attempts = 45

    while attempts > 0:
        row = random.randint(0, 8)
        col = random.randint(0, 8)
        while board[row][col] == 0:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
        board[row][col] = 0
        attempts -= 1
    return board

# ---------------- Leaderboard Handling ----------------
def load_leaderboard():
    leaderboard = {"Easy": [], "Medium": [], "Hard": []}
    if os.path.exists("leaderboard.txt"):
        with open("leaderboard.txt", "r") as f:
            for line in f:
                diff, records = line.strip().split(":")
                entries = records.split(",") if records else []
                leaderboard[diff] = [(e.split("-")[0], int(e.split("-")[1])) for e in entries if "-" in e]
    return leaderboard

def save_leaderboard(leaderboard):
    with open("leaderboard.txt", "w") as f:
        for diff, records in leaderboard.items():
            line = ",".join([f"{name}-{t}" for name, t in records])
            f.write(f"{diff}:{line}\n")

# ---------------- GUI Class ----------------
class SudokuGUI:
    def __init__(self, root, board):
        self.root = root
        self.root.title("Sudoku Game")
        self.entries = [[None for _ in range(9)] for _ in range(9)]
        self.board = board
        self.difficulty = tk.StringVar(value="Medium")
        self.original_cells = set()  # Track which cells were originally filled

        self.start_time = time.time()
        self.running = True

        self.leaderboard = load_leaderboard()

        self.frame = tk.Frame(root, bg="black")
        self.frame.pack()

        self.draw_board()

        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        solve_btn = tk.Button(button_frame, text="Solve", command=self.solve_sudoku)
        solve_btn.grid(row=0, column=0, padx=10)

        check_btn = tk.Button(button_frame, text="Check", command=self.check_solution)
        check_btn.grid(row=0, column=1, padx=10)

        clear_btn = tk.Button(button_frame, text="Clear", command=self.clear_board)
        clear_btn.grid(row=0, column=2, padx=10)

        newgame_btn = tk.Button(button_frame, text="New Game", command=self.new_game)
        newgame_btn.grid(row=0, column=3, padx=10)

        leaderboard_btn = tk.Button(button_frame, text="Leaderboard", command=self.show_leaderboard)
        leaderboard_btn.grid(row=0, column=4, padx=10)

        # Difficulty options
        difficulty_frame = tk.Frame(root)
        difficulty_frame.pack(pady=5)

        tk.Label(difficulty_frame, text="Difficulty:").pack(side="left", padx=5)
        tk.OptionMenu(difficulty_frame, self.difficulty, "Easy", "Medium", "Hard").pack(side="left")

        # Timer
        self.timer_label = tk.Label(root, text="Time: 00:00", font=("Arial", 14))
        self.timer_label.pack(pady=5)

        self.update_timer()
        
    def draw_board(self):
        for i in range(9):
          for j in range(9):
            # Determine background color based on 3x3 box
            if (i // 3 + j // 3) % 2 == 0:
                bg_color = "#f0f0f0"  # Light gray
            else:
                bg_color = "#d9d9d9"  # Slightly darker gray

            # Determine border thickness for 3x3 box borders
            top = 2 if i % 3 == 0 else 1
            left = 2 if j % 3 == 0 else 1
            bottom = 2 if i == 8 else 0
            right = 2 if j == 8 else 0

            entry = tk.Entry(
                self.frame,
                width=2,
                font=("Arial", 18),
                justify="center",
                bg=bg_color,
                relief="solid",
                borderwidth=1,
            )

            entry.grid(
                row=i,
                column=j,
                ipady=5,
                padx=(left, right),
                pady=(top, bottom)
            )

            # If the cell has a value in the puzzle, display it
            if self.board[i][j] != 0:
                entry.insert(0, str(self.board[i][j]))
                entry.config(state="readonly", disabledbackground="#c9c9c9")
                self.original_cells.add((i, j))
            else:
                # Add validation to only allow numbers 1-9
                entry.config(validate="key",
                             validatecommand=(self.root.register(self.validate_input), '%P'))

            self.entries[i][j] = entry

                
       
    def validate_input(self, value):
        # Allow empty string or single digit from 1-9
        return value == "" or (value.isdigit() and 1 <= int(value) <= 9 and len(value) == 1)
    
    def update_timer(self):
        if self.running:
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.timer_label.config(text=f"Time: {minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_timer)
    
    def solve_sudoku(self):
        # Create a copy of the current board state
        current_board = [[0 for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                value = self.entries[i][j].get()
                current_board[i][j] = int(value) if value.isdigit() else 0
        
        # Solve the puzzle
        if solve(current_board):
            # Update the GUI with the solution
            for i in range(9):
                for j in range(9):
                    if (i, j) not in self.original_cells:
                        self.entries[i][j].delete(0, tk.END)
                        self.entries[i][j].insert(0, str(current_board[i][j]))
            self.running = False
            messagebox.showinfo("Solved", "The puzzle has been solved!")
        else:
            messagebox.showerror("Error", "This puzzle cannot be solved!")
    
    def check_solution(self):
        # Create a copy of the current board state
        current_board = [[0 for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                value = self.entries[i][j].get()
                current_board[i][j] = int(value) if value.isdigit() else 0
        
        # Check if the board is complete
        for i in range(9):
            for j in range(9):
                if current_board[i][j] == 0:
                    messagebox.showwarning("Incomplete", "The puzzle is not complete!")
                    return
        
        # Check if the solution is valid
        for i in range(9):
            for j in range(9):
                num = current_board[i][j]
                current_board[i][j] = 0  # Temporarily remove to check validity
                if not valid(current_board, num, (i, j)):
                    messagebox.showerror("Incorrect", "The solution is incorrect!")
                    current_board[i][j] = num  # Restore value
                    return
                current_board[i][j] = num  # Restore value
        
        # If we get here, the solution is correct
        self.running = False
        elapsed = int(time.time() - self.start_time)
        
        # Ask for player name and update leaderboard
        name = simpledialog.askstring("Congratulations!", 
                                     f"You solved the puzzle in {elapsed} seconds!\nEnter your name for the leaderboard:")
        if name:
            difficulty = self.difficulty.get()
            self.leaderboard[difficulty].append((name, elapsed))
            # Sort by time and keep top 10
            self.leaderboard[difficulty].sort(key=lambda x: x[1])
            self.leaderboard[difficulty] = self.leaderboard[difficulty][:10]
            save_leaderboard(self.leaderboard)
        
        messagebox.showinfo("Correct", "Congratulations! The solution is correct!")
    
    def clear_board(self):
        for i in range(9):
            for j in range(9):
                if (i, j) not in self.original_cells:
                    self.entries[i][j].delete(0, tk.END)
    
    def new_game(self):
        self.running = False
        self.frame.destroy()
        
        # Generate new puzzle with selected difficulty
        new_board = generate_puzzle(self.difficulty.get())
        
        # Reinitialize with new board
        self.__init__(self.root, new_board)
    
    def show_leaderboard(self):
        leaderboard_window = tk.Toplevel(self.root)
        leaderboard_window.title("Leaderboard")
        leaderboard_window.geometry("300x200")
        
        # Create a notebook for different difficulty tabs
        notebook = tk.ttk.Notebook(leaderboard_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        for difficulty in ["Easy", "Medium", "Hard"]:
            frame = tk.Frame(notebook)
            notebook.add(frame, text=difficulty)
            
            if not self.leaderboard[difficulty]:
                tk.Label(frame, text="No records yet", font=("Arial", 12)).pack(pady=20)
            else:
                for i, (name, time_val) in enumerate(self.leaderboard[difficulty]):
                    minutes = time_val // 60
                    seconds = time_val % 60
                    tk.Label(frame, 
                            text=f"{i+1}. {name}: {minutes:02d}:{seconds:02d}", 
                            font=("Arial", 10 if i < 3 else 9)).pack(anchor="w", padx=10)

# ---------------- Run Game ----------------
if __name__ == "__main__":
    sudoku_board = generate_puzzle("Medium")
    root = tk.Tk()
    game = SudokuGUI(root, sudoku_board)
    root.mainloop()