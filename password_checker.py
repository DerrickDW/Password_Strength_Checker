def score_password(pw: str) -> tuple[int, list[str]]:
    """
    Returns: (score_0_to_100, feedback_list)
    """
    score = 0
    feedback: list[str] = []

    # TODO: implement checks and update score/feedback
    # ---- LENGTH CHECK -----
    length = len(pw)

    if length < 8:
        feedback.append("Use at least 12 characters.")
    elif length < 12:
        score += 15
    elif length < 16:
        score += 30
    else:
        score += 40
   
    # ---- Character Variety ----
    if any(c.islower() for c in pw):
        score += 10
    else:
        feedback.append("Add lowercase letters.")

    if any(c.isupper() for c in pw):
        score += 10
    else:
        feedback.append("Add uppercase letters.")

    if any(c.isdigit() for c in pw):
        score += 10
    else:
        feedback.append("Add numbers.")

    if any(not c.isalnum() for c in pw):
        score += 10
    else:
        feedback.append("Add special characters.")
    # ---- BADS ----
    score = max(0, min(score, 100))
    return score, feedback
def strength_label(score: int) -> str:
     if score < 40:
        return "WEAK"
     elif score < 70:
        return "OKAY"
     else:
        return "STRONG"


def main() -> None:
    pw = input("Enter a password to check: ")

    score, feedback = score_password(pw)
    label = strength_label(score)

    print(f"\nScore: {score}/100")
    print(f"Strength: {label}")

    if feedback:
        print("\nSuggestions:")
        for item in feedback:
            print(f"- {item}")


def main() -> None:
    while True:
        pw = input("Enter a password to check (or type 'quit'): ")

        if pw.lower() == "quit":
            print("Goodbye.")
            break

        score, feedback = score_password(pw)
        label = strength_label(score)

        print(f"\nScore: {score}/100")
        print(f"Strength: {label}")

        if feedback:
            print("\nSuggestions:")
            for item in feedback:
                print(f"- {item}")

        print()


if __name__ == "__main__":
    main()