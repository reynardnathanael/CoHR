from load import load_pdf_files
from parser import parse_pdf_with_docling
from extractor import extract_resume_info
from similarity import calculate_similarity


DATA_DIR = "data/test"


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

        print("\n===== RAW TEXT DEBUG =====")
        print(raw_text[:1000])
        print("===== END RAW TEXT DEBUG =====\n")

        resume_info = extract_resume_info(raw_text)
        resume_info["file_name"] = pdf_file.name
        resume_info["full_text"] = raw_text

        resumes.append(resume_info)

    ranked_resumes = calculate_similarity(job_description, resumes)

    print("\n===== TOP MATCHING CANDIDATES =====")

    for idx, resume in enumerate(ranked_resumes, start=1):
        print(f"\nRank {idx}")
        print("File:", resume["file_name"])
        print("Final Score:", resume["similarity_score"], "%")
        print("Embedding Score:", resume["embedding_score"], "%")
        print("Skill Match Score:", resume["skill_score"], "%")
        print("Matched Skills:", resume["matched_skills"])
        print("Email:", resume.get("email", ""))
        print("Phone Number:", resume.get("phone_number", ""))
        print("Location:", resume.get("location", ""))
        print("Skills:", resume["extracted_skills"])
        print("Education:", resume.get("education", "")[:300])
        print("Experience Preview:", resume.get("experience", "")[:500])

        if not resume.get("email"):
            print("WARNING: Email was not extracted. Check whether the email appears in RAW TEXT DEBUG above.")

        if not resume.get("phone_number"):
            print("WARNING: Phone number was not extracted. Check whether the phone appears in RAW TEXT DEBUG above.")

        if not resume.get("experience"):
            print("WARNING: Experience section was not extracted. Check the exact heading name in RAW TEXT DEBUG above.")


if __name__ == "__main__":
    main()