import mysql.connector
from mysql.connector import pooling
import bcrypt
import json
from typing import Optional, List, Dict, Any


class Database:
    def __init__(self, host: str, user: str, password: str, database: str) -> None:
        self.db_config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "pool_name": f"pool_{database}",
            "pool_size": 10,
            "pool_reset_session": True,
            "autocommit": False
        }
        
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(**self.db_config)
        except pooling.PoolError:
            self.pool = mysql.connector.pooling.MySQLConnectionPool.get_connection(
                f"pool_{database}"
            )._pool

    def _get_connection(self):
        return self.pool.get_connection()

    def _execute(self, query: str, params: tuple = None, fetch: bool = False):
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def setup(self) -> None:
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
            """)

            cursor.execute("""
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

            conn.commit()
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def create_user(self, name: str, password: str) -> None:
        hashed: bytes = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        self._execute(
            "INSERT INTO users (name, password) VALUES (%s, %s)",
            (name, hashed.decode())
        )

    def get_user(self, name: str) -> Optional[Dict[str, Any]]:
        result = self._execute(
            "SELECT * FROM users WHERE name=%s",
            (name,),
            fetch=True
        )
        return result[0] if result else None

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
        cursor = self._execute(
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
        return cursor.lastrowid

    def delete_project(self, project_id: int) -> bool:
        cursor = self._execute(
            "DELETE FROM projects WHERE id=%s",
            (project_id,)
        )
        return cursor.rowcount > 0

    def get_projects(self) -> List[Dict[str, Any]]:
        projects = self._execute(
            "SELECT * FROM projects ORDER BY project_priority ASC",
            fetch=True
        )

        if projects:
            for project in projects:
                if project["milestones"]:
                    project["milestones"] = json.loads(project["milestones"])

        return projects if projects else []

    def update_milestones(self, project_id: int, milestones: Dict[str, bool]) -> None:
        self._execute(
            "UPDATE projects SET milestones=%s WHERE id=%s",
            (json.dumps(milestones), project_id)
        )

    def update_progress(self, project_id: int, progress: int) -> None:
        self._execute(
            "UPDATE projects SET overall_progress=%s WHERE id=%s",
            (progress, project_id)
        )

    def update_status(self, project_id: int, status: str) -> None:
        self._execute(
            "UPDATE projects SET project_status=%s WHERE id=%s",
            (status, project_id)
        )

    def update_priority(self, project_id: int, priority: int) -> None:
        self._execute(
            "UPDATE projects SET project_priority=%s WHERE id=%s",
            (priority, project_id)
        )

    def update_description(self, project_id: int, description: str) -> None:
        self._execute(
            "UPDATE projects SET project_description=%s WHERE id=%s",
            (description, project_id)
        )

    def get_project_by_track_id(self, track_id: str) -> Optional[Dict[str, Any]]:
        result = self._execute(
            "SELECT * FROM projects WHERE project_track_id=%s",
            (track_id,),
            fetch=True
        )
        
        project = result[0] if result else None
        
        if project and project["milestones"]:
            project["milestones"] = json.loads(project["milestones"])

        return project
    
    def get_project_by_id(self, project_id: int) -> Optional[Dict[str, Any]]:
        result = self._execute(
            "SELECT * FROM projects WHERE id=%s",
            (project_id,),
            fetch=True
        )
        
        project = result[0] if result else None
        
        if project and project["milestones"]:
            project["milestones"] = json.loads(project["milestones"])

        return project