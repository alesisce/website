import mysql.connector
import bcrypt
import json
from typing import Optional, List, Dict, Any


class Database:
    def __init__(self, host: str, user: str, password: str, database: str) -> None:
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cur = self.conn.cursor(dictionary=True)

    def setup(self) -> None:
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            project_author_id VARCHAR(100),
            project_track_id VARCHAR(255),
            project_description TEXT,
            project_status ENUM('PENDING','WORKING','ALMOST','DONE'),
            project_priority INT,
            milestones JSON,
            overall_progress INT,
            last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)

        self.conn.commit()

    def create_user(self, name: str, password: str) -> None:
        hashed: bytes = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        self.cur.execute(
            "INSERT INTO users (name, password) VALUES (%s, %s)",
            (name, hashed.decode())
        )
        self.conn.commit()

    def get_user(self, name: str) -> Optional[Dict[str, Any]]:
        self.cur.execute("SELECT * FROM users WHERE name=%s", (name,))
        return self.cur.fetchone()

    def verify_user(self, name: str, password: str) -> bool:
        user: Optional[Dict[str, Any]] = self.get_user(name)
        if not user:
            return False
        return bcrypt.checkpw(password.encode(), user["password"].encode())

    def create_project(
        self,
        name: str,
        author_id: str,
        track_id: str,
        description: str,
        status: str,
        priority: int,
        milestones: Dict[str, bool]
    ) -> int:

        self.cur.execute(
            """INSERT INTO projects
            (name, project_author_id, project_track_id, project_description,
             project_status, project_priority, milestones, overall_progress)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                name,
                author_id,
                track_id,
                description,
                status,
                priority,
                json.dumps(milestones),
                0
            )
        )

        self.conn.commit()
        return self.cur.lastrowid

    def delete_project(self, project_id: int) -> bool:
        self.cur.execute(
            "DELETE FROM projects WHERE id=%s",
            (project_id,)
        )
        self.conn.commit()
        return self.cur.rowcount > 0

    def get_projects(self) -> List[Dict[str, Any]]:
        self.cur.execute(
            "SELECT * FROM projects ORDER BY project_priority ASC"
        )

        projects = self.cur.fetchall()

        for project in projects:
            if project["milestones"]:
                project["milestones"] = json.loads(project["milestones"])

        return projects

    def update_milestones(self, project_id: int, milestones: Dict[str, bool]) -> None:
        self.cur.execute(
            "UPDATE projects SET milestones=%s WHERE id=%s",
            (json.dumps(milestones), project_id)
        )
        self.conn.commit()

    def update_progress(self, project_id: int, progress: int) -> None:
        self.cur.execute(
            "UPDATE projects SET overall_progress=%s WHERE id=%s",
            (progress, project_id)
        )
        self.conn.commit()

    def update_status(self, project_id: int, status: str) -> None:
        self.cur.execute(
            "UPDATE projects SET project_status=%s WHERE id=%s",
            (status, project_id)
        )
        self.conn.commit()

    def update_priority(self, project_id: int, priority: int) -> None:
        self.cur.execute(
            "UPDATE projects SET project_priority=%s WHERE id=%s",
            (priority, project_id)
        )
        self.conn.commit()

    def update_description(self, project_id: int, description: str) -> None:
        self.cur.execute(
            "UPDATE projects SET project_description=%s WHERE id=%s",
            (description, project_id)
        )
        self.conn.commit()

    def get_project_by_track_id(self, track_id: str) -> Optional[Dict[str, Any]]:
        self.cur.execute(
            "SELECT * FROM projects WHERE project_track_id=%s",
            (track_id,)
        )

        project = self.cur.fetchone()

        if not project:
            return None

        if project["milestones"]:
            project["milestones"] = json.loads(project["milestones"])

        return project
    
    def get_project_by_id(self, project_id: int) -> Optional[Dict[str, Any]]:
        self.cur.execute(
            "SELECT * FROM projects WHERE id=%s",
            (project_id,)
        )

        project = self.cur.fetchone()

        if not project:
            return None

        if project["milestones"]:
            project["milestones"] = json.loads(project["milestones"])

        return project