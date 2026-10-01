from app.core.registry.tool_loader import load_tools

registry = load_tools()

print("=" * 50)
print("Registered Tools")
print("=" * 50)

for tool in registry.list_tools():
    print(tool)