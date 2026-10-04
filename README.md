# EduPro Instructor Performance and Course Quality Evaluation

An interactive Streamlit dashboard for analysing instructor effectiveness, course quality consistency, experience, expertise, and enrollment activity.

> **Demo-data notice:** The included datasets are synthetic and exist solely to demonstrate the dashboard. Replace them with authorized source extracts before using this work for operational decisions.

## Features

- Instructor performance leaderboard with rating consistency and enrollment volume
- Experience vs. teacher-rating scatter plot with a regression trend line
- Course-quality heatmap by category and level
- Expertise-wise course-quality comparison
- Filters for expertise, course category, course level, teacher-rating range, and enrollments
- CSV export of the filtered instructor results

## Data model

| File | Key fields |
|---|---|
| `data/teachers.csv` | TeacherID, TeacherName, Age, Gender, Expertise, YearsOfExperience, TeacherRating |
| `data/courses.csv` | CourseID, CourseName, CourseCategory, CourseLevel, CourseRating |
| `data/transactions.csv` | TransactionID, CourseID, TeacherID |

The application aggregates transactions as an enrollment proxy and joins them to courses and teachers.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository and upload this project folder.
2. Open [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
3. Select the repository, branch, and `app.py` as the entry point.
4. Deploy and copy the generated `https://...streamlit.app` URL.

## Research paper

Upload `EduPro_Instructor_and_Course_Quality_Evaluation.pdf` to the repository or a public cloud-drive folder. Use the public HTTPS URL for the research-paper submission field.

## Responsible use

The dashboard supports quality improvement, not automated high-stakes personnel decisions. Always consider sample size, course context, and learner feedback alongside ratings.
