import asyncio
import sys
from pathlib import Path

# Ensure project root is on sys.path so 'backend' imports work when running this file directly
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.graph.ResumeGraph import ResumeGraph

async def main():

    resume = """
    Eshwar is a software engineering graduate with experience
    building Python applications and web projects.

    Skills:
    Python, Java, JavaScript, React, FastAPI, SQL, MongoDB, Git.

    Projects:
    Built a document intelligence platform using Python and FastAPI.
    Built a healthcare record management application using React,
    Node.js and MongoDB.

    Education:
    Bachelor's degree in Computer Science.
    """

    job_description = """
    We are looking for a Python Backend Developer.

    Requirements:
    - Python
    - FastAPI
    - REST APIs
    - PostgreSQL
    - Docker
    - AWS
    - Git
    - SQL
    """

    graph = ResumeGraph().build()

    result = await graph.ainvoke({
        "resume_text": resume,
        "job_description": job_description
    })

    print("\n========== PROFILE ANALYSIS ==========")
    print(result["profile_analysis"])

    print("\n========== ATS ANALYSIS ==========")
    print(result["ats_analysis"])

    print("\n========== GENERATED RESUME ==========")
    print(result["generated_resume"])

    print("\n========== REVIEW RESULT ==========")
    print(result["review_result"])


if __name__ == "__main__":
    asyncio.run(main())