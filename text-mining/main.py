from load import load_pdf_files
from parser import parse_pdf_with_docling
from extractor import parse_resume_info
from similarity import calculate_similarity


DATA_DIR = "/home/bella/Code/CoHR/data/pdf"


job_description = """
Looking for a database engineer with experience in SQL, Oracle, MySQL,
MongoDB, database design, data warehousing, performance tuning,
and database administration.
"""


def main():
    pdf_files = load_pdf_files(DATA_DIR)

    resumes = []

    for pdf_file in pdf_files:
        print(f"Parsing: {pdf_file.name}")

        raw_text = parse_pdf_with_docling(pdf_file)

        resume_info = parse_resume_info(
            file_name=pdf_file.name,
            raw_text=raw_text
        )

        resumes.append(resume_info)

    ranked_resumes = calculate_similarity(job_description, resumes)

    print("\n===== TOP MATCHING CANDIDATES =====")

    for idx, resume in enumerate(ranked_resumes, start=1):
        print(f"\nRank {idx}")
        print("File:", resume["file_name"])
        print("Similarity Score:", resume["similarity_score"], "%")
        print("Skills:", resume["extracted_skills"])
        print("Education:", resume["education"][:300])
        print("Experience Preview:", resume["experience"][:500])


if __name__ == "__main__":
    main()