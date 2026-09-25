from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# Configuration
# ============================================================

FILE = Path("hr_employee_data_2500.csv")

CLEANED_FILE = Path("hr_employee_data_cleaned.csv")

SUMMARY_FILES = {
    "department": Path("department_summary.csv"),
    "job_role": Path("job_role_summary.csv"),
    "gender": Path("gender_summary.csv"),
    "experience": Path("experience_summary.csv"),
    "performance": Path("performance_summary.csv"),
    "overtime": Path("overtime_summary.csv"),
    "tenure": Path("tenure_summary.csv"),
}


REQUIRED_COLUMNS = [
    "Employee_ID",
    "Age",
    "Gender",
    "Department",
    "Job_Role",
    "City",
    "Education",
    "Employment_Type",
    "Experience_Years",
    "Salary",
    "Joining_Date",
    "Tenure_Years",
    "Performance_Rating",
    "Job_Satisfaction",
    "Overtime",
    "Monthly_Work_Hours",
    "Leave_Days",
    "Absent_Days",
    "Manager_ID",
    "Attrition",
]


# ============================================================
# Utility Functions
# ============================================================

def pct(value):
    """Format a numeric value as a percentage."""
    return f"{value:.2f}%"


def validate_input(df):
    """Validate that the dataset contains all required columns."""
    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


# ============================================================
# Data Cleaning
# ============================================================

