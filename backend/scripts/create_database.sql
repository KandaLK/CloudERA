-- PostgreSQL Database Creation Script for Cloud ERA
-- Run this script as a PostgreSQL superuser (postgres) to create the database and user

-- Create database
CREATE DATABASE "cloud-web"
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Create user
CREATE USER cloud_era_user WITH
    LOGIN
    NOSUPERUSER
    INHERIT
    CREATEDB
    CREATEROLE
    NOREPLICATION
    PASSWORD 'cloud_era_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE "cloud-web" TO cloud_era_user;

-- Connect to the new database
\c "cloud-web";

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO cloud_era_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cloud_era_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cloud_era_user;

-- Ensure future objects also have correct privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO cloud_era_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO cloud_era_user;