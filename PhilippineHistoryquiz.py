# quiz.py
# Philippine History Quiz - a desktop quiz game built with Python Tkinter.
# Colors: blue, red and yellow (inspired by the Philippine flag).

import tkinter as tk
from tkinter import messagebox
import random
import os

# ---------------------------------------------------------------
# QUIZ DATA: a list of dictionaries (question, four choices, answer letter)
# ---------------------------------------------------------------
QUESTIONS = [
    {
        "question": "Which leader is known as the \"Father of the Philippine Revolution\" for founding and leading the Katipunan?",
        "choices": ["A. Jose Rizal", "B. Emilio Aguinaldo", "C. Andres Bonifacio", "D. Apolinario Mabini"],
        "answer": "C"
    },
    {
        "question": "On which date did Emilio Aguinaldo proclaim Philippine independence in Kawit, Cavite?",
        "choices": ["A. June 12, 1898", "B. July 4, 1946", "C. August 23, 1896", "D. February 25, 1986"],
        "answer": "A"
    },
    {
        "question": "Which explorer sailing for Spain reached the Philippines in 1521 and was killed in the Battle of Mactan?",
        "choices": ["A. Miguel Lopez de Legazpi", "B. Juan Sebastian Elcano", "C. Ruy Lopez de Villalobos", "D. Ferdinand Magellan"],
        "answer": "D"
    },
    {
        "question": "Which novel by Jose Rizal, published in 1887, exposed the abuses of Spanish friars and officials?",
        "choices": ["A. El Filibusterismo", "B. Noli Me Tangere", "C. Mi Ultimo Adios", "D. Sobre la Indolencia de los Filipinos"],
        "answer": "B"
    },
    {
        "question": "Under the 1898 Treaty of Paris, Spain handed the Philippines over to which country?",
        "choices": ["A. Japan", "B. Great Britain", "C. The United States", "D. Germany"],
        "answer": "C"
    },
    {
        "question": "Who became the first President of the Commonwealth of the Philippines in 1935?",
        "choices": ["A. Manuel L. Quezon", "B. Sergio Osmena", "C. Manuel Roxas", "D. Ramon Magsaysay"],
        "answer": "A"
    },
    {
        "question": "The Bataan Death March of 1942 took place during which conflict?",
        "choices": ["A. The Spanish-American War", "B. The Philippine-American War", "C. World War I", "D. World War II"],
        "answer": "D"
    },
    {
        "question": "On what date did the United States recognize Philippine independence, creating the Third Republic?",
        "choices": ["A. June 12, 1898", "B. July 4, 1946", "C. September 21, 1972", "D. December 30, 1896"],
        "answer": "B"
    },
    {
        "question": "The 1986 People Power Revolution on EDSA led to which leader becoming President?",
        "choices": ["A. Fidel V. Ramos", "B. Joseph Estrada", "C. Corazon Aquino", "D. Diosdado Macapagal"],
        "answer": "C"
    },
    {
        "question": "Which Filipino, nicknamed the \"Sublime Paralytic\", served as the chief adviser of Emilio Aguinaldo?",
        "choices": ["A. Antonio Luna", "B. Marcelo H. del Pilar", "C. Gregorio del Pilar", "D. Apolinario Mabini"],
        "answer": "D"
    }
]

# ---------------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------------
TIME_LIMIT = 15  # seconds per question
HIGH_SCORE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "high_score.txt"
)

BLUE = "#0038A8"        # main color
DARK_BLUE = "#00246E"   # header and text
RED = "#CE1126"         # wrong answers, low time, accents
YELLOW = "#FCD116"      # highlights, progress fill
CREAM = "#FFF8DC"       # page background
TRACK = "#D9DEEA"       # empty part of a bar
WINDOW_W, BAR_W, BAR_H = 760, 680, 16

root = tk.Tk()
root.title("Philippine History Quiz")
root.geometry(f"{WINDOW_W}x700")
root.configure(bg=CREAM)
root.resizable(False, False)

# ---------------------------------------------------------------
# QUIZ STATE
# ---------------------------------------------------------------
quiz_questions = []      # shuffled copy of QUESTIONS
current_question = 0     # index of the current question
score = 0
time_left = TIME_LIMIT
wrong_answers = []       # details for the answer review
timer_job = None         # id from root.after(), needed to cancel the timer
answered = False         # True once the question is submitted / time is up
selected_answer = tk.StringVar()

