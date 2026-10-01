class CapabilityExporter:

    @staticmethod
    def export(registry):

        capabilities = []

        for capability in registry.list_capabilities():

            capabilities.append(capability)

        return "\n".join(capabilities)