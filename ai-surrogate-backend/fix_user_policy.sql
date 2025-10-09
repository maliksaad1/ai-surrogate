-- Fix RLS policy for user registration
-- This allows the backend service to create user profiles during registration

-- Drop the existing restrictive policy
DROP POLICY IF EXISTS "Users can insert own profile" ON public.users;

-- Create a more permissive policy that allows service role to create users
CREATE POLICY "Enable user creation" ON public.users
    FOR INSERT WITH CHECK (true);

-- Keep the existing policies for other operations
-- Users can still only view and update their own profiles