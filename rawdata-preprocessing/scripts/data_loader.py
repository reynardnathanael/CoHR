"""
Simple Data Loader (Student-Friendly Version)
Loads Hugging Face datasets and saves them as CSV files
"""

import os
from datasets import load_dataset


# =========================
# PATH SETUP
# =========================
# Start from current working directory
CURRENT_DIR = os.getcwd()

# Move up until we find "CoHR" folder
while os.path.basename(CURRENT_DIR) != "CoHR":
    CURRENT_DIR = os.path.dirname(CURRENT_DIR)

PROJECT_ROOT = CURRENT_DIR

# Now this will ALWAYS be inside CoHR/
DATA_RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")

# Create folder
os.makedirs(DATA_RAW_DIR, exist_ok=True)

print("Saving to:", DATA_RAW_DIR)


# =========================
# FUNCTION: SAVE DATASET
# =========================
def save_dataset_to_csv(dataset, dataset_name):
    """
    Convert dataset to CSV and save it

    dataset: HuggingFace dataset
    dataset_name: name for the saved file
    """

    for split in dataset:
        print(f"Processing split: {split}")

        # convert to pandas
        df = dataset[split].to_pandas()

        # create file path
        file_path = os.path.join(DATA_RAW_DIR, f"{dataset_name}_{split}.csv")

        # save
        df.to_csv(file_path, index=False)

        print(f"Saved: {file_path}")


# =========================
# FUNCTION: LOAD + SAVE
# =========================
def load_and_save(dataset_hf_name, dataset_name):
    """
    Load dataset from HuggingFace and save as CSV
    """

    print(f"Loading dataset: {dataset_hf_name}")

    dataset = load_dataset(dataset_hf_name)

    save_dataset_to_csv(dataset, dataset_name)

    print("Done!")


# =========================
# RUN THIS FILE DIRECTLY
# =========================
if __name__ == "__main__":
    load_and_save("AzharAli05/Resume-Screening-Dataset", "azharali")