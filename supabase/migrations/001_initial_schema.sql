-- Migration: 001_initial_schema.sql
-- Description: Initialize dongne.me MVP database schema
-- Tables: subscribers, briefings, send_logs
-- Features: UUID PKs, RLS policies, indexes for performance
-- Created: 2026-06-25

-- ============================================================================
-- 1. SUBSCRIBERS TABLE
-- ============================================================================
-- Stores email subscribers with double opt-in confirmation
-- Columns:
--   id: UUID primary key
--   email: Unique email address
--   region: Geographic region code (default: 'suwon')
--   status: Subscription state (pending | active | unsubscribed)
--   token: Unique token for opt-in/unsubscribe links
--   created_at: Subscription request timestamp
--   confirmed_at: Double opt-in confirmation timestamp

CREATE TABLE IF NOT EXISTS subscribers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  region text NOT NULL DEFAULT 'suwon',
  status text NOT NULL DEFAULT 'pending',
  token text UNIQUE NOT NULL,
  created_at timestamptz DEFAULT now(),
  confirmed_at timestamptz
);

-- Indexes for subscribers
CREATE INDEX IF NOT EXISTS idx_subscribers_email ON subscribers(email);
CREATE INDEX IF NOT EXISTS idx_subscribers_token ON subscribers(token);
CREATE INDEX IF NOT EXISTS idx_subscribers_status ON subscribers(status);

-- Enable RLS on subscribers
ALTER TABLE subscribers ENABLE ROW LEVEL SECURITY;

-- RLS Policy: service_role has full access
CREATE POLICY "service_role_all_access" ON subscribers
  FOR ALL USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- RLS Policy: anon role cannot access (backend only)
CREATE POLICY "anon_no_access" ON subscribers
  FOR ALL USING (false)
  WITH CHECK (false);

-- ============================================================================
-- 2. BRIEFINGS TABLE
-- ============================================================================
-- Stores daily briefings by region, date, and category
-- Columns:
--   id: UUID primary key
--   region: Geographic region code (e.g., 'suwon')
--   date: Briefing date
--   category: Content category (weather | news | license)
--   raw_data: Original API response as JSONB
--   summary: AI-generated summary from Gemini
--   sources: Array of source links [{title, url}]
--   created_at: Record creation timestamp
-- Constraint: UNIQUE(region, date, category) prevents duplicates

CREATE TABLE IF NOT EXISTS briefings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  region text NOT NULL,
  date date NOT NULL,
  category text NOT NULL,
  raw_data jsonb,
  summary text,
  sources jsonb,
  created_at timestamptz DEFAULT now(),
  UNIQUE(region, date, category)
);

-- Indexes for briefings (critical for web dashboard queries)
CREATE INDEX IF NOT EXISTS idx_briefings_region_date ON briefings(region, date DESC);
CREATE INDEX IF NOT EXISTS idx_briefings_date ON briefings(date DESC);

-- Enable RLS on briefings
ALTER TABLE briefings ENABLE ROW LEVEL SECURITY;

-- RLS Policy: anon role can SELECT (for web dashboard)
CREATE POLICY "anon_select_briefings" ON briefings
  FOR SELECT USING (auth.role() = 'anon');

-- RLS Policy: service_role has full access
CREATE POLICY "service_role_all_access_briefings" ON briefings
  FOR ALL USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- ============================================================================
-- 3. SEND_LOGS TABLE
-- ============================================================================
-- Tracks email and Kakao message delivery status
-- Columns:
--   id: UUID primary key
--   subscriber_id: Foreign key to subscribers(id) with CASCADE delete
--   briefing_date: Date of the briefing sent
--   channel: Delivery channel (email | kakao)
--   status: Delivery status (sent | failed | bounced)
--   sent_at: Timestamp when message was sent
--   error_message: Error details if status is 'failed'

CREATE TABLE IF NOT EXISTS send_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  subscriber_id uuid NOT NULL REFERENCES subscribers(id) ON DELETE CASCADE,
  briefing_date date NOT NULL,
  channel text NOT NULL,
  status text NOT NULL,
  sent_at timestamptz DEFAULT now(),
  error_message text
);

-- Indexes for send_logs (for analytics and retry queries)
CREATE INDEX IF NOT EXISTS idx_send_logs_subscriber_id ON send_logs(subscriber_id);
CREATE INDEX IF NOT EXISTS idx_send_logs_briefing_date ON send_logs(briefing_date DESC);

-- Enable RLS on send_logs
ALTER TABLE send_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policy: service_role has full access
CREATE POLICY "service_role_all_access_send_logs" ON send_logs
  FOR ALL USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- RLS Policy: anon role cannot access
CREATE POLICY "anon_no_access_send_logs" ON send_logs
  FOR ALL USING (false)
  WITH CHECK (false);

-- ============================================================================
-- MIGRATION NOTES
-- ============================================================================
-- 1. All tables use UUID primary keys for distributed system compatibility
-- 2. RLS is enabled on all tables:
--    - subscribers: service_role only (backend access)
--    - briefings: anon can SELECT (web dashboard), service_role full access
--    - send_logs: service_role only (backend logging)
-- 3. Indexes are optimized for:
--    - subscribers: email/token lookups, status filtering
--    - briefings: region+date queries (web dashboard), date-based sorting
--    - send_logs: subscriber tracking, date-based analytics
-- 4. Foreign key on send_logs.subscriber_id uses CASCADE delete
--    (deleting a subscriber removes their send logs)
-- 5. UNIQUE constraint on briefings(region, date, category) prevents
--    duplicate briefing generation for the same day/region/category
