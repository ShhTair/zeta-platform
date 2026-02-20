'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useLogin } from '@/lib/queries';
import { useAuthStore } from '@/lib/store';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { setUser, setToken } = useAuthStore();
  const loginMutation = useLogin();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const data = await loginMutation.mutateAsync({ email, password });
      
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      setToken(data.token);
      setUser(data.user);
      
      router.push('/dashboard');
    } catch (error: any) {
      alert(error.response?.data?.message || 'Login failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="w-full max-w-md p-10 bg-white border border-[#DADCE0] rounded-lg shadow-google-md">
        <div className="text-center mb-8">
          <h1 className="text-[24px] font-medium text-[#202124] mb-2">Welcome to ZETA</h1>
          <p className="text-[#5F6368] text-[14px]">Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <Input
            type="email"
            label="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
          />

          <Input
            type="password"
            label="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            required
          />

          <Button
            type="submit"
            className="w-full mt-6"
            disabled={loginMutation.isPending}
          >
            {loginMutation.isPending ? 'Signing in...' : 'Sign In'}
          </Button>
        </form>

        <p className="mt-6 text-center text-[14px] text-[#5F6368]">
          Don't have an account?{' '}
          <Link href="/register" className="text-[#1A73E8] hover:underline font-medium">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}
