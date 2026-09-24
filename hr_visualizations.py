import pandas as pd
import matplotlib.pyplot as plt

FILE = "hr_employee_data_2500.csv"
OUTPUT = "screenshots"


def load_clean_data():
    df = pd.read_csv(FILE)
    df = df.drop_duplicates(subset="Employee_ID", keep="first")

    for col in ["Education", "Manager_ID"]:
        df[col] = df[col].fillna("Unknown")

    for col in ["Tenure_Years", "Performance_Rating", "Job_Satisfaction", "Leave_Days"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(df[col].median())

    df["Salary"] = pd.to_numeric(df["Salary"], errors="coerce")
    df["Experience_Years"] = pd.to_numeric(df["Experience_Years"], errors="coerce")
    df["Monthly_Work_Hours"] = pd.to_numeric(df["Monthly_Work_Hours"], errors="coerce")
    df["Attrition_Flag"] = (df["Attrition"] == "Yes").astype(int)
    return df


def save_chart(filename):
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/{filename}", dpi=180, bbox_inches="tight")
    plt.close()


def main():
    df = load_clean_data()

    # 1. Salary by department
    dept_salary = df.groupby("Department")["Salary"].mean().sort_values()
    dept_salary.plot(kind="barh", figsize=(9, 5), title="Average Salary by Department")
    plt.xlabel("Average Salary (₹)")
    plt.ylabel("Department")
    save_chart("salary_by_department.png")

    # 2. Attrition by department
    dept_attrition = (df.groupby("Department")["Attrition_Flag"].mean() * 100).sort_values()
    dept_attrition.plot(kind="barh", figsize=(9, 5), title="Attrition Rate by Department")
    plt.xlabel("Attrition Rate (%)")
    plt.ylabel("Department")
    save_chart("attrition_by_department.png")

    # 3. Salary vs experience
    plt.figure(figsize=(9, 5))
    plt.scatter(df["Experience_Years"], df["Salary"], alpha=0.35)
    plt.title("Salary vs Experience")
    plt.xlabel("Experience (Years)")
    plt.ylabel("Salary (₹)")
    save_chart("salary_vs_experience.png")

    # 4. Attrition by performance rating
    performance = (df.groupby("Performance_Rating")["Attrition_Flag"].mean() * 100)
    performance.plot(kind="bar", figsize=(8, 5), title="Attrition Rate by Performance Rating")
    plt.xlabel("Performance Rating")
    plt.ylabel("Attrition Rate (%)")
    plt.xticks(rotation=0)
    save_chart("performance_analysis.png")

    # 5. Attrition: overtime vs non-overtime
    overtime = (df.groupby("Overtime")["Attrition_Flag"].mean() * 100)
    overtime.plot(kind="bar", figsize=(7, 5), title="Attrition Rate: Overtime vs Non-Overtime")
    plt.xlabel("Overtime")
    plt.ylabel("Attrition Rate (%)")
    plt.xticks(rotation=0)
    save_chart("attrition_overview.png")

    print("5 HR charts generated successfully in the screenshots folder.")


if __name__ == "__main__":
    main()