# Widgets that change while the quiz runs
timer_label = None
feedback_label = None
submit_button = None
next_button = None
progress_bar = None
timer_bar = None
choice_buttons = []

main_frame = tk.Frame(root, bg=CREAM)
main_frame.pack(fill="both", expand=True)


# ---------------------------------------------------------------
# HIGH SCORE (file handling)
# ---------------------------------------------------------------
def get_high_score():
    """Read the saved high score. Return 0 if the file is missing or invalid."""
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "r") as file:
                return int(file.read().strip())
        except (ValueError, OSError):
            return 0
    return 0


def save_high_score(new_score):
    """Save the score only when it beats the old one. Return True if it did."""
    if new_score > get_high_score():
        try:
            with open(HIGH_SCORE_FILE, "w") as file:
                file.write(str(new_score))
            return True
        except OSError:
            return False
    return False


# ---------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------
def clear_screen():
    """Remove every widget so a new screen can reuse the same space."""
    for widget in main_frame.winfo_children():
        widget.destroy()


def get_choice_text(question, letter):
    """Turn a letter such as 'C' into its full choice text 'C. Andres Bonifacio'."""
    for choice in question["choices"]:
        if choice.startswith(letter + "."):
            return choice
    return "No answer (time is up)"


def make_header(title, subtitle=""):
    """Blue banner with a red and yellow stripe underneath."""
    banner = tk.Frame(main_frame, bg=BLUE)
    banner.pack(fill="x")
    tk.Label(banner, text=title, font=("Georgia", 24, "bold"),
             bg=BLUE, fg="white").pack(pady=(18, 2))
    if subtitle:
        tk.Label(banner, text=subtitle, font=("Helvetica", 11),
                 bg=BLUE, fg=YELLOW).pack(pady=(0, 14))
    stripe = tk.Frame(main_frame, bg=CREAM)
    stripe.pack(fill="x")
    tk.Frame(stripe, bg=RED, height=6).pack(fill="x")
    tk.Frame(stripe, bg=YELLOW, height=4).pack(fill="x")
    return banner


def make_bar():
    """Create an empty bar (a Canvas we draw on)."""
    return tk.Canvas(main_frame, width=BAR_W, height=BAR_H, bg=TRACK,
                     highlightthickness=0)


def draw_bar(bar, fraction, color):
    """Fill `fraction` (0 to 1) of the bar with `color`."""
    bar.delete("all")
    bar.create_rectangle(0, 0, BAR_W, BAR_H, fill=TRACK, outline="")
    bar.create_rectangle(0, 0, BAR_W * fraction, BAR_H, fill=color, outline="")


def lock_choices():
    """Disable the four answer buttons."""
    for button in choice_buttons:
        button.config(state="disabled")


def make_button(parent, text, command, bg, fg="white", width=14):
    return tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                     font=("Helvetica", 13, "bold"), width=width,
                     relief="flat", cursor="hand2", activebackground=DARK_BLUE,
                     activeforeground="white")


# ---------------------------------------------------------------
# SCREENS
# ---------------------------------------------------------------
def show_start_screen():
    clear_screen()
    make_header("Philippine History Quiz", "Test what you know about our nation's past")
    tk.Label(main_frame, text=f"{len(QUESTIONS)} questions  |  {TIME_LIMIT} seconds each",
             font=("Helvetica", 14), bg=CREAM, fg=DARK_BLUE).pack(pady=(50, 8))
    tk.Label(main_frame, text=f"High Score: {get_high_score()} / {len(QUESTIONS)}",
             font=("Georgia", 22, "bold"), bg=CREAM, fg=RED).pack(pady=15)
    tk.Label(main_frame, text="Pick one answer, press Submit, then Next.\nBeat the clock!",
             font=("Helvetica", 12), bg=CREAM, fg=DARK_BLUE, justify="center").pack(pady=10)
    make_button(main_frame, "Start Quiz", start_quiz, BLUE, width=18).pack(pady=30)


def start_quiz():
    """Reset everything and shuffle the questions (also used by Restart)."""
    global quiz_questions, current_question, score, wrong_answers
    quiz_questions = random.sample(QUESTIONS, len(QUESTIONS))  # new shuffled list
    current_question = 0
    score = 0
    wrong_answers = []
    show_question()


