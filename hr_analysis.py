import pandas as pd
import numpy as np

FILE = "hr_employee_data_2500.csv"


def clean_data(df):
    df = df.copy()

    # Remove duplicate employee records, keeping the first occurrence.
    df = df.drop_duplicates(subset="Employee_ID", keep="first")

    # Standardize text columns.
    text_cols = [
        "Gender", "Department", "Job_Role", "City", "Education",
        "Employment_Type", "Overtime", "Manager_ID", "Attrition"
    ]
    for col in text_cols:
        df[col] = df[col].astype("string").str.strip()

    # Missing categorical values.
    for col in ["Education", "Manager_ID"]:
        df[col] = df[col].fillna("Unknown")

    # Numeric missing values: use median to avoid extreme-value distortion.
    numeric_cols = ["Tenure_Years", "Performance_Rating", "Job_Satisfaction", "Leave_Days"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(df[col].median())

    # Convert dates and numeric fields.
    df["Joining_Date"] = pd.to_datetime(df["Joining_Date"], errors="coerce")
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
    df["Experience_Years"] = pd.to_numeric(df["Experience_Years"], errors="coerce")
    df["Salary"] = pd.to_numeric(df["Salary"], errors="coerce")
    df["Monthly_Work_Hours"] = pd.to_numeric(df["Monthly_Work_Hours"], errors="coerce")
    df["Absent_Days"] = pd.to_numeric(df["Absent_Days"], errors="coerce")

    # Derived business fields.
    df["Attrition_Flag"] = np.where(df["Attrition"].eq("Yes"), 1, 0)
    df["Age_Group"] = pd.cut(
        df["Age"], bins=[0, 25, 35, 45, 55, 100],
        labels=["18-25", "26-35", "36-45", "46-55", "56+"]
    )
    df["Experience_Group"] = pd.cut(
        df["Experience_Years"], bins=[-1, 2, 5, 10, 20, 100],
        labels=["0-2", "3-5", "6-10", "11-20", "21+"]
    )
    df["Tenure_Group"] = pd.cut(
        df["Tenure_Years"], bins=[-1, 2, 5, 10, 20, 100],
        labels=["0-2", "3-5", "6-10", "11-20", "21+"]
    )

    return df


def pct(value):
    return f"{value:.2f}%"


def main():
    raw = pd.read_csv(FILE)
    df = clean_data(raw)

    print("=" * 70)
    print("HR ANALYTICS - DATA QUALITY")
    print("=" * 70)
    print(f"Raw rows: {len(raw):,}")
    print(f"Clean rows: {len(df):,}")
    print(f"Raw duplicate Employee IDs: {raw['Employee_ID'].duplicated().sum():,}")
    print(f"Remaining duplicate Employee IDs: {df['Employee_ID'].duplicated().sum():,}")
    print(f"Remaining missing cells: {int(df.isna().sum().sum()):,}")

    print("\n" + "=" * 70)
    print("OVERALL HR KPIs")
    print("=" * 70)
    total_employees = len(df)
    avg_salary = df["Salary"].mean()
    median_salary = df["Salary"].median()
    total_salary = df["Salary"].sum()
    attrition_rate = df["Attrition_Flag"].mean() * 100
    print(f"Total Employees: {total_employees:,}")
    print(f"Average Age: {df['Age'].mean():.2f}")
    print(f"Average Salary: ₹{avg_salary:,.2f}")
    print(f"Median Salary: ₹{median_salary:,.2f}")
    print(f"Total Salary Expense: ₹{total_salary:,.0f}")
    print(f"Average Experience: {df['Experience_Years'].mean():.2f} years")
    print(f"Average Tenure: {df['Tenure_Years'].mean():.2f} years")
    print(f"Average Job Satisfaction: {df['Job_Satisfaction'].mean():.2f}/5")
    print(f"Average Monthly Work Hours: {df['Monthly_Work_Hours'].mean():.2f}")
    print(f"Attrition Rate: {pct(attrition_rate)}")

    print("\n" + "=" * 70)
    print("DEPARTMENT ANALYSIS")
    print("=" * 70)
    dept = df.groupby("Department").agg(
        Employees=("Employee_ID", "nunique"),
        Avg_Salary=("Salary", "mean"),
        Salary_Expense=("Salary", "sum"),
        Avg_Performance=("Performance_Rating", "mean"),
        Avg_Satisfaction=("Job_Satisfaction", "mean"),
        Attrition_Rate=("Attrition_Flag", "mean"),
    ).sort_values("Employees", ascending=False)
    dept["Attrition_Rate"] *= 100
    print(dept.round(2))

    print("\n" + "=" * 70)
    print("JOB ROLE ANALYSIS - TOP 10 BY EMPLOYEE COUNT")
    print("=" * 70)
    role = df.groupby("Job_Role").agg(
        Employees=("Employee_ID", "nunique"),
        Avg_Salary=("Salary", "mean"),
        Avg_Performance=("Performance_Rating", "mean"),
        Attrition_Rate=("Attrition_Flag", "mean"),
    ).sort_values("Employees", ascending=False).head(10)
    role["Attrition_Rate"] *= 100
    print(role.round(2))

    print("\n" + "=" * 70)
    print("GENDER ANALYSIS")
    print("=" * 70)
    gender = df.groupby("Gender").agg(
        Employees=("Employee_ID", "nunique"),
        Avg_Salary=("Salary", "mean"),
        Attrition_Rate=("Attrition_Flag", "mean"),
    )
    gender["Attrition_Rate"] *= 100
    print(gender.round(2))

    print("\n" + "=" * 70)
    print("EXPERIENCE ANALYSIS")
    print("=" * 70)
    experience = df.groupby("Experience_Group", observed=False).agg(
        Employees=("Employee_ID", "nunique"),
        Avg_Salary=("Salary", "mean"),
        Attrition_Rate=("Attrition_Flag", "mean"),
    )
    experience["Attrition_Rate"] *= 100
    print(experience.round(2))

    print("\n" + "=" * 70)
    print("PERFORMANCE ANALYSIS")
    print("=" * 70)
    performance = df.groupby("Performance_Rating").agg(
        Employees=("Employee_ID", "nunique"),
        Avg_Salary=("Salary", "mean"),
        Avg_Satisfaction=("Job_Satisfaction", "mean"),
        Attrition_Rate=("Attrition_Flag", "mean"),
    )
    performance["Attrition_Rate"] *= 100
    print(performance.round(2))

    print("\n" + "=" * 70)
    print("OVERTIME & WORKLOAD ANALYSIS")
    print("=" * 70)
    overtime = df.groupby("Overtime").agg(
        Employees=("Employee_ID", "nunique"),
        Avg_Work_Hours=("Monthly_Work_Hours", "mean"),
        Avg_Absent_Days=("Absent_Days", "mean"),
        Attrition_Rate=("Attrition_Flag", "mean"),
    )
    overtime["Attrition_Rate"] *= 100
    print(overtime.round(2))

    print("\n" + "=" * 70)
    print("TENURE ANALYSIS")
    print("=" * 70)
    tenure = df.groupby("Tenure_Group", observed=False).agg(
        Employees=("Employee_ID", "nunique"),
        Avg_Salary=("Salary", "mean"),
        Attrition_Rate=("Attrition_Flag", "mean"),
    )
    tenure["Attrition_Rate"] *= 100
    print(tenure.round(2))

    print("\n" + "=" * 70)
    print("TOP / BOTTOM BUSINESS SIGNALS")
    print("=" * 70)
    print(f"Highest average salary department: {dept['Avg_Salary'].idxmax()}")
    print(f"Largest department: {dept['Employees'].idxmax()}")
    print(f"Highest department attrition: {dept['Attrition_Rate'].idxmax()} ({dept['Attrition_Rate'].max():.2f}%)")
    print(f"Highest average salary job role: {df.groupby('Job_Role')['Salary'].mean().idxmax()}")
    print(f"Highest salary: ₹{df['Salary'].max():,.0f}")
    print(f"Lowest salary: ₹{df['Salary'].min():,.0f}")
    print(f"Highest paid employee: {df.loc[df['Salary'].idxmax(), 'Employee_ID']}")

    # Export cleaned data and summary tables for portfolio reuse.
    df.to_csv("hr_employee_data_cleaned.csv", index=False)
    dept.to_csv("department_summary.csv")
    role.to_csv("job_role_summary.csv")
    gender.to_csv("gender_summary.csv")
    experience.to_csv("experience_summary.csv")
    performance.to_csv("performance_summary.csv")
    overtime.to_csv("overtime_summary.csv")
    tenure.to_csv("tenure_summary.csv")

    print("\nCleaned dataset and summary CSV files exported successfully.")


if __name__ == "__main__":
    main()
