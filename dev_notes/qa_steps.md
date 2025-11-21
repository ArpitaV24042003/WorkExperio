## QA Steps for WorkExperio (tasks, analytics, AI, persistence)

1. **Create user & login**
   - Start backend from `backend`: `uvicorn app.main:app --reload --port 8000`
   - Start frontend from `frontend`: `npm run dev`
   - Open the app, go to `/signup`, create a user.
   - Confirm a JWT is stored in `localStorage.token` and `/users/me` returns the same user after refresh.

2. **Create project with known members**
   - Visit `/profile` and copy your `User ID`.
   - Create a second user in another browser/profile; copy their `User ID`.
   - Login as the first user, go to `/projects/create`, use “Add Known Members” and paste the second user’s `User ID`.
   - Complete project creation and verify the project appears immediately in `/projects` and `/dashboard` without needing to re-login.

3. **Create tasks & assign members**
   - Navigate to `/projects/:id/dashboard`.
   - In the Tasks panel, create several tasks with `estimated_hours`, assign some to yourself and some to the known member, with due dates.
   - Confirm they appear under “All Tasks” and your own tasks appear in the “My Tasks” section.

4. **Start and stop time logs**
   - For a task, click **Start** and wait at least 1 minute, then click **Stop**.
   - Repeat for a couple of tasks.
   - Verify a `timelogs` entry is created (via DB or `/health` + DB tool) with `duration_minutes > 0`.
   - Confirm `/projects/:id/analytics/overview` shows non-zero `total_hours` for your user and updated `avg_completion_minutes`.

5. **Project dashboard analytics & charts**
   - On `/projects/:id/dashboard`, confirm:
     - Completion percentage and overdue count match the tasks you created.
     - “Daily completions” mini chart shows bars after marking tasks as **done**.
     - “Member hours” mini chart shows your total hours.

6. **AI assistant chat**
   - In the AI Assistant panel on the dashboard, send a natural language question (e.g. “What should I do next on this project?”).
   - Confirm a reply appears and both user/assistant messages appear in `/projects/:id/ai/history`.
   - Check DB table `ai_chat_messages` has corresponding rows.

7. **User performance page**
   - Navigate to `/profile/performance`.
   - Confirm:
     - Global KPIs show non-zero values after tasks and timelogs.
     - Per-project cards list your tasks completed, hours, and a simple sparkline.

8. **Code quality analysis endpoint**
   - From a REST client, call `POST /projects/{project_id}/analyze-code` with a code file.
   - Verify JSON response `{ score, details }` is returned and `project_contributions.code_quality_score` updates for your user/project.

9. **File uploads**
   - On `/projects/:id/dashboard`, upload a small text file.
   - Confirm it appears in the “Project Files” list and can be downloaded.
   - Verify the file is saved under `backend/uploads/projects/{project_id}/`.

10. **Persistence across restart**
    - Stop the backend server.
    - Verify `backend/.env` has `DATABASE_URL=sqlite:///./dev.db` or environment defaults to that.
    - Restart backend with `uvicorn app.main:app --reload --port 8000`.
    - Refresh the frontend: login with the same credentials and confirm projects, tasks, timelogs, analytics, and chat history still exist.

11. **Delete project**
    - As the project owner, click **Delete** on `/projects/:id/dashboard` and confirm the dialog.
    - Verify the project disappears from `/projects` and `/dashboard`.
    - Confirm `backend/uploads/projects/{project_id}` directory is removed.

### Useful commands

- Create tables (from `backend` directory):
  ```bash
  python -c "from app.db import create_all_tables; create_all_tables()"
  ```

- Run backend:
  ```bash
  uvicorn app.main:app --reload --port 8000
  ```

- Run frontend:
  ```bash
  npm run dev
  ```


