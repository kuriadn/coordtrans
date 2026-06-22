-- Run on the HOST PostgreSQL as a superuser (e.g. sudo -u postgres psql).
-- Adjust database name if needed.

CREATE USER fayvad WITH PASSWORD 'your-password-here';
CREATE DATABASE fayvad_survey OWNER fayvad;
\c fayvad_survey
CREATE EXTENSION IF NOT EXISTS postgis;

-- Allow Docker containers to reach host Postgres (pick one approach):

-- Option A: trust connections from Docker bridge (common on Linux)
-- Edit pg_hba.conf and add:
--   host  fayvad_survey  fayvad  172.16.0.0/12  scram-sha-256
-- Then reload: sudo systemctl reload postgresql

-- Option B: listen on all interfaces in postgresql.conf:
--   listen_addresses = '*'
