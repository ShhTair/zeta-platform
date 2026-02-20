'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';

export default function LoginPage() {
  const router = useRouter();
  const { setUser, setToken } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Hardcoded validation
    if (
      (email === 'admin@zeta.kz' || email === 'admin@zeta.local') &&
      password === 'admin123'
    ) {
      const token = 'fake-jwt-token-' + Date.now();
      const user = { 
        id: 'admin-1',
        email, 
        name: 'Admin', 
        role: 'SUPER_ADMIN' as const, 
        cityAccess: [],
        createdAt: new Date().toISOString()
      };
      
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      setToken(token);
      setUser(user);
      
      router.push('/dashboard');
    } else {
      setError('Invalid email or password');
    }
  };

  return (
    <div className="relative min-h-screen bg-gdrive-bg">
      {/* Background preview */}
      <div className="absolute inset-0 blur-sm opacity-40">
        <div className="p-8">
          <h1 className="text-3xl font-google font-medium text-gdrive-text mb-8">
            ZETA Platform
          </h1>
          <div className="grid grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="bg-white rounded-lg p-6 shadow-google-sm h-32" />
            ))}
          </div>
        </div>
      </div>

      {/* Login overlay */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-md flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-google-md p-8 w-full max-w-md">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gdrive-blue rounded-full mx-auto mb-4 flex items-center justify-center">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
            </div>
            <h2 className="text-2xl font-google font-medium text-gdrive-text">
              Sign in to ZETA
            </h2>
            <p className="text-sm text-gdrive-secondary mt-2">Admin Panel</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gdrive-text mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 border border-gdrive-border rounded-lg focus:outline-none focus:ring-2 focus:ring-gdrive-blue focus:border-transparent"
                placeholder="admin@zeta.kz"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gdrive-text mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gdrive-border rounded-lg focus:outline-none focus:ring-2 focus:ring-gdrive-blue focus:border-transparent"
                placeholder="••••••••"
                required
              />
            </div>

            <button
              type="submit"
              className="w-full bg-gdrive-blue text-white py-2.5 rounded-lg font-medium hover:bg-blue-600 transition-colors"
            >
              Sign in
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-xs text-gdrive-secondary">
              Credentials: admin@zeta.kz / admin123
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
