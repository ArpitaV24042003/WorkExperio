# Database Tables Reference

All database tables are defined in `backend/app/models.py`. Here's a complete list:

## 📊 All Database Tables

### 1. **users** (`User` model)
- `id` (String, Primary Key, UUID)
- `name` (String)
- `email` (String, Unique, Indexed)
- `password_hash` (String, Nullable - for OAuth users)
- `created_at` (DateTime)
- `profile_completed` (Boolean)
- `xp_points` (Integer)
- `github_id` (String, Unique, Nullable)
- `avatar_url` (String, Nullable) - **Can store profile pictures**
- `auth_provider` (String)

**Relationships:**
- `resumes` → List of Resume
- `educations` → List of Education
- `experiences` → List of Experience
- `skills` → List of Skill
- `stats` → UserStats (one-to-one)

---

### 2. **resumes** (`Resume` model)
- `id` (String, Primary Key, UUID)
- `user_id` (String, Foreign Key → users.id)
- `filename` (String)
- `uploaded_at` (DateTime)
- `parsed_json` (JSON/JSONB)

---

### 3. **educations** (`Education` model)
- `id` (String, Primary Key, UUID)
- `user_id` (String, Foreign Key → users.id)
- `institution` (String)
- `degree` (String)
- `field` (String)
- `start_date` (String, Nullable)
- `end_date` (String, Nullable)

---

### 4. **experiences** (`Experience` model)
- `id` (String, Primary Key, UUID)
- `user_id` (String, Foreign Key → users.id)
- `company` (String)
- `role` (String)
- `description` (Text, Nullable)
- `start_date` (String, Nullable)
- `end_date` (String, Nullable)

---

### 5. **skills** (`Skill` model)
- `id` (String, Primary Key, UUID)
- `user_id` (String, Foreign Key → users.id)
- `name` (String)
- `level` (String, Nullable)

---

### 6. **projects** (`Project` model)
- `id` (String, Primary Key, UUID)
- `title` (String)
- `description` (Text)
- `owner_id` (String, Foreign Key → users.id)
- `team_id` (String, Foreign Key → teams.id, Nullable)
- `team_type` (String)
- `ai_generated` (Boolean)
- `created_at` (DateTime)

---

### 7. **teams** (`Team` model)
- `id` (String, Primary Key, UUID)
- `project_id` (String, Foreign Key → projects.id)
- `created_at` (DateTime)

**Relationships:**
- `members` → List of TeamMember

---

### 8. **team_members** (`TeamMember` model)
- `id` (String, Primary Key, UUID)
- `team_id` (String, Foreign Key → teams.id)
- `user_id` (String)
- `role` (String, Nullable)
- `task` (Text, Nullable)
- `joined_at` (DateTime)

---

### 9. **project_waitlists** (`ProjectWaitlist` model)
- `id` (String, Primary Key, UUID)
- `project_id` (String, Foreign Key → projects.id)
- `user_id` (String)
- `created_at` (DateTime)

---

### 10. **chat_messages** (`ChatMessage` model)
- `id` (String, Primary Key, UUID)
- `project_id` (String, Foreign Key → projects.id)
- `user_id` (String)
- `content` (Text)
- `created_at` (DateTime)

---

### 11. **ai_conversations** (`AIConversation` model)
- `id` (String, Primary Key, UUID)
- `user_id` (String, Foreign Key → users.id)
- `project_id` (String, Foreign Key → projects.id, Nullable)
- `role` (String) - "user" or "assistant"
- `content` (Text)
- `created_at` (DateTime)

---

### 12. **user_stats** (`UserStats` model)
- `id` (String, Primary Key, UUID)
- `user_id` (String, Foreign Key → users.id, Unique)
- `total_xp` (Integer)
- `tasks_completed` (Integer)
- `files_uploaded` (Integer) - **Metric for evaluation**
- `reviews_received` (JSON/JSONB)
- `ai_score` (Float)
- `updated_at` (DateTime)

---

### 13. **model_predictions** (`ModelPrediction` model)
- `id` (String, Primary Key, UUID)
- `project_id` (String, Foreign Key → projects.id, Nullable)
- `model_name` (String)
- `input_json` (JSON/JSONB)
- `output_json` (JSON/JSONB)
- `score` (Float, Nullable)
- `created_at` (DateTime)

---

### 14. **project_files** (`ProjectFile` model) ⭐ **For Images/Pictures**
- `id` (String, Primary Key, UUID)
- `project_id` (String, Foreign Key → projects.id)
- `user_id` (String, Foreign Key → users.id)
- `filename` (String)
- `file_path` (String) - **Path to stored file**
- `file_size` (Integer) - Size in bytes
- `file_type` (String, Nullable) - "code", "document", "folder", "other"
- `mime_type` (String, Nullable) - **e.g., "image/png", "image/jpeg"**
- `description` (Text, Nullable)
- `uploaded_at` (DateTime)

---

## 🔍 How to Query Database Tables

### In Backend (Python/SQLAlchemy):
```python
from app.models import User, Project, ProjectFile, Team, TeamMember, ChatMessage, UserStats
from app.db import get_db

# Get all users
users = db.query(User).all()

# Get all projects
projects = db.query(Project).all()

# Get all project files (including images)
files = db.query(ProjectFile).all()

# Get images only
images = db.query(ProjectFile).filter(
    ProjectFile.mime_type.like('image/%')
).all()

# Get all team members
team_members = db.query(TeamMember).all()

# Get all chat messages
messages = db.query(ChatMessage).all()
```

### API Endpoints:
- `GET /users/me` - Get current user
- `GET /projects` - Get all projects
- `GET /projects/{project_id}/files` - Get all files for a project
- `GET /files/projects/{project_id}/files/{file_id}/download` - Download file/image
- `GET /ai/analyze-performance/{project_id}` - Get performance report data

---

## 📸 Adding Images to Reports

The `project_files` table stores all uploaded files including images. To add images to reports:

1. **Upload images** via: `POST /files/projects/{project_id}/upload`
2. **Retrieve images** via: `GET /projects/{project_id}/files` (filter by `mime_type` like `image/%`)
3. **Display in frontend** using the `file_path` or download URL

---

## 📝 File Location

All database models are in: **`backend/app/models.py`**



