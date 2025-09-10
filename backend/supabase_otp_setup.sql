-- OTP Setup for Supabase
-- Run this in your Supabase SQL editor

-- Create OTP codes table
CREATE TABLE IF NOT EXISTS otp_codes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT NOT NULL,
    otp_code TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    used BOOLEAN DEFAULT FALSE,
    created_at_utc TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_otp_codes_email ON otp_codes(email);

-- Create index on expires_at for cleanup operations
CREATE INDEX IF NOT EXISTS idx_otp_codes_expires_at ON otp_codes(expires_at);

-- Create index on used status
CREATE INDEX IF NOT EXISTS idx_otp_codes_used ON otp_codes(used);

-- Enable Row Level Security (RLS)
ALTER TABLE otp_codes ENABLE ROW LEVEL SECURITY;

-- Create policy to allow authenticated users to read their own OTP codes
CREATE POLICY "Users can read their own OTP codes" ON otp_codes
    FOR SELECT USING (auth.email() = email);

-- Create policy to allow service role to insert OTP codes
CREATE POLICY "Service role can insert OTP codes" ON otp_codes
    FOR INSERT WITH CHECK (true);

-- Create policy to allow service role to update OTP codes
CREATE POLICY "Service role can update OTP codes" ON otp_codes
    FOR UPDATE USING (true);

-- Create policy to allow service role to delete expired OTP codes
CREATE POLICY "Service role can delete expired OTP codes" ON otp_codes
    FOR DELETE USING (true);

-- Create function to clean up expired OTP codes
CREATE OR REPLACE FUNCTION cleanup_expired_otps()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM otp_codes 
    WHERE expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create a scheduled job to clean up expired OTPs (optional)
-- This requires pg_cron extension to be enabled
-- SELECT cron.schedule('cleanup-expired-otps', '*/15 * * * *', 'SELECT cleanup_expired_otps();');

-- Grant necessary permissions
GRANT ALL ON otp_codes TO authenticated;
GRANT ALL ON otp_codes TO service_role;

-- Insert sample data for testing (optional)
-- INSERT INTO otp_codes (email, otp_code, expires_at) VALUES 
-- ('test@example.com', '123456', NOW() + INTERVAL '10 minutes');

-- View the table structure
-- \d otp_codes

-- Test the cleanup function
-- SELECT cleanup_expired_otps();
