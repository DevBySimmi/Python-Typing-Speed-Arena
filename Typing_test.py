import tkinter as tk
from tkinter import messagebox
import random
import time
import json
import os


# ---------------------------------
# SETTINGS
# ---------------------------------

BG = "#0B1020"
PANEL = "#151F33"
INPUT_BG = "#101827"
CYAN = "#67F5D4"
WHITE = "#E6EDF7"
MUTED = "#9CA3AF"
RED = "#FF6B81"
BORDER = "#26334B"

BEST_FILE = "typing_best.json"

SENTENCES = [
    "Practice every day and improve your typing speed with focus, patience, and consistency.",
    "Python is a powerful programming language for beginners and experienced developers.",
    "Great things happen when you stay curious and keep learning something new every day.",
    "Technology helps people solve problems and build creative solutions for the future.",
    "Success comes from small improvements repeated consistently over a long period of time.",
    "Learning to code teaches you how to think logically and solve difficult problems.",
    "Stay focused on your goals and remember that progress matters more than perfection.",
    "Every expert was once a beginner who decided not to give up on learning.",
    "Creativity and technology together can turn simple ideas into useful projects.",
    "A good programmer writes code that is easy to understand, test, and improve."
]


# ---------------------------------
# MAIN WINDOW
# ---------------------------------

root = tk.Tk()
root.title("Typing Speed Arena")
root.geometry("850x720")
root.minsize(760, 650)
root.configure(bg=BG)

duration_var = tk.IntVar(value=60)

current_text = ""
start_time = None
timer_job = None
test_running = False
test_finished = False
best_wpm = 0


# ---------------------------------
# LOAD PERSONAL BEST
# ---------------------------------

