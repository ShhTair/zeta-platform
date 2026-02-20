'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useRegister } from '@/lib/queries';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';

export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    inviteCode: '',
  });
  const registerMutation = useRegister();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await registerMutation.mutateAsync(formData);
      alert('Registration successful! Please log in.');
      router.push('/login');
    } catch (error: any) {
      alert(error.response?.data?.message || 'Registration failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="w-full max-w-md p-10 bg-white border border-[#DADCE0] rounded-lg shadow-google-md">
        <div className="text-center mb-8">
          <h1 className="text-[24px] font-medium text-[#202124] mb-2">Join ZETA</h1>
          <p className="text-[#5F6368] text-[14px]">Create your account (invite only)</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <Input
            type="text"
            label="Full Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="John Doe"
            required
          />

          <Input
            type="email"
            label="Email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            placeholder="you@example.com"
            required
          />

          <Input
            type="password"
            label="Password"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            placeholder="Create a strong password"
            required
          />

          <Input
            type="text"
            label="Invite Code"
            value={formData.inviteCode}
            onChange={(e) => setFormData({ ...formData, inviteCode: e.target.value })}
            placeholder="XXXX-XXXX-XXXX"
            required
          />

          <Button
            type="submit"
            className="w-full mt-6"
            disabled={registerMutation.isPending}
          >
            {registerMutation.isPending ? 'Creating account...' : 'Create Account'}
          </Button>
        </form>

        <p className="mt-6 text-center text-[14px] text-[#5F6368]">
          Already have an account?{' '}
          <Link href="/login" className="text-[#1A73E8] hover:underline font-medium">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
