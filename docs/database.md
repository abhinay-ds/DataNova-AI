# DataNova AI — Database Architecture & Schema

The application uses **SQLAlchemy ORM** backed by **SQLite** (`backend/datanova.db`) in development and production deployments. Strict foreign key constraints and user ownership isolation are enforced at the database and application levels.

---

## Entity Relationship Model

```mermaid
erDiagram
    USERS ||--o{ PROJECTS : owns
    PROJECTS ||--o{ DATASETS : contains
    PROJECTS ||--o{ CONVERSATIONS : holds
    CONVERSATIONS ||--o{ MESSAGES : records
    PROJECTS ||--o{ ANALYSES : tracks
    PROJECTS ||--o{ CHARTS : references

    USERS {
        int id PK
        string email UK
        string hashed_password
        string role
        datetime created_at
    }

    PROJECTS {
        int id PK
        string name
        string description
        int owner_id FK
        datetime created_at
    }

    DATASETS {
        int id PK
        int project_id FK
        string filename
        string file_type
        int rows
        int columns
        string storage_path
        datetime created_at
    }

    CONVERSATIONS {
        int id PK
        int project_id FK
        string title
        datetime created_at
        datetime updated_at
    }

    MESSAGES {
        int id PK
        int conversation_id FK
        string role
        text content
        json message_data
        datetime created_at
    }

    ANALYSES {
        int id PK
        int project_id FK
        string title
        string analysis_type
        json summary
        datetime created_at
    }

    CHARTS {
        int id PK
        int project_id FK
        string title
        string chart_type
        string image_path
        datetime created_at
    }
```

---

## Key Design Principles
1. **Multi-Tenant Project Isolation:** Every data entity (`Dataset`, `Conversation`, `Message`, `Analysis`, `Chart`) belongs to a `Project`, and every `Project` is strictly mapped to an `owner_id`.
2. **Ephemeral Guest Handling:** Guest users receive a special virtual token (`id=0`, `is_guest=True`) without polluting the database with transient account records.
3. **Structured Card Payloads:** Complex AI tool outputs (profiling tables, correlation matrices, code snippets, evaluation metrics) are stored in `messages.message_data` as JSON, enabling identical UI card reconstruction on browser reload.