def load_best():
    global best_wpm

    try:
        if os.path.exists(BEST_FILE):
            with open(BEST_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                best_wpm = int(data.get("best_wpm", 0))
    except (OSError, ValueError, json.JSONDecodeError):
        best_wpm = 0


def save_best():
    try:
        with open(BEST_FILE, "w", encoding="utf-8") as file:
            json.dump({"best_wpm": best_wpm}, file, indent=4)
    except OSError:
        pass


# ---------------------------------
# TEXT AND STATISTICS
# ---------------------------------

def get_typed_text():
    return typing_box.get("1.0", "end-1c")


def calculate_stats():
    typed = get_typed_text()
    elapsed = 0

    if start_time is not None:
        elapsed = time.monotonic() - start_time

    # Use at least one second to avoid division by zero.
    elapsed_minutes = max(elapsed / 60, 1 / 60)

    correct_chars = sum(
        1 for i, char in enumerate(typed)
        if i < len(current_text) and char == current_text[i]
    )

    total_typed = len(typed)

    # WPM is based on correctly typed characters.
    wpm = int((correct_chars / 5) / elapsed_minutes)

    if total_typed == 0:
        accuracy = 100
    else:
        accuracy = round((correct_chars / total_typed) * 100)

    return wpm, accuracy, correct_chars, total_typed


def update_stats():
    wpm, accuracy, correct, total = calculate_stats()

    wpm_value.config(text=str(wpm))
    accuracy_value.config(text=f"{accuracy}%")

    if total:
        progress_label.config(
            text=f"Correct characters: {correct} / {total}"
        )
    else:
        progress_label.config(text="Start typing to begin the test")


def update_text_colors():
    typed = get_typed_text()

    display_box.config(state="normal")
    display_box.delete("1.0", "end")

    for i, char in enumerate(current_text):
        if i < len(typed):
            if typed[i] == char:
                color = CYAN
            else:
                color = RED
        else:
            color = "#8190A8"

        display_box.insert("end", char, f"char_{i}")
        display_box.tag_config(f"char_{i}", foreground=color)

    display_box.config(state="disabled")


# ---------------------------------
# TIMER
# ---------------------------------

def update_timer():
    global timer_job, test_running, test_finished

    if not test_running:
        return

    elapsed = time.monotonic() - start_time
    remaining = max(0, duration_var.get() - int(elapsed))

    timer_value.config(text=f"{remaining}s")
    update_stats()

    if remaining <= 0:
        finish_test()
        return

    timer_job = root.after(100, update_timer)


def start_test_if_needed(event=None):
    global start_time, test_running, test_finished, timer_job

    if test_finished:
        return "break"

    if not test_running:
        test_running = True
        start_time = time.monotonic()
        status_label.config(
            text="● TEST IN PROGRESS",
            fg=CYAN
        )
        update_timer()

    return None


# ---------------------------------
# TYPING EVENTS
# ---------------------------------

def on_typing(event=None):
    if test_finished:
        return "break"

    # Start the timer on the first real character.
    if get_typed_text():
        start_test_if_needed()

    update_text_colors()
    update_stats()

    typed = get_typed_text()

    if typed == current_text:
        finish_test()

    return None


# ---------------------------------
# FINISH TEST
# ---------------------------------

def finish_test():
    global test_running, test_finished, timer_job, best_wpm

    if test_finished:
        return

    test_running = False
    test_finished = True

    if timer_job is not None:
        root.after_cancel(timer_job)
        timer_job = None

    wpm, accuracy, correct, total = calculate_stats()

    if wpm > best_wpm:
        best_wpm = wpm
        save_best()

    best_value.config(text=str(best_wpm))
    status_label.config(text="✓ TEST COMPLETED", fg=CYAN)

    typing_box.config(state="disabled")
    update_stats()

    messagebox.showinfo(
        "Test Completed",
        f"Typing Test Finished!\n\n"
        f"Speed: {wpm} WPM\n"
        f"Accuracy: {accuracy}%\n"
        f"Correct characters: {correct}/{total}\n"
        f"Personal best: {best_wpm} WPM"
    )


# ---------------------------------
# NEW TEST / RESTART
# ---------------------------------

def new_test():
    global current_text, start_time, timer_job
    global test_running, test_finished

    if timer_job is not None:
        root.after_cancel(timer_job)
        timer_job = None

    test_running = False
    test_finished = False
    start_time = None

    current_text = random.choice(SENTENCES)

    display_box.config(state="normal")
    display_box.delete("1.0", "end")
    display_box.insert("1.0", current_text)
    display_box.config(state="disabled")

    typing_box.config(state="normal")
    typing_box.delete("1.0", "end")

    # Reset the timer and statistics.
    timer_value.config(text=f"{duration_var.get()}s")
    wpm_value.config(text="0")
    accuracy_value.config(text="100%")
    progress_label.config(text="Start typing to begin the test")
    status_label.config(text="● READY TO START", fg=MUTED)
    typing_box.focus_set()


def change_duration(*args):
    if not test_running:
        new_test()


# ---------------------------------
# BUTTON HELPER
# ---------------------------------

def make_button(parent, text, command, color=PANEL):
    return tk.Button(
        parent,
        text=text,
        command=command,
        font=("Arial", 10, "bold"),
        bg=color,
        fg=WHITE,
        activebackground="#263650",
        activeforeground=CYAN,
        relief="flat",
        cursor="hand2",
        padx=14,
        pady=9,
        bd=0
    )


# ---------------------------------
# HEADER
# ---------------------------------

header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=28, pady=(22, 10))

tk.Label(
    header,
    text="TYPING ARENA",
    font=("Arial", 25, "bold"),
    bg=BG,
    fg=CYAN
).pack(anchor="w")

tk.Label(
    header,
    text="NEURAL INTERFACE  //  TYPING TRAINING SYSTEM",
    font=("Consolas", 9),
    bg=BG,
    fg=MUTED
).pack(anchor="w", pady=(4, 0))


# ---------------------------------
# STAT CARDS
# ---------------------------------

stats_frame = tk.Frame(root, bg=BG)
stats_frame.pack(fill="x", padx=28, pady=10)


