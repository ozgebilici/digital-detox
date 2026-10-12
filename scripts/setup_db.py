import os
import sys
import psycopg
from psycopg import sql

def parse_env(file_path):
    env_vars = {}
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    env_vars[key.strip()] = val.strip()
    return env_vars

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.abspath(os.path.join(script_dir, "..", "backend"))
    env_path = os.path.join(backend_dir, ".env")
    
    env_vars = parse_env(env_path)
    db_url = env_vars.get("DATABASE_URL")
    
    # If not found, ask or use default postgres url to connect first
    # Default connection string to postgres (not digital_detox)
    conn_str = "postgresql://postgres:postgres@localhost:5432/postgres"
    
    target_db = "digital_detox"
    db_user = "postgres"
    
    if db_url:
        # Convert DATABASE_URL to a connection string for the maintenance database 'postgres'
        # e.g., postgresql://postgres:password@localhost:5432/digital_detox -> postgresql://postgres:password@localhost:5432/postgres
        # Handle custom schemas if present
        if "postgresql://" in db_url:
            clean_url = db_url.split("?")[0] # remove query params
            parts = clean_url.rsplit("/", 1)
            if len(parts) == 2:
                conn_str = parts[0] + "/postgres"
                target_db = parts[1]
                
                # Extract user
                user_part = parts[0].replace("postgresql://", "")
                if "@" in user_part:
                    credentials = user_part.split("@")[0]
                    if ":" in credentials:
                        db_user = credentials.split(":")[0]
                    else:
                        db_user = credentials

    print(f"Connecting to database server using: {conn_str.split('@')[-1] if '@' in conn_str else conn_str}")
    
    try:
        # Connect to 'postgres' database to create the target database
        conn = psycopg.connect(conn_str, autocommit=True)
        with conn.cursor() as cur:
            # Check if database exists
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
            exists = cur.fetchone()
            
            if not exists:
                print(f"Database '{target_db}' does not exist. Creating...")
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_db)))
                print(f"Database '{target_db}' created successfully.")
            else:
                print(f"Database '{target_db}' already exists.")
                
            # Grant privileges
            print(f"Granting all privileges on database '{target_db}' to user '{db_user}'...")
            cur.execute(sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                sql.Identifier(target_db),
                sql.Identifier(db_user)
            ))
            print("Privileges granted successfully.")
            
        conn.close()
    except Exception as e:
        print(f"Error occurred during database setup: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
