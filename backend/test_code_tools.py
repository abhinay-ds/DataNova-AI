from app.core.registry.tool_loader import load_tools


def test_tool(registry, name, **kwargs):

    print()
    print("=" * 60)
    print(name.upper())
    print("=" * 60)

    try:

        tool = registry.get(name)

        response = tool.execute(
            **kwargs
        )

        print(
            "Success:",
            response.success
        )

        print(
            "Message:",
            response.message
        )

        print(
            "Output:",
            response.data
        )

    except Exception as e:

        print(
            "ERROR:",
            str(e)
        )


def main():

    registry = load_tools()

    # -----------------------------------------
    # Generate SQL
    # -----------------------------------------

    test_tool(
        registry,
        "generate_sql",
        prompt=(
            "Generate SQL to calculate the average "
            "salary for each department from a table "
            "called employees with columns "
            "department and salary."
        )
    )

    # -----------------------------------------
    # Explain Code
    # -----------------------------------------

    test_tool(
        registry,
        "explain_code",
        code="""
numbers = [1, 2, 3, 4, 5]

squares = [
    number ** 2
    for number in numbers
]

print(squares)
"""
    )

    # -----------------------------------------
    # Debug Code
    # -----------------------------------------

    test_tool(
        registry,
        "debug_code",
        code="""
numbers = [1, 2, 3]

for i in range(len(numbers) + 1):
    print(numbers[i])
""",
        error=(
            "IndexError: list index out of range"
        )
    )

    # -----------------------------------------
    # Optimize Code
    # -----------------------------------------

    test_tool(
        registry,
        "optimize_code",
        code="""
result = []

for i in range(len(numbers)):
    result.append(numbers[i] * 2)
"""
    )

    # -----------------------------------------
    # Convert Code
    # -----------------------------------------

    test_tool(
        registry,
        "convert_code",
        code="""
numbers = [1, 2, 3, 4, 5]

total = sum(numbers)

print(total)
""",
        target_language="javascript"
    )


if __name__ == "__main__":
    main()