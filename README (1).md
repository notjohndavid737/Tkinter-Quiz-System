# Philippine History Quiz (Tkinter)

**Name:** John David I. Dalawis
**Section:** SE-3A
**Topic:** Philippine History

A desktop quiz game made with Python Tkinter. It has 10 multiple-choice questions, a 15-second timer for each question, a results screen with an answer review, a high score saved in a text file, and a Restart button. The colors are blue, red and yellow, like the Philippine flag.

## How to run

1. Install Python 3 (from python.org, keep Tcl/Tk selected). On Linux: `sudo apt install python3-tk`.
2. Open a terminal in this folder and run:

```
python quiz.py
```

## Features completed

- [x] Exactly 10 multiple-choice questions about Philippine history
- [x] Four choices (A to D), one correct answer each
- [x] Questions are shuffled every time the quiz starts or restarts
- [x] 15-second countdown shown on screen; time-out counts as wrong
- [x] Submit checks the answer automatically
- [x] No double submission; the timer stops on submit
- [x] 1 point per correct answer
- [x] "Question X of 10" label, time left, and a **progress bar** plus a shrinking **time bar**
- [x] Results screen with score, percentage and a performance message
- [x] Answer review of every wrong answer with the correct answer
- [x] High score saved in `high_score.txt`
- [x] Restart button (and Exit button)
- [x] Own design: blue, red and yellow theme, Georgia headings, color feedback

## How it works (explanations)

**Questions.** Every question is a dictionary with three keys: `question`, `choices` (a list of four strings that start with "A.", "B.", ...) and `answer` (one letter). The ten dictionaries sit inside the list `QUESTIONS`. When the quiz starts, `random.sample(QUESTIONS, len(QUESTIONS))` makes a new shuffled list called `quiz_questions`, so the original list is never changed and the order is different each time.

**Timer.** `show_question()` sets `time_left` to 15 and calls `update_timer()`. That function writes the time on screen, redraws the time bar, subtracts 1 and uses `root.after(1000, update_timer)` to run itself again one second later. The id that `after()` returns is stored in `timer_job`. When the player submits, `stop_timer()` calls `root.after_cancel(timer_job)`, and `update_timer()` also returns right away if `answered` is `True`. If `time_left` reaches 0, `time_up()` runs.

**Correct answer.** Each Radiobutton uses the first letter of its choice as its value, so the variable `selected_answer` always holds "A", "B", "C" or "D". In `submit_answer()` the program compares that letter with `question["answer"]`. If they are equal the answer is correct.

**Score.** `score` starts at 0 and goes up by 1 for each correct answer (inside `finish_question()`). The percentage is `(score / total) * 100`, where `total` is the number of questions. An `if / elif / else` chain picks the performance message (90% and up, 70% and up, 50% and up, or lower).

**High score.** `get_high_score()` opens `high_score.txt`, reads the number and returns it (or 0 if the file is missing or damaged). `save_high_score()` writes the new score to the file only if it is higher than the old one, and returns `True` so the results screen can show "NEW HIGH SCORE!". The file path uses `os.path.dirname(os.path.abspath(__file__))`, so the file stays next to `quiz.py`. The screenshot `screenshots/05_high_score_after_reopen.png` shows the score still there after closing and reopening.

## Function table

| Function | Purpose | Called when |
| --- | --- | --- |
| `show_start_screen()` | Shows the title, number of questions, time limit, high score and Start button | The program opens |
| `start_quiz()` | Resets the variables and shuffles the questions | Start or Restart is clicked |
| `show_question()` | Builds the question page, progress bar, choices and buttons | Each new question |
| `update_timer()` | Shows the time left, redraws the time bar and counts down every second | A question is displayed |
| `stop_timer()` | Cancels the scheduled timer call | An answer is submitted or time is up |
| `submit_answer()` | Checks the selected answer, blocks double submission, updates the score | Submit is clicked |
| `time_up()` | Marks the question wrong with "No answer (time is up)" | The countdown reaches 0 |
| `finish_question()` | Locks the choices, shows feedback, saves wrong answers, fills the progress bar | After Submit or time-up |
| `next_question()` | Moves to the next question or to the results | Next is clicked |
| `show_results()` | Shows score, percentage, message, high score and the answer review | After question 10 |
| `get_high_score()` / `save_high_score()` | Read and write the high score file | Start screen and results screen |
| `on_close()` | Stops the timer, then closes the window | The window is closed or Exit is clicked |

## Screenshots

See the `screenshots` folder: start screen, question with timer, answer feedback, results with review, and high score after reopening.
