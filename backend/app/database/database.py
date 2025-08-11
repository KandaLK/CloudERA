from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from app.core.config import settings
import logging
import sys

# Configure logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

def create_database_if_not_exists():
    """Create database and user if they don't exist"""
    try:
        # Parse database URL
        db_url_parts = settings.database_url.replace('postgresql://', '').split('/')
        user_pass_host = db_url_parts[0]
        db_name = db_url_parts[1]
        
        user_pass, host_port = user_pass_host.split('@')
        username, password = user_pass.split(':')
        host_port_parts = host_port.split(':')
        host = host_port_parts[0]
        port = host_port_parts[1] if len(host_port_parts) > 1 else '5432'
        
        # Connect to PostgreSQL as postgres user to create database
        postgres_url = f"postgresql://postgres:manelka1234@{host}:{port}/postgres"
        
        print(f"[Database] Checking if database '{db_name}' exists...")
        
        # Create engine for postgres database
        postgres_engine = create_engine(postgres_url)
        
        with postgres_engine.connect() as conn:
            # Set autocommit mode for database creation
            conn.execute(text("COMMIT"))
            
            # Check if database exists
            result = conn.execute(text(
                "SELECT 1 FROM pg_database WHERE datname = :db_name"
            ), {"db_name": db_name})
            
            if not result.fetchone():
                print(f"[Database] Creating database '{db_name}'...")
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                print(f"[Database] ✅ Database '{db_name}' created")
            else:
                print(f"[Database] ✅ Database '{db_name}' already exists")
            
            # Check if user exists
            result = conn.execute(text(
                "SELECT 1 FROM pg_user WHERE usename = :username"
            ), {"username": username})
            
            if not result.fetchone():
                print(f"[Database] Creating user '{username}'...")
                conn.execute(text(f"CREATE USER {username} WITH PASSWORD '{password}'"))
                print(f"[Database] ✅ User '{username}' created")
            else:
                print(f"[Database] ✅ User '{username}' already exists")
                
            # Grant database privileges
            conn.execute(text(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {username}"))
            
        postgres_engine.dispose()
        
        # Connect to the target database to grant schema privileges
        target_db_url = f"postgresql://postgres:manelka1234@{host}:{port}/{db_name}"
        target_engine = create_engine(target_db_url)
        
        with target_engine.connect() as conn:
            print(f"[Database] Setting schema permissions for '{username}'...")
            
            # Grant schema-level privileges (required for PostgreSQL 15+)
            conn.execute(text(f"GRANT ALL PRIVILEGES ON SCHEMA public TO {username}"))
            conn.execute(text(f"GRANT CREATE ON SCHEMA public TO {username}"))
            conn.execute(text(f"GRANT USAGE ON SCHEMA public TO {username}"))
            
            # Grant default privileges for future objects
            conn.execute(text(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {username}"))
            conn.execute(text(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {username}"))
            conn.execute(text(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO {username}"))
            conn.execute(text(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TYPES TO {username}"))
            
            # Commit the changes
            conn.execute(text("COMMIT"))
            
            print(f"[Database] ✅ Schema permissions granted to '{username}'")
            
        target_engine.dispose()
        
    except Exception as e:
        print(f"[Database] ❌ Error creating database: {str(e)}")
        print("[Database] Please ensure PostgreSQL is running and postgres user password is 'manelka1234'")
        sys.exit(1)

def verify_connection():
    """Verify database connection works"""
    try:
        test_engine = create_engine(settings.database_url)
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        test_engine.dispose()
        print(f"[Database] ✅ Connection verified: {settings.database_url.split('@')[-1]}")
        return True
    except Exception as e:
        print(f"[Database] ❌ Connection failed: {str(e)}")
        return False

def verify_schema_permissions():
    """Verify user has necessary schema permissions"""
    try:
        print("[Database] Verifying schema permissions...")
        test_engine = create_engine(settings.database_url)
        
        with test_engine.connect() as conn:
            # Check if user can create types (the main issue we encountered)
            result = conn.execute(text("""
                SELECT 
                    has_schema_privilege(current_user, 'public', 'CREATE') as can_create,
                    has_schema_privilege(current_user, 'public', 'USAGE') as can_use,
                    current_user as username
            """))
            
            permissions = result.fetchone()
            username = permissions.username
            can_create = permissions.can_create
            can_use = permissions.can_use
            
            if can_create and can_use:
                print(f"[Database] ✅ User '{username}' has proper schema permissions")
                test_engine.dispose()
                return True
            else:
                print(f"[Database] ❌ User '{username}' lacks schema permissions:")
                print(f"  - CREATE permission: {can_create}")
                print(f"  - USAGE permission: {can_use}")
                test_engine.dispose()
                return False
                
    except Exception as e:
        print(f"[Database] ❌ Error checking schema permissions: {str(e)}")
        return False

def fix_schema_permissions():
    """Fix schema permissions if they're missing"""
    try:
        print("[Database] Attempting to fix schema permissions...")
        
        # Parse database URL to get connection details
        db_url_parts = settings.database_url.replace('postgresql://', '').split('/')
        user_pass_host = db_url_parts[0]
        db_name = db_url_parts[1]
        
        user_pass, host_port = user_pass_host.split('@')
        username, password = user_pass.split(':')
        host_port_parts = host_port.split(':')
        host = host_port_parts[0]
        port = host_port_parts[1] if len(host_port_parts) > 1 else '5432'
        
        # Connect as postgres to grant permissions
        postgres_url = f"postgresql://postgres:manelka1234@{host}:{port}/{db_name}"
        postgres_engine = create_engine(postgres_url)
        
        with postgres_engine.connect() as conn:
            print(f"[Database] Granting schema permissions to '{username}'...")
            
            # Grant comprehensive schema privileges
            conn.execute(text(f"GRANT ALL PRIVILEGES ON SCHEMA public TO {username}"))
            conn.execute(text(f"GRANT CREATE ON SCHEMA public TO {username}"))
            conn.execute(text(f"GRANT USAGE ON SCHEMA public TO {username}"))
            
            # Grant default privileges for future objects
            conn.execute(text(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {username}"))
            conn.execute(text(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {username}"))
            conn.execute(text(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO {username}"))
            conn.execute(text(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TYPES TO {username}"))
            
            conn.execute(text("COMMIT"))
            print(f"[Database] ✅ Schema permissions fixed for '{username}'")
            
        postgres_engine.dispose()
        return True
        
    except Exception as e:
        print(f"[Database] ❌ Could not fix schema permissions: {str(e)}")
        print("[Database] Please run this command manually:")
        print(f"sudo -u postgres psql -d {db_name} -c \"GRANT ALL PRIVILEGES ON SCHEMA public TO {username}; GRANT CREATE ON SCHEMA public TO {username};\"")
        return False

# Ensure database exists before creating engine
create_database_if_not_exists()

# PostgreSQL optimized configuration
engine = create_engine(
    settings.database_url,
    pool_size=20,                # Connection pool size
    max_overflow=30,             # Maximum overflow connections  
    pool_recycle=3600,           # Recycle connections every hour
    pool_pre_ping=True,          # Verify connections before use
    echo=False,                  # Set to True for SQL debugging
    echo_pool=False              # Set to True for connection pool debugging
)

# Verify connection works
if not verify_connection():
    print("[Database] ❌ Cannot connect to PostgreSQL database")
    sys.exit(1)

# Verify and fix schema permissions
if not verify_schema_permissions():
    print("[Database] ⚠️  Schema permissions missing, attempting to fix...")
    if fix_schema_permissions():
        # Verify the fix worked
        if not verify_schema_permissions():
            print("[Database] ❌ Could not fix schema permissions automatically")
            print("[Database] Please run the manual fix command shown above")
            sys.exit(1)
    else:
        sys.exit(1)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()