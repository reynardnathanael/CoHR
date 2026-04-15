import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer

# 1. Load data and clean text columns
df = pd.read_csv('../data/raw/azharali_train_parsed.csv')
df['decision_clean'] = df['decision'].astype(str).str.strip().str.lower()
df = df[df['decision_clean'].isin(['select', 'reject'])]
df['role_clean'] = df['role'].astype(str).str.strip().str.title()

# 2. Filter specifically for Data & AI roles
data_ai_roles = [
    'Ai Researcher', 'Machine Learning Engineer', 'Data Engineer', 
    'Data Analyst', 'Data Architect', 'Data Scientist', 'Ai Engineer'
]
df_ai = df[df['role_clean'].isin(data_ai_roles)].copy()

# Focus purely on the Skills column
df_ai['skills_clean'] = df_ai['skills'].fillna('')

# 3. Custom tokenizer to treat each comma-separated skill as a single phrase
def skill_tokenizer(text):
    if not text: 
        return []
    # Split by comma, remove extra whitespace, and format as Title Case
    return [s.strip().title() for s in text.split(',') if s.strip()]

# 4. Apply TF-IDF with the custom tokenizer
# min_df=0.01 ensures the skill appears in at least 1% of Data & AI resumes 
tfidf = TfidfVectorizer(tokenizer=skill_tokenizer, token_pattern=None, min_df=0.01)
X = tfidf.fit_transform(df_ai['skills_clean'])
feature_names = tfidf.get_feature_names_out()

# 5. Calculate mean TF-IDF score per class
# select_idx = df_ai['decision_clean'] == 'select'
# reject_idx = df_ai['decision_clean'] == 'reject'

select_idx = (df_ai['decision_clean'] == 'select').values
reject_idx = (df_ai['decision_clean'] == 'reject').values

mean_tfidf_select = np.asarray(X[select_idx].mean(axis=0)).flatten()
mean_tfidf_reject = np.asarray(X[reject_idx].mean(axis=0)).flatten()

tfidf_df = pd.DataFrame({
    'Term': feature_names,
    'Select_Score': mean_tfidf_select,
    'Reject_Score': mean_tfidf_reject
})

# Calculate the difference (Select - Reject)
tfidf_df['Difference'] = tfidf_df['Select_Score'] - tfidf_df['Reject_Score']

# 6. Get top 15 Select and top 15 Reject skills
top_select = tfidf_df.sort_values(by='Difference', ascending=False).head(15)
top_reject = tfidf_df.sort_values(by='Difference', ascending=True).head(15)

# Combine and sort for plotting
plot_df = pd.concat([top_select, top_reject]).sort_values(by='Difference', ascending=True)

# ---------------------------------------------------------
# 7. Plotting the Results
# ---------------------------------------------------------
plt.figure(figsize=(14, 11))
sns.set_style("whitegrid")

# Assign colors (Green for positive difference, Red for negative)
colors = ['#d62728' if x < 0 else '#2ca02c' for x in plot_df['Difference']]

plt.barh(plot_df['Term'], plot_df['Difference'], color=colors)

plt.title('TF-IDF Skill Differentiators (DATA & AI Roles)\nWhich Specific Skills Mathematically Separate Selected vs. Rejected?', fontsize=18, fontweight='bold')
plt.xlabel('TF-IDF Weight Difference (Further Right = Stronger Select, Further Left = Stronger Reject)', fontsize=12)
plt.yticks(fontsize=12, fontweight='bold')
plt.axvline(0, color='black', linewidth=1.5)

# Custom legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#2ca02c', label='Highly Predictive of Selection'),
                   Patch(facecolor='#d62728', label='Highly Predictive of Rejection')]
plt.legend(handles=legend_elements, loc='lower right', fontsize=12)

sns.despine(left=True, bottom=True)
plt.tight_layout()
plt.show()