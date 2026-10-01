class WorkspaceService:

    _workspaces = {}

    @classmethod
    def get_workspace(cls, project_id):

        return cls._workspaces.get(project_id)

    @classmethod
    def save_workspace(
        cls,
        project_id,
        workspace
    ):

        cls._workspaces[project_id] = workspace