from app.core.memory.memory_manager import MemoryManager


class SessionManager:

    _sessions = {}

    @classmethod
    def get_memory(cls, session_id: str) -> MemoryManager:

        if session_id not in cls._sessions:
            cls._sessions[session_id] = MemoryManager()

        return cls._sessions[session_id]

    @classmethod
    def remove_session(cls, session_id: str):

        cls._sessions.pop(session_id, None)

    @classmethod
    def clear(cls):

        cls._sessions.clear()