def show_question():
    global time_left, answered, timer_label, feedback_label
    global submit_button, next_button, choice_buttons, progress_bar, timer_bar

    clear_screen()
    answered = False
    selected_answer.set("")
    time_left = TIME_LIMIT
    question = quiz_questions[current_question]
    total = len(quiz_questions)

    make_header("Philippine History Quiz")

    # Progress: text + progress bar (questions completed so far)
    info = tk.Frame(main_frame, bg=CREAM)
    info.pack(fill="x", padx=40, pady=(14, 4))
    tk.Label(info, text=f"Question {current_question + 1} of {total}",
             font=("Helvetica", 14, "bold"), bg=CREAM, fg=DARK_BLUE).pack(side="left")
    tk.Label(info, text=f"Score: {score}", font=("Helvetica", 13),
             bg=CREAM, fg=DARK_BLUE).pack(side="left", padx=25)
    timer_label = tk.Label(info, text="", font=("Helvetica", 14, "bold"),
                           bg=CREAM, fg=DARK_BLUE)
    timer_label.pack(side="right")

    progress_bar = make_bar()
    progress_bar.pack(pady=(0, 6))
    draw_bar(progress_bar, current_question / total, BLUE)

    # Time bar (shrinks every second, turns yellow then red)
    timer_bar = make_bar()
    timer_bar.pack(pady=(0, 6))
    draw_bar(timer_bar, 1, YELLOW)

    # Question text
    tk.Label(main_frame, text=question["question"], font=("Georgia", 16, "bold"),
             wraplength=660, justify="left", bg=CREAM, fg=DARK_BLUE).pack(
        padx=40, pady=(16, 10), anchor="w")

    # Four choices. The value of each button is its letter (A to D).
    choice_buttons = []
    for choice in question["choices"]:
        letter = choice[0]
        button = tk.Radiobutton(main_frame, text=choice, variable=selected_answer,
                                value=letter, font=("Helvetica", 13), anchor="w",
                                bg="white", fg=DARK_BLUE, selectcolor=YELLOW,
                                activebackground=YELLOW, padx=14, pady=6,
                                relief="flat", cursor="hand2")
        button.pack(fill="x", padx=40, pady=4)
        choice_buttons.append(button)

    feedback_label = tk.Label(main_frame, text="", font=("Helvetica", 13, "bold"),
                              bg=CREAM, wraplength=660)
    feedback_label.pack(pady=(10, 4))

    buttons = tk.Frame(main_frame, bg=CREAM)
    buttons.pack(pady=6)
    submit_button = make_button(buttons, "Submit", submit_answer, RED)
    submit_button.pack(side="left", padx=8)
    next_button = make_button(buttons, "Next", next_question, BLUE)
    next_button.config(state="disabled")
    next_button.pack(side="left", padx=8)

    update_timer()  # start the countdown


# ---------------------------------------------------------------
# TIMER
# ---------------------------------------------------------------
def update_timer():
    """Show the time left, then call itself again after 1 second."""
    global time_left, timer_job
    if answered:                      # stop counting once the question is done
        return
    timer_label.config(text=f"Time left: {time_left}s")
    color = YELLOW if time_left > 8 else (RED if time_left <= 5 else "#F28C28")
    draw_bar(timer_bar, time_left / TIME_LIMIT, color)
    if time_left <= 5:
        timer_label.config(fg=RED)
    if time_left == 0:
        time_up()
        return
    time_left -= 1
    timer_job = root.after(1000, update_timer)


def stop_timer():
    """Cancel the scheduled timer call."""
    global timer_job
    if timer_job is not None:
        root.after_cancel(timer_job)
        timer_job = None


# ---------------------------------------------------------------
# ANSWER CHECKING
# ---------------------------------------------------------------
def finish_question(your_answer, is_correct, message, color):
    """Shared ending for Submit and Time-up: lock, feedback, update bar."""
    global score
    question = quiz_questions[current_question]
    if is_correct:
        score += 1
    else:
        wrong_answers.append({
            "question": question["question"],
            "your_answer": your_answer,
            "correct_answer": get_choice_text(question, question["answer"]),
        })
    lock_choices()
    submit_button.config(state="disabled")
    feedback_label.config(text=message, fg=color)
    draw_bar(progress_bar, (current_question + 1) / len(quiz_questions), BLUE)
    next_button.config(state="normal")


