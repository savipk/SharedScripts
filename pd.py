import pandas as pd
import re

# df is assumed to be provided and has a column "control_description"

# Updated regex patterns
patterns = {
    "Who":   r"(?:\[\s*who\s*\]|\(\s*who\s*\)|who:)",
    "What":  r"(?:\[\s*what\s*\]|\(\s*what\s*\)|what:)",
    "When":  r"(?:\[\s*when\s*\]|\(\s*when\s*\)|when:)",
    "Where": r"(?:\[\s*where\s*\]|\(\s*where\s*\)|where:)",
    "Why":   r"(?:\[\s*why\s*\]|\(\s*why\s*\)|why:)"
}

# Count how many controls contain each W
counts = {
    w: df["control_description"].str.contains(pat, flags=re.IGNORECASE, regex=True).sum()
    for w, pat in patterns.items()
}

# Convert to DataFrame for display or plotting
counts_df = pd.DataFrame(list(counts.items()), columns=["W", "Num_Controls"])

print(counts_df)
