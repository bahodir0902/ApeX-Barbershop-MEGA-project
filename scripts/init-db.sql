-- PostgreSQL initialization script
-- This script runs when the database container is first created

-- Create extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
        CREATE TYPE user_role AS ENUM ('client', 'barber', 'owner', 'admin');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'privacy_level') THEN
        CREATE TYPE privacy_level AS ENUM ('private', 'public');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'appointment_status') THEN
        CREATE TYPE appointment_status AS ENUM ('pending', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show');
    END IF;
END $$;

-- Log successful initialization
SELECT 'ApeX Barbershop database initialized successfully!' as message;
