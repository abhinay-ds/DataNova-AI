from app.core.registry.tool_loader import load_tools


def run_test(registry, capability, **kwargs):

    print()
    print("=" * 70)
    print(capability.upper())
    print("=" * 70)

    try:

        tool = registry.get(capability)

        response = tool.execute(**kwargs)

        print("Success :", response.success)
        print("Message :", response.message)
        print()
        print("Output:")
        print(response.data)

    except Exception as e:

        print("ERROR:", str(e))


def main():

    registry = load_tools()

    # =====================================================
    # 1. Generate SQL
    # =====================================================

    run_test(
        registry,
        "generate_sql",
        prompt="""
Generate SQL for a table called employees.

Columns:
- employee_id
- name
- department
- salary

Return a query that calculates the average salary
for each department and sorts the result by average
salary in descending order.
"""
    )

    # =====================================================
    # 2. Explain Code
    # =====================================================

    run_test(
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

    # =====================================================
    # 3. Debug Code
    # =====================================================

    run_test(
        registry,
        "debug_code",
        code="""
numbers = [10, 20, 30]

for i in range(len(numbers) + 1):
    print(numbers[i])
""",
        error="IndexError: list index out of range"
    )

    # =====================================================
    # 4. Optimize Code
    # =====================================================

    run_test(
        registry,
        "optimize_code",
        code="""
result = []

for i in range(len(numbers)):
    result.append(numbers[i] * 2)
"""
    )

    # =====================================================
    # 5. Convert Code
    # =====================================================

    run_test(
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