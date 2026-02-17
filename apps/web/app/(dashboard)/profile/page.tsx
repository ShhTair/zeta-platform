'use client';

import { useState, useEffect } from 'react';
import { useProfile, useUpdateProfile } from '@/lib/queries';
import { useAuthStore } from '@/lib/store';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import { User, Mail, Shield } from 'lucide-react';

export default function ProfilePage() {
  const { user: storeUser, setUser } = useAuthStore();
  const { data: profile, isLoading } = useProfile();
  const updateProfile = useUpdateProfile();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
  });

  useEffect(() => {
    if (profile) {
      setFormData({
        name: profile.name,
        email: profile.email,
      });
    }
  }, [profile]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!profile) {
    return <Card><p>Profile not found</p></Card>;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const updated = await updateProfile.mutateAsync(formData);
      
      // Update store and localStorage
      const updatedUser = { ...storeUser!, ...updated };
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
      
      alert('Profile updated successfully!');
    } catch (error: any) {
      alert(error.response?.data?.message || 'Failed to update profile');
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Profile</h1>
        <p className="text-gray-400 mt-1">Manage your account settings</p>
      </div>

      <Card>
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center text-2xl font-bold">
            {profile.name.charAt(0).toUpperCase()}
          </div>
          <div>
            <h2 className="text-xl font-bold">{profile.name}</h2>
            <p className="text-sm text-gray-400">{profile.email}</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Full Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />

          <Input
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            required
          />

          <Button type="submit" disabled={updateProfile.isPending}>
            {updateProfile.isPending ? 'Saving...' : 'Save Changes'}
          </Button>
        </form>
      </Card>

      <Card>
        <h2 className="text-xl font-bold mb-4">Account Information</h2>
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <Shield size={20} className="text-gray-400" />
            <div>
              <p className="text-sm text-gray-400">Role</p>
              <p className="font-medium">{profile.role.replace('_', ' ')}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <User size={20} className="text-gray-400" />
            <div>
              <p className="text-sm text-gray-400">User ID</p>
              <p className="font-mono text-sm">{profile.id}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Mail size={20} className="text-gray-400" />
            <div>
              <p className="text-sm text-gray-400">Member Since</p>
              <p>{new Date(profile.createdAt).toLocaleDateString()}</p>
            </div>
          </div>

          <div>
            <p className="text-sm text-gray-400 mb-2">City Access</p>
            <div className="flex flex-wrap gap-2">
              {profile.role === 'SUPER_ADMIN' ? (
                <span className="px-3 py-1 bg-purple-600 rounded-full text-sm">
                  All Cities
                </span>
              ) : profile.cityAccess.length > 0 ? (
                profile.cityAccess.map((cityId) => (
                  <span key={cityId} className="px-3 py-1 bg-blue-600 rounded-full text-sm">
                    {cityId}
                  </span>
                ))
              ) : (
                <span className="text-gray-500">No cities assigned</span>
              )}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