def make_stat_card(parent, title, initial_value):
    card = tk.Frame(
        parent,
        bg=PANEL,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    tk.Label(
        card,
        text=title,
        font=("Arial", 10, "bold"),
        bg=PANEL,
        fg=MUTED
    ).pack(pady=(12, 3))

    value = tk.Label(
        card,
        text=initial_value,
        font=("Consolas", 23, "bold"),
        bg=PANEL,
        fg=CYAN
    )
    value.pack(pady=(0, 12))

    return card, value


card1, wpm_value = make_stat_card(stats_frame, "SPEED (WPM)", "0")
card2, accuracy_value = make_stat_card(stats_frame, "ACCURACY", "100%")
card3, timer_value = make_stat_card(stats_frame, "TIME LEFT", "60s")
card4, best_value = make_stat_card(stats_frame, "PERSONAL BEST", "0")

for card in (card1, card2, card3, card4):
    card.pack(side="left", expand=True, fill="x", padx=4)


# ---------------------------------
# TEST SETTINGS
# ---------------------------------

settings = tk.Frame(root, bg=BG)
settings.pack(fill="x", padx=32, pady=(8, 10))

tk.Label(
    settings,
    text="TEST DURATION",
    font=("Arial", 10, "bold"),
    bg=BG,
    fg=MUTED
).pack(side="left", padx=(0, 12))

for seconds in (30, 60, 120):
    tk.Radiobutton(
        settings,
        text=f"{seconds} seconds",
        variable=duration_var,
        value=seconds,
        command=change_duration,
        bg=BG,
        fg=WHITE,
        selectcolor=PANEL,
        activebackground=BG,
        activeforeground=CYAN,
        font=("Arial", 10)
    ).pack(side="left", padx=5)


# ---------------------------------
# TARGET TEXT
# ---------------------------------

target_panel = tk.Frame(
    root,
    bg=PANEL,
    highlightbackground=BORDER,
    highlightthickness=1
)
target_panel.pack(fill="x", padx=32, pady=5)

tk.Label(
    target_panel,
    text="TYPE THE TEXT BELOW",
    font=("Arial", 10, "bold"),
    bg=PANEL,
    fg=CYAN
).pack(anchor="w", padx=15, pady=(12, 5))

display_box = tk.Text(
    target_panel,
    height=4,
    wrap="word",
    font=("Consolas", 13),
    bg=PANEL,
    fg=WHITE,
    relief="flat",
    padx=10,
    pady=5,
    cursor="arrow",
    state="disabled"
)
display_box.pack(fill="x", padx=10, pady=(0, 10))


# ---------------------------------
# TYPING INPUT
# ---------------------------------

tk.Label(
    root,
    text="YOUR INPUT",
    font=("Arial", 10, "bold"),
    bg=BG,
    fg=MUTED
).pack(anchor="w", padx=34, pady=(12, 5))

typing_box = tk.Text(
    root,
    height=4,
    wrap="word",
    font=("Consolas", 13),
    bg=INPUT_BG,
    fg=WHITE,
    insertbackground=CYAN,
    selectbackground="#245C64",
    relief="flat",
    padx=12,
    pady=10,
    highlightbackground=BORDER,
    highlightthickness=1
)
typing_box.pack(fill="x", padx=32)

typing_box.bind("<KeyRelease>", on_typing)
typing_box.bind("<KeyPress>", start_test_if_needed)


# ---------------------------------
# STATUS AND PROGRESS
# ---------------------------------

status_frame = tk.Frame(root, bg=BG)
status_frame.pack(fill="x", padx=34, pady=(10, 4))

status_label = tk.Label(
    status_frame,
    text="● READY TO START",
    font=("Consolas", 10, "bold"),
    bg=BG,
    fg=MUTED
)
status_label.pack(side="left")

progress_label = tk.Label(
    status_frame,
    text="Start typing to begin the test",
    font=("Arial", 9),
    bg=BG,
    fg=MUTED
)
progress_label.pack(side="right")


# ---------------------------------
# ACTION BUTTONS
# ---------------------------------

button_frame = tk.Frame(root, bg=BG)
button_frame.pack(pady=16)

make_button(
    button_frame,
    "↻ NEW TEST",
    new_test,
    color="#123B3A"
).pack(side="left", padx=6)

make_button(
    button_frame,
    "FINISH TEST",
    finish_test,
    color="#352235"
).pack(side="left", padx=6)


# ---------------------------------
# FOOTER
# ---------------------------------

tk.Label(
    root,
    text="FOCUS  •  TYPE  •  IMPROVE",
    font=("Consolas", 9),
    bg=BG,
    fg="#53627B"
).pack(side="bottom", pady=12)


# ---------------------------------
# START APPLICATION
# ---------------------------------

load_best()
best_value.config(text=str(best_wpm))
new_test()

root.mainloop()