def clean_data(df):
    """
    Clean the HR dataset and create derived business fields.

    Cleaning steps:
    - Remove duplicate employees
    - Standardize text columns
    - Handle missing categorical values
    - Handle missing numeric values using median imputation
    - Convert dates and numeric columns
    - Create business-friendly analysis fields
    """

    df = df.copy()

    # --------------------------------------------------------
    # Remove duplicate employee records
    # --------------------------------------------------------

    df = df.drop_duplicates(
        subset="Employee_ID",
        keep="first"
    )

    # --------------------------------------------------------
    # Standardize text columns
    # --------------------------------------------------------

    text_cols = [
        "Gender",
        "Department",
        "Job_Role",
        "City",
        "Education",
        "Employment_Type",
        "Overtime",
        "Manager_ID",
        "Attrition",
    ]

    for col in text_cols:
        df[col] = df[col].astype("string").str.strip()

    # --------------------------------------------------------
    # Handle missing categorical values
    # --------------------------------------------------------

    categorical_cols = [
        "Education",
        "Manager_ID",
    ]

    for col in categorical_cols:
        df[col] = df[col].fillna("Unknown")

    # --------------------------------------------------------
    # Convert numeric columns
    # --------------------------------------------------------

    numeric_cols = [
        "Age",
        "Experience_Years",
        "Salary",
        "Tenure_Years",
        "Performance_Rating",
        "Job_Satisfaction",
        "Monthly_Work_Hours",
        "Leave_Days",
        "Absent_Days",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Median imputation for selected numeric columns
    # --------------------------------------------------------

    imputation_cols = [
        "Tenure_Years",
        "Performance_Rating",
        "Job_Satisfaction",
        "Leave_Days",
    ]

    for col in imputation_cols:
        df[col] = df[col].fillna(df[col].median())

    # --------------------------------------------------------
    # Convert date column
    # --------------------------------------------------------

    df["Joining_Date"] = pd.to_datetime(
        df["Joining_Date"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Create Attrition Flag
    # --------------------------------------------------------
    # Yes = 1
    # No = 0
    # Missing remains missing

    df["Attrition_Flag"] = (
        df["Attrition"]
        .map({
            "Yes": 1,
            "No": 0,
        })
        .astype("Int64")
    )

    # --------------------------------------------------------
    # Create Age Groups
    # --------------------------------------------------------

    df["Age_Group"] = pd.cut(
        df["Age"],
        bins=[0, 25, 35, 45, 55, 100],
        labels=[
            "18-25",
            "26-35",
            "36-45",
            "46-55",
            "56+",
        ],
    )

    # --------------------------------------------------------
    # Create Experience Groups
    # --------------------------------------------------------

    df["Experience_Group"] = pd.cut(
        df["Experience_Years"],
        bins=[-1, 2, 5, 10, 20, 100],
        labels=[
            "0-2",
            "3-5",
            "6-10",
            "11-20",
            "21+",
        ],
    )

    # --------------------------------------------------------
    # Create Tenure Groups
    # --------------------------------------------------------

    df["Tenure_Group"] = pd.cut(
        df["Tenure_Years"],
        bins=[-1, 2, 5, 10, 20, 100],
        labels=[
            "0-2",
            "3-5",
            "6-10",
            "11-20",
            "21+",
        ],
    )

    return df


# ============================================================
# Analysis Functions
# ============================================================

def department_analysis(df):
    """Analyze employee distribution and HR metrics by department."""

    result = df.groupby("Department").agg(
        Employees=("Employee_ID", "nunique"),
        Avg_Salary=("Salary", "mean"),
        Salary_Expense=("Salary", "sum"),
        Avg_Performance=("Performance_Rating", "mean"),
        Avg_Satisfaction=("Job_Satisfaction", "mean"),
        Attrition_Rate=("Attrition_Flag", "mean"),
    )

    result["Attrition_Rate"] *= 100

    return result.sort_values(
        "Employees",
        ascending=False
    )


def job_role_analysis(df):
    """Analyze the top job roles by employee count."""

    result = df.groupby("Job_Role").agg(
        Employees=("Employee_ID", "nunique"),
        Avg_Salary=("Salary", "mean"),
        Avg_Performance=("Performance_Rating", "mean"),
        Attrition_Rate=("Attrition_Flag", "mean"),
    )

    result["Attrition_Rate"] *= 100

    return result.sort_values(
        "Employees",
        ascending=False
    ).head(10)


def gender_analysis(df):
    """Analyze salary and attrition by gender."""

    result = df.groupby("Gender").agg(
        Employees=("Employee_ID", "nunique"),
        Avg_Salary=("Salary", "mean"),
        Attrition_Rate=("Attrition_Flag", "mean"),
    )

    result["Attrition_Rate"] *= 100

    return result


def experience_analysis(df):
    """Analyze salary and attrition across experience groups."""

    result = df.groupby(
        "Experience_Group",
        observed=False
    ).agg(
        Employees=("Employee_ID", "nunique"),
        Avg_Salary=("Salary", "mean"),
        Attrition_Rate=("Attrition_Flag", "mean"),
    )

    result["Attrition_Rate"] *= 100

    return result


def performance_analysis(df):
    """Analyze salary, satisfaction and attrition by performance rating."""

    result = df.groupby("Performance_Rating").agg(
        Employees=("Employee_ID", "nunique"),
        Avg_Salary=("Salary", "mean"),
        Avg_Satisfaction=("Job_Satisfaction", "mean"),
        Attrition_Rate=("Attrition_Flag", "mean"),
    )

    result["Attrition_Rate"] *= 100

    return result


def overtime_analysis(df):
    """Analyze workload and attrition by overtime status."""

    result = df.groupby("Overtime").agg(
        Employees=("Employee_ID", "nunique"),
        Avg_Work_Hours=("Monthly_Work_Hours", "mean"),
        Avg_Absent_Days=("Absent_Days", "mean"),
        Attrition_Rate=("Attrition_Flag", "mean"),
    )

    result["Attrition_Rate"] *= 100

    return result


def tenure_analysis(df):
    """Analyze salary and attrition across tenure groups."""

    result = df.groupby(
        "Tenure_Group",
        observed=False
    ).agg(
        Employees=("Employee_ID", "nunique"),
        Avg_Salary=("Salary", "mean"),
        Attrition_Rate=("Attrition_Flag", "mean"),
    )

    result["Attrition_Rate"] *= 100

    return result


# ============================================================
# Overall KPI Analysis
# ============================================================

def print_overall_kpis(df):
    """Print overall HR KPIs."""

    total_employees = df["Employee_ID"].nunique()
    avg_age = df["Age"].mean()
    avg_salary = df["Salary"].mean()
    median_salary = df["Salary"].median()
    total_salary = df["Salary"].sum()
    avg_experience = df["Experience_Years"].mean()
    avg_tenure = df["Tenure_Years"].mean()
    avg_satisfaction = df["Job_Satisfaction"].mean()
    avg_work_hours = df["Monthly_Work_Hours"].mean()
    attrition_rate = df["Attrition_Flag"].mean() * 100

    print(f"Total Employees: {total_employees:,}")
    print(f"Average Age: {avg_age:.2f}")
    print(f"Average Salary: ₹{avg_salary:,.2f}")
    print(f"Median Salary: ₹{median_salary:,.2f}")
    print(f"Total Salary Expense: ₹{total_salary:,.0f}")
    print(f"Average Experience: {avg_experience:.2f} years")
    print(f"Average Tenure: {avg_tenure:.2f} years")
    print(f"Average Job Satisfaction: {avg_satisfaction:.2f}/5")
    print(f"Average Monthly Work Hours: {avg_work_hours:.2f}")
    print(f"Attrition Rate: {pct(attrition_rate)}")


# ============================================================
# Business Signals
# ============================================================

def print_business_signals(df, dept):
    """Print key business signals from the HR dataset."""

    highest_salary_department = dept["Avg_Salary"].idxmax()
    largest_department = dept["Employees"].idxmax()
    highest_attrition_department = dept["Attrition_Rate"].idxmax()

    highest_salary_role = (
        df.groupby("Job_Role")["Salary"]
        .mean()
        .idxmax()
    )

    highest_salary = df["Salary"].max()
    lowest_salary = df["Salary"].min()

    highest_paid_employee = df.loc[
        df["Salary"].idxmax(),
        "Employee_ID"
    ]

    print(
        f"Highest average salary department: "
        f"{highest_salary_department}"
    )

    print(
        f"Largest department: "
        f"{largest_department}"
    )

    print(
        f"Highest department attrition: "
        f"{highest_attrition_department} "
        f"({dept['Attrition_Rate'].max():.2f}%)"
    )

    print(
        f"Highest average salary job role: "
        f"{highest_salary_role}"
    )

    print(f"Highest salary: ₹{highest_salary:,.0f}")
    print(f"Lowest salary: ₹{lowest_salary:,.0f}")

    print(
        f"Highest paid employee: "
        f"{highest_paid_employee}"
    )


# ============================================================
# Export Results
# ============================================================

def export_results(
    df,
    department,
    job_role,
    gender,
    experience,
    performance,
    overtime,
    tenure,
):
    """Export cleaned dataset and summary tables."""

    df.to_csv(
        CLEANED_FILE,
        index=False
    )

    summaries = {
        SUMMARY_FILES["department"]: department,
        SUMMARY_FILES["job_role"]: job_role,
        SUMMARY_FILES["gender"]: gender,
        SUMMARY_FILES["experience"]: experience,
        SUMMARY_FILES["performance"]: performance,
        SUMMARY_FILES["overtime"]: overtime,
        SUMMARY_FILES["tenure"]: tenure,
    }

    for file, data in summaries.items():
        data.to_csv(
            file,
            index=True
        )

    print("\nCleaned dataset and summary CSV files exported successfully.")


# ============================================================
# Main Program
# ============================================================

def main():
    """Run the complete HR analytics workflow."""

    if not FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {FILE}"
        )

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    raw = pd.read_csv(FILE)

    validate_input(raw)

    # --------------------------------------------------------
    # Clean data
    # --------------------------------------------------------

    df = clean_data(raw)

    # --------------------------------------------------------
    # Data Quality Report
    # --------------------------------------------------------

    print("=" * 70)
    print("HR ANALYTICS - DATA QUALITY")
    print("=" * 70)

    print(f"Raw rows: {len(raw):,}")
    print(f"Clean rows: {len(df):,}")

    print(
        f"Raw duplicate Employee IDs: "
        f"{raw['Employee_ID'].duplicated().sum():,}"
    )

    print(
        f"Remaining duplicate Employee IDs: "
        f"{df['Employee_ID'].duplicated().sum():,}"
    )

    print(
        f"Remaining missing cells: "
        f"{int(df.isna().sum().sum()):,}"
    )

    # --------------------------------------------------------
    # Overall KPIs
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("OVERALL HR KPIs")
    print("=" * 70)

    print_overall_kpis(df)

    # --------------------------------------------------------
    # Department Analysis
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("DEPARTMENT ANALYSIS")
    print("=" * 70)

    dept = department_analysis(df)
    print(dept.round(2))

    # --------------------------------------------------------
    # Job Role Analysis
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("JOB ROLE ANALYSIS - TOP 10 BY EMPLOYEE COUNT")
    print("=" * 70)

    role = job_role_analysis(df)
    print(role.round(2))

    # --------------------------------------------------------
    # Gender Analysis
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("GENDER ANALYSIS")
    print("=" * 70)

    gender = gender_analysis(df)
    print(gender.round(2))

    # --------------------------------------------------------
    # Experience Analysis
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("EXPERIENCE ANALYSIS")
    print("=" * 70)

    experience = experience_analysis(df)
    print(experience.round(2))

    # --------------------------------------------------------
    # Performance Analysis
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("PERFORMANCE ANALYSIS")
    print("=" * 70)

    performance = performance_analysis(df)
    print(performance.round(2))

    # --------------------------------------------------------
    # Overtime Analysis
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("OVERTIME & WORKLOAD ANALYSIS")
    print("=" * 70)

    overtime = overtime_analysis(df)
    print(overtime.round(2))

    # --------------------------------------------------------
    # Tenure Analysis
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("TENURE ANALYSIS")
    print("=" * 70)

    tenure = tenure_analysis(df)
    print(tenure.round(2))

    # --------------------------------------------------------
    # Business Signals
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("TOP / BOTTOM BUSINESS SIGNALS")
    print("=" * 70)

    print_business_signals(df, dept)

    # --------------------------------------------------------
    # Export Results
    # --------------------------------------------------------

    export_results(
        df=df,
        department=dept,
        job_role=role,
        gender=gender,
        experience=experience,
        performance=performance,
        overtime=overtime,
        tenure=tenure,
    )


# ============================================================
# Script Entry Point
# ============================================================

if __name__ == "__main__":
    main()
