"""EduPro - Instructor Performance and Course Quality Evaluation dashboard."""
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="EduPro Quality Analytics", page_icon="🎓", layout="wide")
DATA_DIR = Path(__file__).parent / "data"

@st.cache_data
def load_data():
    teachers = pd.read_csv(DATA_DIR / "teachers.csv")
    courses = pd.read_csv(DATA_DIR / "courses.csv")
    transactions = pd.read_csv(DATA_DIR / "transactions.csv")
    enrollment = transactions.groupby(["TeacherID", "CourseID"], as_index=False).size().rename(columns={"size": "Enrollments"})
    detail = (enrollment.merge(teachers, on="TeacherID", how="left")
                        .merge(courses, on="CourseID", how="left"))
    return teachers, courses, transactions, detail

teachers, courses, transactions, detail = load_data()

st.title("EduPro | Instructor & Course Quality")
st.caption("Interactive teaching-effectiveness analytics. The bundled CSV data is synthetic demo data; replace it with approved EduPro extracts for production use.")

with st.sidebar:
    st.header("Filters")
    expertise = st.multiselect("Instructor expertise", sorted(detail.Expertise.unique()), default=sorted(detail.Expertise.unique()))
    categories = st.multiselect("Course category", sorted(detail.CourseCategory.unique()), default=sorted(detail.CourseCategory.unique()))
    levels = st.multiselect("Course level", sorted(detail.CourseLevel.unique()), default=sorted(detail.CourseLevel.unique()))
    rating_range = st.slider("Teacher rating", 1.0, 5.0, (1.0, 5.0), 0.1)
    min_enrollments = st.number_input("Minimum enrollments per course", min_value=0, value=0, step=5)

filtered = detail[
    detail.Expertise.isin(expertise)
    & detail.CourseCategory.isin(categories)
    & detail.CourseLevel.isin(levels)
    & detail.TeacherRating.between(*rating_range)
    & (detail.Enrollments >= min_enrollments)
].copy()

if filtered.empty:
    st.warning("No records match these filters. Expand a filter and try again.")
    st.stop()

course_n = filtered.CourseID.nunique()
teacher_n = filtered.TeacherID.nunique()
avg_teacher = filtered.drop_duplicates("TeacherID").TeacherRating.mean()
avg_course = filtered.CourseRating.mean()

cols = st.columns(4)
cols[0].metric("Average teacher rating", f"{avg_teacher:.2f} / 5")
cols[1].metric("Average course rating", f"{avg_course:.2f} / 5")
cols[2].metric("Active instructors", f"{teacher_n:,}")
cols[3].metric("Course enrollments", f"{int(filtered.Enrollments.sum()):,}")

st.divider()
left, right = st.columns(2)
with left:
    st.subheader("Experience vs. teaching performance")
    instructor_summary = (filtered.groupby(["TeacherID", "TeacherName", "Expertise", "YearsOfExperience", "TeacherRating"], as_index=False)
                         .agg(AverageCourseRating=("CourseRating", "mean"), Enrollments=("Enrollments", "sum")))
    fig = px.scatter(instructor_summary, x="YearsOfExperience", y="TeacherRating", color="Expertise",
                     size="Enrollments", hover_name="TeacherName", trendline="ols",
                     labels={"TeacherRating":"Teacher rating", "YearsOfExperience":"Years of experience"},
                     color_discrete_sequence=px.colors.qualitative.Safe)
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Course quality by category and level")
    heat = filtered.pivot_table(index="CourseCategory", columns="CourseLevel", values="CourseRating", aggfunc="mean")
    fig = px.imshow(heat, text_auto=".2f", color_continuous_scale="Tealgrn", aspect="auto",
                    labels=dict(color="Average course rating", x="Course level", y="Course category"))
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Expertise-wise performance")
    expertise_summary = (filtered.groupby("Expertise", as_index=False)
                          .agg(AverageCourseRating=("CourseRating", "mean"), Courses=("CourseID", "nunique"))
                          .sort_values("AverageCourseRating", ascending=True))
    fig = px.bar(expertise_summary, x="AverageCourseRating", y="Expertise", orientation="h", text="Courses",
                 range_x=[0, 5], color="AverageCourseRating", color_continuous_scale="Blues")
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Instructor rating distribution")
    fig = px.histogram(instructor_summary, x="TeacherRating", nbins=12, color_discrete_sequence=["#168aad"],
                       labels={"TeacherRating":"Teacher rating"})
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Instructor performance leaderboard")
leaderboard = (instructor_summary.assign(
    RatingConsistency=lambda x: 1 - (filtered.groupby("TeacherID").CourseRating.std().reindex(x.TeacherID).fillna(0).to_numpy() / 4),
    RatingTier=lambda x: pd.cut(x.TeacherRating, bins=[0, 3.5, 4.2, 5], labels=["Low", "Mid", "High"], include_lowest=True)
).sort_values(["TeacherRating", "AverageCourseRating", "Enrollments"], ascending=False))
st.dataframe(leaderboard[["TeacherName", "Expertise", "YearsOfExperience", "TeacherRating", "AverageCourseRating", "RatingConsistency", "Enrollments", "RatingTier"]], hide_index=True, use_container_width=True,
             column_config={"RatingConsistency": st.column_config.NumberColumn(format="%.2f"), "AverageCourseRating": st.column_config.NumberColumn(format="%.2f")})

st.download_button("Download filtered instructor results", leaderboard.to_csv(index=False).encode("utf-8"), "edupro_instructor_results.csv", "text/csv")
st.caption("Interpretation note: ratings are observational indicators. Review volume, category mix, learner feedback, and sample size before taking action.")
