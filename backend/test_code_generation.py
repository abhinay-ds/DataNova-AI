from app.core.registry.tool_loader import load_tools


def main():

    registry = load_tools()

    print("=" * 60)
    print("PYTHON CODE GENERATION TEST")
    print("=" * 60)

    tool = registry.get(
        "generate_python"
    )

    response = tool.execute(
        prompt=(
            "Generate Python code that reads "
            "employees.csv using pandas and displays "
            "the first 10 rows, dataset shape, "
            "missing values, and basic statistics."
        )
    )

    print()
    print("Success:", response.success)
    print("Message:", response.message)
    print()
    print("Generated Code:")
    print("=" * 60)
    print(response.data)


if __name__ == "__main__":
    main()