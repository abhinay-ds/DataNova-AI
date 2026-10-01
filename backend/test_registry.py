from app.core.registry.capability_loader import load_capabilities

registry = load_capabilities()

print("=" * 50)
print("Registered Capabilities")
print("=" * 50)

for capability in registry.list_capabilities():
    print(capability)