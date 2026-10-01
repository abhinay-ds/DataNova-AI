class ProjectService:

    _projects = {}

    @classmethod
    def create(cls, project):

        cls._projects[project.id] = project

        return project

    @classmethod
    def get(cls, project_id):

        return cls._projects.get(project_id)

    @classmethod
    def delete(cls, project_id):

        cls._projects.pop(project_id, None)

    @classmethod
    def list(cls):

        return list(cls._projects.values())