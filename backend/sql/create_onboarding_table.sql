-- Create onboarding table in Supabase
CREATE TABLE IF NOT EXISTS onboarding (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    company_domain VARCHAR(255) NOT NULL UNIQUE,
    company_size VARCHAR(50) NOT NULL,
    company_industry VARCHAR(100) NOT NULL,
    company_roles VARCHAR(100) NOT NULL,
    your_needs VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'completed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_onboarding_user_id ON onboarding(user_id);

-- Create index on company_domain for faster lookups
CREATE INDEX IF NOT EXISTS idx_onboarding_company_domain ON onboarding(company_domain);

-- Create index on created_at for sorting
CREATE INDEX IF NOT EXISTS idx_onboarding_created_at ON onboarding(created_at);

-- Enable Row Level Security (RLS)
ALTER TABLE onboarding ENABLE ROW LEVEL SECURITY;

-- Create policy to allow service role to insert data (for backend API)
CREATE POLICY "Service role can insert onboarding data" ON onboarding
    FOR INSERT WITH CHECK (true);

-- Create policy to allow service role to read data
CREATE POLICY "Service role can read onboarding data" ON onboarding
    FOR SELECT USING (true);

-- Create policy to allow service role to update data
CREATE POLICY "Service role can update onboarding data" ON onboarding
    FOR UPDATE USING (true);

-- Create policy to allow authenticated users to read their own data
CREATE POLICY "Users can read their own onboarding data" ON onboarding
    FOR SELECT USING (auth.uid()::text = user_id::text);

-- Create policy to allow authenticated users to update their own data
CREATE POLICY "Users can update their own onboarding data" ON onboarding
    FOR UPDATE USING (auth.uid()::text = user_id::text);
