import math
def load_common_passwords(path: str) -> set[str]:
    with open(path, "r", encoding="utf-8") as f:
        return {line.strip().lower() for line in f if line.strip()}
    
def score_password(pw: str, common_passwords: set[str]) -> tuple[int, list[str]]:

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
    if " " in pw:
        score -= 10
        feedback.append("avoid spaces.")
    lower_pw = pw.lower()
    common_patterns = ["password", "qwerty", "admin", "letmein", "iloveyou", "1234", "123456","1111", "abcd"]
    
    if any(pat in lower_pw for pat in common_patterns):
        score -= 20
        feedback.append("Avoid common patterns/words (e.g. 'password', '1234', 'admin' '1234')")
    if any(pw.count(ch) >= max(4, len(pw) // 2)for ch in set(pw)):
        score -= 10
        feedback.append("Avoid repeated characters (e.g., 'aaaa', '1111')")
    sequences = ["abcdefghijklmnopqrstuvwxyz", "0123456789"]
    for seq in sequences:
        for i in range(len(seq) -3):
            if seq[i:i+4] in lower_pw:
                score -=15
                feedback.append("Avoid sequential patterns like 'abcd' or '1234'.")
                break
    score += min(len(pw) * 2, 20)
    lower_pw = pw.lower()
    if lower_pw in common_passwords:
        score = 0
        feedback.append("This password appears in a common password list.")
    
    score = max(0, min(score, 100))
    return score, feedback
def strength_label(score: int) -> str:
    if score < 40:
        return "WEAK"
    elif score < 70:
        return "OKAY"
    elif score < 90:
        return "STRONG"
    else:
        return "GODLIKE"

def estimate_entropy_bits(pw:str) -> float:
    has_lower = any(c.islower() for c in pw)
    has_upper = any(c.isupper() for c in pw)
    has_digit = any(c.isdigit() for c in pw)
    has_special = any(not c.isalnum() for c in pw)
    
    alphabet = 0
    if has_lower:
        alphabet += 26
    if has_upper:
        alphabet += 26
    if has_digit:
        alphabet += 10
    if has_special:
        alphabet += 33  # rough count of common printable specials
        
    if alphabet == 0:
        return 0.0
    
    return len(pw) * math.log2(alphabet)

def format_duration(seconds: float) -> str:
    if seconds <1:
        return "< 1 second"
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24
    years = days / 365
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    if minutes <60:
        return f"{minutes:.1f} minutes"
    if hours < 24:
        return f"{hours:.1f} hours"
    if days < 365:
        return f"{days:1f} days"
    return f"{years:.1} years"

def estimate_crack_times(pw:str) -> dict[str, str]:
    bits = estimate_entropy_bits(pw)
    
    #average guesses to find it (uniform random assumtion)
    guesses_avg = 2 ** max(bits - 1, 0)
    
    rates = {
        "online (100 guesses/sec)": 100,
        "offline fast (1e10 guesses/sec)": 10_000_000_000,
        "offline slow (1e4 guesses/sec)": 10_000,
    }
    
    out: dict[str, str] = {}
    for label, rate in rates.items():
        out[label] = format_duration(guesses_avg / rate)
    return out


def main() -> None:
    try:
        common_passwords = load_common_passwords("common_passwords.txt")
    except FileNotFoundError:
        common_passwords = set()
        print("Warning: common_passwords.txt not found; skipping common-password checks.")
    while True:
        pw = input("Enter a password to check (or type 'quit'): ")
        if pw.lower() == "quit":
            print("Goodbye.")
            break
        
        score, feedback = score_password(pw, common_passwords)
        label = strength_label(score)
    
        print(f"\nScore: {score}/100")
        print(f"Strength: {label}")

        if feedback:
            print("\nSuggestions:")
            for item in feedback:
                print(f"- {item}")

        times = estimate_crack_times(pw)
        print("Rough Crack-time estimates (entropy model):")
        for k, v in times.items():
            print(f"- {k}: {v}")

        print()
if __name__ == "__main__":
    main()