def submit_answer():
    global answered
    if answered:                                  # blocks double submission
        return
    choice = selected_answer.get()
    if choice == "":
        messagebox.showwarning("No answer", "Please select an answer first.")
        return                                    # timer keeps running

    answered = True
    stop_timer()
    question = quiz_questions[current_question]
    if choice == question["answer"]:              # the answer check
        finish_question(get_choice_text(question, choice), True, "Correct! Mabuhay!", BLUE)
    else:
        correct = get_choice_text(question, question["answer"])
        finish_question(get_choice_text(question, choice), False,
                        f"Wrong! The correct answer is {correct}", RED)


def time_up():
    """Called when the countdown reaches zero: counted as wrong."""
    global answered
    if answered:
        return
    answered = True
    stop_timer()
    question = quiz_questions[current_question]
    correct = get_choice_text(question, question["answer"])
    finish_question("No answer (time is up)", False,
                    f"Time is up! The correct answer is {correct}", RED)


def next_question():
    global current_question
    current_question += 1
    if current_question < len(quiz_questions):
        show_question()
    else:
        show_results()


# ---------------------------------------------------------------
# RESULTS
# ---------------------------------------------------------------
def show_results():
    clear_screen()
    total = len(quiz_questions)
    percentage = (score / total) * 100
    new_record = save_high_score(score)

    if percentage >= 90:
        message = "Outstanding! You are a true history buff!"
    elif percentage >= 70:
        message = "Good job! You know your history."
    elif percentage >= 50:
        message = "Not bad. Keep studying our history!"
    else:
        message = "Review the lessons and try again."

    make_header("Quiz Complete!")
    tk.Label(main_frame, text=f"{score} / {total}", font=("Georgia", 34, "bold"),
             bg=CREAM, fg=BLUE).pack(pady=(14, 0))
    tk.Label(main_frame, text=f"{percentage:.0f}%  -  {message}",
             font=("Helvetica", 14, "bold"), bg=CREAM, fg=DARK_BLUE).pack()
    if new_record:
        tk.Label(main_frame, text="NEW HIGH SCORE!", font=("Helvetica", 14, "bold"),
                 bg=YELLOW, fg=DARK_BLUE, padx=14, pady=3).pack(pady=6)
    else:
        tk.Label(main_frame, text=f"High Score: {get_high_score()} / {total}",
                 font=("Helvetica", 12), bg=CREAM, fg=RED).pack(pady=6)

    # Buttons first (packed at the bottom) so they never get pushed off screen
    buttons = tk.Frame(main_frame, bg=CREAM)
    buttons.pack(side="bottom", pady=14)
    make_button(buttons, "Restart", start_quiz, BLUE).pack(side="left", padx=8)
    make_button(buttons, "Exit", on_close, RED).pack(side="left", padx=8)

    # Answer review (only incorrect answers)
    tk.Label(main_frame, text="Answer Review", font=("Georgia", 14, "bold"),
             bg=CREAM, fg=DARK_BLUE).pack(anchor="w", padx=40)
    review_frame = tk.Frame(main_frame, bg=CREAM)
    review_frame.pack(fill="both", expand=True, padx=40, pady=(4, 0))
    scrollbar = tk.Scrollbar(review_frame)
    scrollbar.pack(side="right", fill="y")
    review_box = tk.Text(review_frame, height=9, wrap="word", font=("Helvetica", 11),
                         bg="white", fg=DARK_BLUE, yscrollcommand=scrollbar.set)
    review_box.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=review_box.yview)

    if not wrong_answers:
        review_box.insert("end", "Perfect score! You answered every question correctly.")
    for number, item in enumerate(wrong_answers, start=1):
        review_box.insert("end", f"{number}. {item['question']}\n")
        review_box.insert("end", f"   Your answer: {item['your_answer']}\n")
        review_box.insert("end", f"   Correct answer: {item['correct_answer']}\n\n")
    review_box.config(state="disabled")      # read-only


def on_close():
    """Cancel the timer before closing so no error appears."""
    stop_timer()
    root.destroy()


if __name__ == "__main__":
    root.protocol("WM_DELETE_WINDOW", on_close)
    show_start_screen()
    root.mainloop()
