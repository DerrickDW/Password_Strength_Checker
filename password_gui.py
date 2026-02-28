import tkinter as tk
from tkinter import ttk, messagebox
import os, sys


def resource_path(relative_path: str) -> str:
    # When packaged, PyInstaller puts files in a temp folder referenced by _MEIPASS
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)


from password_checker import (
    load_common_passwords,
    score_password,
    strength_label,
)

try:
    from password_checker import estimate_crack_times
except Exception:
    estimate_crack_times = None


def run_gui():
    root = tk.Tk()
    live_after_id = None

    # Load common passwords once at startup
    try:
        common_passwords = load_common_passwords(resource_path("common_passwords.txt"))
        common_loaded_msg = f"Loaded {len(common_passwords):,} common passwords."
    except FileNotFoundError:
        common_passwords = set()
        common_loaded_msg = (
            "common_passwords.txt not found (common-list check disabled)."
        )

    root.title("Password Strength Checker V1.0")
    root.geometry("850x720")
    root.minsize(800, 650)
    root.update_idletasks()

    width = 850
    height = 720
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)

    root.geometry(f"{width}x{height}+{x}+{y}")

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

    bar = ttk.Progressbar(
        root, orient="horizontal", length=400, mode="determinate", maximum=100
    )
    bar.pack(fill="x", padx=14, pady=(0, 14))

    ttk.Label(root, text="Suggestions:", font=("Segoe UI", 10, "bold")).pack(
        anchor="w", padx=14
    )
    suggestions = tk.Text(root, height=10, wrap="word")
    suggestions.pack(fill="both", expand=True, padx=14, pady=(6, 10))
    suggestions.config(state="disabled")

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

    def on_check(*_, live=False):
        pw = pw_var.get()

        # Empty: reset UI, no popup during live typing
        if not pw:
            score_lbl.config(text="Score: —/100")
            strength_lbl.config(text="Strength: —")
            bar["value"] = 0
            if not live:
                set_text(suggestions, "")
                set_text(crack_box, "")
            return

        # Quick feedback paint before heavier work
        score_lbl.config(text="Scoring...")
        root.update_idletasks()

        score, feedback = score_password(pw, common_passwords)
        label = strength_label(score)

        score_lbl.config(text=f"Score: {score}/100")
        strength_lbl.config(text=f"Strength: {label}")
        bar["value"] = score

        # Live typing: stop here (skip slow widgets)
        if live:
            return

        # Full update (Enter/button)
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

    def schedule_live_update(*_):
        nonlocal live_after_id
        if live_after_id is not None:
            try:
                root.after_cancel(live_after_id)
            except tk.TclError:
                pass
        live_after_id = root.after(150, lambda: on_check(live=True))

    entry.bind("<KeyRelease>", schedule_live_update)

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

    ttk.Button(btns, text="Check", command=lambda: on_check(live=False)).pack(
        side="left"
    )
    ttk.Button(btns, text="Clear", command=on_clear).pack(side="left", padx=(10, 0))

    # Enter triggers full check (bind once)
    root.bind("<Return>", lambda e: on_check(live=False))

    entry.focus()
    root.mainloop()


if __name__ == "__main__":
    run_gui()
