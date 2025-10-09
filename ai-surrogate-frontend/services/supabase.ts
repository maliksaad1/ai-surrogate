import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://oipnwnrkjhegtodzyoez.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9pcG53bnJramhlZ3RvZHp5b2V6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAwMDMxNzksImV4cCI6MjA3NTU3OTE3OX0.AKoNejtbvmU7XM8j32EIvj-jl2fExNAKL8M7N0binME';

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
});

export default supabase;