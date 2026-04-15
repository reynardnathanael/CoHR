import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('../data/raw/azharali_train_parsed.csv')

# Clean decisions & roles
df['decision_clean'] = df['decision'].astype(str).str.strip().str.lower()
df = df[df['decision_clean'].isin(['select', 'reject'])]
df['role_clean'] = df['role'].astype(str).str.strip().str.lower()
print(df['role_clean'].unique())
# data_ai_roles = [
#     'AI Researcher', 'Machine Learning Engineer', 'Data Engineer', 
#     'Data Analyst', 'Data Architect', 'Data Scientist', 'AI Engineer', 'Database Administrator'
# ]
# data_ai_roles = [
#     'Software Engineer', 'Software Developer', 'Full Stack Developer', 
#     'Mobile App Developer', 'Game Developer', 
#     'AR/VR Developer', 'Blockchain Developer',
# ]

data_ai_roles = [
    'DevOps Engineer', 'Cloud Engineer', 
    'IT Support Specialist', 'Cloud Architect', 'Systems Administrator'
]
safe_data_ai_roles = [role.lower() for role in data_ai_roles]

df_ai = df[df['role_clean'].isin(safe_data_ai_roles)].copy()

# Categorize Education
def categorize_edu(edu_str):
    edu_str = str(edu_str).lower()
    if 'phd' in edu_str or 'ph.d' in edu_str or 'doctorate' in edu_str:
        return "PhD"
    elif 'master' in edu_str or 'msc' in edu_str or 'ms ' in edu_str or 'mba' in edu_str or 'm.s' in edu_str or "master's" in edu_str:
        return "Master's"
    elif 'bachelor' in edu_str or 'bsc' in edu_str or 'bs ' in edu_str or 'ba ' in edu_str or 'b.s' in edu_str or "bachelor's" in edu_str:
        return "Bachelor's"
    else:
        return "Other / Not Specified"

df_ai['edu_level'] = df_ai['education'].apply(categorize_edu)

# Filter out the 'Other / Not Specified' category
df_filtered = df_ai[df_ai['edu_level'] != "Other / Not Specified"]

overall_rate = (len(df_ai[df_ai['decision_clean'] == 'select']) / len(df_ai)) * 100

stats = df_filtered.groupby('edu_level').agg(
    total=('decision_clean', 'count'),
    selected=('decision_clean', lambda x: (x == 'select').sum())
).reset_index()

stats['select_rate'] = (stats['selected'] / stats['total']) * 100

# Plot
plt.figure(figsize=(10, 6))
sns.set_style("whitegrid")
order = ["Bachelor's", "Master's", "PhD"]
ax = sns.barplot(data=stats, x='edu_level', y='select_rate', order=order, palette='Purples_d', width=0.6)

plt.title('Hiring Selection Rate by Education Level (Cloud & IT Roles)\nDoes an advanced degree help here?', fontsize=23, fontweight='bold', pad=10)
plt.ylabel('Selection Rate (%)', fontsize=20)
plt.xlabel('Highest Education Level', fontsize=20, labelpad=15)
plt.xticks(fontsize=20)
plt.yticks(fontsize=14)

plt.axhline(overall_rate, color='#d62728', linestyle='--', linewidth=2, label=f'Cloud & IT Average ({overall_rate:.1f}%)')

for i, edu in enumerate(order):
    row = stats[stats['edu_level'] == edu]
    if not row.empty:
        rate = row['select_rate'].values[0]
        count = row['total'].values[0]
        # Lifted the text higher by adding 1.5 instead of 0.5 to avoid overlapping the line
        plt.text(i, rate + 2.5, f'{rate:.1f}%\n(n={count})', ha='center', fontweight='bold', fontsize=20)

plt.ylim(0, max(stats['select_rate']) + 35)
plt.legend(loc='upper right', bbox_to_anchor=(1.0, 1.01), fontsize=20)
sns.despine(left=True, bottom=True)
plt.tight_layout()
plt.savefig('education_rates_cloud_it_updated.png', dpi=300)