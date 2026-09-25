from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# Configuration
# ============================================================

FILE = Path("hr_employee_data_2500.csv")
OUTPUT = Path("screenshots")


# ============================================================
# Data Loading and Cleaning
# ============================================================

def load_clean_data():
    """
    Load the HR dataset, remove duplicate employees,
    standardize important fields, and handle missing values.
    """

    if not FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {FILE}"
        )

    df = pd.read_csv(FILE)

    # --------------------------------------------------------
    # Remove duplicate employees
    # --------------------------------------------------------

    df = df.drop_duplicates(
        subset="Employee_ID",
        keep="first"
    )

    # --------------------------------------------------------
    # Standardize text columns
    # --------------------------------------------------------

    text_cols = [
        "Department",
        "Education",
        "Manager_ID",
        "Overtime",
        "Attrition",
    ]

    for col in text_cols:
        df[col] = (
            df[col]
            .astype("string")
            .str.strip()
        )

    # --------------------------------------------------------
    # Handle missing categorical values
    # --------------------------------------------------------

    for col in [
        "Education",
        "Manager_ID",
    ]:
        df[col] = df[col].fillna("Unknown")

    # --------------------------------------------------------
    # Convert numeric columns
    # --------------------------------------------------------

    numeric_cols = [
        "Salary",
        "Experience_Years",
        "Tenure_Years",
        "Performance_Rating",
        "Job_Satisfaction",
        "Leave_Days",
        "Monthly_Work_Hours",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Median imputation
    # --------------------------------------------------------

    imputation_cols = [
        "Tenure_Years",
        "Performance_Rating",
        "Job_Satisfaction",
        "Leave_Days",
    ]

    for col in imputation_cols:
        df[col] = df[col].fillna(
            df[col].median()
        )

    # --------------------------------------------------------
    # Attrition flag
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

    return df


# ============================================================
# Chart Utility
# ============================================================

def save_chart(filename):
    """Save the current chart to the screenshots folder."""

    OUTPUT.mkdir(
        parents=True,
        exist_ok=True
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT / filename,
        dpi=180,
        bbox_inches="tight"
    )

    plt.close()


# ============================================================
# Main Visualization Workflow
# ============================================================

def main():
    """Generate all HR analytics visualizations."""

    df = load_clean_data()

    # ========================================================
    # 1. Average Salary by Department
    # ========================================================

    dept_salary = (
        df.groupby("Department")["Salary"]
        .mean()
        .sort_values()
    )

    dept_salary.plot(
        kind="barh",
        figsize=(9, 5),
        title="Average Salary by Department",
    )

    plt.xlabel("Average Salary (₹)")
    plt.ylabel("Department")

    save_chart(
        "salary_by_department.png"
    )

    # ========================================================
    # 2. Attrition Rate by Department
    # ========================================================

    dept_attrition = (
        df.groupby("Department")["Attrition_Flag"]
        .mean()
        .mul(100)
        .sort_values()
    )

    dept_attrition.plot(
        kind="barh",
        figsize=(9, 5),
        title="Attrition Rate by Department",
    )

    plt.xlabel("Attrition Rate (%)")
    plt.ylabel("Department")

    save_chart(
        "attrition_by_department.png"
    )

    # ========================================================
    # 3. Salary vs Experience
    # ========================================================

    plt.figure(figsize=(9, 5))

    plt.scatter(
        df["Experience_Years"],
        df["Salary"],
        alpha=0.35,
    )

    plt.title(
        "Salary vs Experience"
    )

    plt.xlabel(
        "Experience (Years)"
    )

    plt.ylabel(
        "Salary (₹)"
    )

    save_chart(
        "salary_vs_experience.png"
    )

    # ========================================================
    # 4. Attrition Rate by Performance Rating
    # ========================================================

    performance = (
        df.groupby("Performance_Rating")[
            "Attrition_Flag"
        ]
        .mean()
        .mul(100)
    )

    performance.plot(
        kind="bar",
        figsize=(8, 5),
        title="Attrition Rate by Performance Rating",
    )

    plt.xlabel(
        "Performance Rating"
    )

    plt.ylabel(
        "Attrition Rate (%)"
    )

    plt.xticks(
        rotation=0
    )

    save_chart(
        "performance_analysis.png"
    )

    # ========================================================
    # 5. Attrition Rate: Overtime vs Non-Overtime
    # ========================================================

    overtime = (
        df.groupby("Overtime")["Attrition_Flag"]
        .mean()
        .mul(100)
    )

    overtime.plot(
        kind="bar",
        figsize=(7, 5),
        title="Attrition Rate: Overtime vs Non-Overtime",
    )

    plt.xlabel(
        "Overtime"
    )

    plt.ylabel(
        "Attrition Rate (%)"
    )

    plt.xticks(
        rotation=0
    )

    save_chart(
        "attrition_overview.png"
    )

    print(
        "5 HR charts generated successfully "
        "in the screenshots folder."
    )


# ============================================================
# Script Entry Point
# ============================================================

if __name__ == "__main__":
    main()
