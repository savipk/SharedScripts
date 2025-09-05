import pandas as pd
import matplotlib.pyplot as plt
import re

# Example dataframe
data = {
    "description": [
        "desv"
    ]
}
df = pd.DataFrame(data)

# Simplified regex patterns
patterns = {
    "Who": r"[\[\(\s]*who[\]\)\s:]*",
    "What": r"[\[\(\s]*what[\]\)\s:]*",
    "When": r"[\[\(\s]*when[\]\)\s:]*",
    "Where": r"[\[\(\s]*where[\]\)\s:]*",
    "Why": r"[\[\(\s]*why[\]\)\s:]*"
}

# Count occurrences
counts = {
    w: df["control_description"].str.contains(pat, flags=re.IGNORECASE, regex=True).sum()
    for w, pat in patterns.items()
}

# Convert to DataFrame for plotting
counts_df = pd.DataFrame(list(counts.items()), columns=["W", "Count"])

# Plot
counts_df.plot(kind="bar", x="W", y="Count", legend=False, rot=0)
plt.title("Presence of 5Ws in Control Descriptions")
plt.ylabel("Count")
plt.show()
