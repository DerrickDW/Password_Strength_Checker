import tkinter as tk
from tkinter import ttk, messagebox

# Import your functions from your checker file
from password_checker import (
    load_common_passwords,
    score_password,
    strength_label,
)

# If you added estimate_crack_times in password_checker.py, we’ll try to import it.
try:
    from password_checker import estimate_crack_times
except Exception:
    estimate_crack_times = None


def run_gui():
    root = tk.Tk()
    live_after_id = None

    def schedule_live_update(*_):
        nonlocal live_after_id
        # cancel the previous scheduled run if user is still typing
        if live_after_id is not None:
            root.after_cancel(live_after_id)

        # run check 300ms after the last keypress
        live_after_id = root.after(300, on_check)
        entry.bind("<KeyRelease>", schedule_live_update)
        root.bind("<Return>", on_check)
        entry.focus
        print("key release fired")

    # Load common passwords once at startup
    try:
        common_passwords = load_common_passwords("common_passwords.txt")
        common_loaded_msg = f"Loaded {len(common_passwords):,} common passwords."
    except FileNotFoundError:
        common_passwords = set()
        common_loaded_msg = (
            "common_passwords.txt not found (common-list check disabled)."
        )


    root.title("Password Strength Checker")
    root.geometry("640x520")

    pw_var = tk.StringVar()
    show_var = tk.BooleanVar(value=False)

    header = ttk.Label(
        root, text="Password Strength Checker", font=("Segoe UI", 16, "bold")
    )
    header.pack(anchor="w", padx=14, pady=(14, 6))

    status = ttk.Label(root, text=common_loaded_msg, font=("Segoe UI", 9))
    status.pack(anchor="w", padx=14, pady=(0, 10))

    # --- Input row ---
    frm = ttk.Frame(root)
    frm.pack(fill="x", padx=14)

    ttk.Label(frm, text="Password:").grid(row=0, column=0, sticky="w")
    entry = ttk.Entry(frm, textvariable=pw_var, show="*")
    entry.bind("<KeyRelease>", lambda e: print("KEY:", repr(e.widget.get())))
    entry.grid(row=1, column=0, sticky="ew", pady=(4, 0))

    frm.columnconfigure(0, weight=1)

    def update_show():
        entry.config(show="" if show_var.get() else "*")

    ttk.Checkbutton(frm, text="Show", variable=show_var, command=update_show).grid(
        row=1, column=1, padx=(10, 0), sticky="w"
    )

    # --- Results ---
    score_lbl = ttk.Label(root, text="Score: —/100", font=("Segoe UI", 12, "bold"))
    score_lbl.pack(anchor="w", padx=14, pady=(14, 2))

    strength_lbl = ttk.Label(root, text="Strength: —", font=("Segoe UI", 12, "bold"))
    strength_lbl.pack(anchor="w", padx=14, pady=(0, 10))

    # Progress bar
    bar = ttk.Progressbar(
        root, orient="horizontal", length=400, mode="determinate", maximum=100
    )
    bar.pack(fill="x", padx=14, pady=(0, 14))

    # Suggestions box
    ttk.Label(root, text="Suggestions:", font=("Segoe UI", 10, "bold")).pack(
        anchor="w", padx=14
    )
    suggestions = tk.Text(root, height=10, wrap="word")
    suggestions.pack(fill="both", expand=True, padx=14, pady=(6, 10))
    suggestions.config(state="disabled")

    # Crack time box (optional)
    ttk.Label(root, text="Crack-time estimates:", font=("Segoe UI", 10, "bold")).pack(
        anchor="w", padx=14
    )
    crack_box = tk.Text(root, height=6, wrap="word")
    crack_box.pack(fill="x", padx=14, pady=(6, 14))
    crack_box.config(state="disabled")

    def set_text(widget: tk.Text, text: str) -> None:
        widget.config(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, text)
        widget.config(state="disabled")

    def on_check(*_):
        pw = pw_var.get()
        if not pw:
            messagebox.showinfo("Missing password", "Type a password first.")
            return

        score, feedback = score_password(pw, common_passwords)
        label = strength_label(score)

        score_lbl.config(text=f"Score: {score}/100")
        strength_lbl.config(text=f"Strength: {label}")
        bar["value"] = score

        if feedback:
            set_text(suggestions, "\n".join(f"- {x}" for x in feedback))
        else:
            set_text(suggestions, "No suggestions. Nice work.")

        if estimate_crack_times is None:
            set_text(crack_box, "(Crack-time estimator not enabled.)")
        else:
            try:
                times = estimate_crack_times(pw)
                lines = ["Rough estimates (entropy model):"]
                for k, v in times.items():
                    lines.append(f"- {k}: {v}")
                set_text(crack_box, "\n".join(lines))
            except Exception as e:
                set_text(crack_box, f"(Estimator error: {e})")

    def on_clear():
        pw_var.set("")
        score_lbl.config(text="Score: —/100")
        strength_lbl.config(text="Strength: —")
        bar["value"] = 0
        set_text(suggestions, "")
        set_text(crack_box, "")
        entry.focus()

    # Buttons
    btns = ttk.Frame(root)
    btns.pack(fill="x", padx=14, pady=(0, 14))

    ttk.Button(btns, text="Check", command=on_check).pack(side="left")
    ttk.Button(btns, text="Clear", command=on_clear).pack(side="left", padx=(10, 0))

    # Enter triggers check
    root.bind("<Return>", on_check)

    entry.focus()
    root.mainloop()


if __name__ == "__main__":
    run_gui()
