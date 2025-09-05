import pandas as pd
import re

# df is assumed to be provided and has a column "control_description"

# Simplified regex patterns for the 5Ws
patterns = {
    "Who":   r"[\[\(\s]*who[\]\)\s:]*",
    "What":  r"[\[\(\s]*what[\]\)\s:]*",
    "When":  r"[\[\(\s]*when[\]\)\s:]*",
    "Where": r"[\[\(\s]*where[\]\)\s:]*",
    "Why":   r"[\[\(\s]*why[\]\)\s:]*"
}

# Count how many controls contain each W
counts = {
    w: df["control_description"].str.contains(pat, flags=re.IGNORECASE, regex=True).sum()
    for w, pat in patterns.items()
}

# Convert to DataFrame for display or plotting
counts_df = pd.DataFrame(list(counts.items()), columns=["W", "Num_Controls"])

print(counts_df)
