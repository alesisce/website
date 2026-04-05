import mysql.connector
import bcrypt

class Database:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cur = self.conn.cursor(dictionary=True)

    def setup(self):
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
            project_author_id INT,
            project_track_id VARCHAR(255),
            project_description TEXT,
            project_status ENUM('PENDING','WORKING','ALMOST','DONE'),
            project_priority INT,
            FOREIGN KEY (project_author_id) REFERENCES users(id)
        )
        """)

        self.conn.commit()

    def create_user(self, name, password):
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        self.cur.execute(
            "INSERT INTO users (name, password) VALUES (%s, %s)",
            (name, hashed.decode())
        )
        self.conn.commit()

    def get_user(self, name):
        self.cur.execute("SELECT * FROM users WHERE name=%s", (name,))
        return self.cur.fetchone()

    def verify_user(self, name, password):
        user = self.get_user(name)
        if not user:
            return False
        return bcrypt.checkpw(password.encode(), user["password"].encode())

    def create_project(self, name, author_id, track_id, description, status, priority):
        self.cur.execute(
            """INSERT INTO projects
            (name, project_author_id, project_track_id, project_description, project_status, project_priority)
            VALUES (%s,%s,%s,%s,%s,%s)""",
            (name, author_id, track_id, description, status, priority)
        )
        self.conn.commit()

    def delete_project(self, project_id: int):
        self.cur.execute(
            "DELETE FROM projects WHERE id=%s",
            (project_id,)
        )
        self.conn.commit()

    def get_projects(self):
        self.cur.execute(
            "SELECT * FROM projects ORDER BY project_priority ASC"
        )
        return self.cur.fetchall()