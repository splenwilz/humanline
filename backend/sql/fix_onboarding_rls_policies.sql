-- Fix RLS policies for onboarding table
-- Run this if the table already exists but has restrictive policies

-- Drop existing policies (if they exist)
DROP POLICY IF EXISTS "Users can insert their own onboarding data" ON onboarding;
DROP POLICY IF EXISTS "Users can read their own onboarding data" ON onboarding;
DROP POLICY IF EXISTS "Users can update their own onboarding data" ON onboarding;
DROP POLICY IF EXISTS "Service role can insert onboarding data" ON onboarding;
DROP POLICY IF EXISTS "Service role can read onboarding data" ON onboarding;
DROP POLICY IF EXISTS "Service role can update onboarding data" ON onboarding;

-- Create new permissive policies for service role
CREATE POLICY "Service role can insert onboarding data" ON onboarding
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Service role can read onboarding data" ON onboarding
    FOR SELECT USING (true);

CREATE POLICY "Service role can update onboarding data" ON onboarding
    FOR UPDATE USING (true);

-- Create user-specific policies
CREATE POLICY "Users can read their own onboarding data" ON onboarding
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update their own onboarding data" ON onboarding
    FOR UPDATE USING (auth.uid()::text = user_id::text);
