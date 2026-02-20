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
    return <div className="text-[#5F6368] text-[14px]">Loading...</div>;
  }

  if (!profile) {
    return <Card><p className="text-[#5F6368]">Profile not found</p></Card>;
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
      <div className="mb-8">
        <h1 className="text-[28px] font-medium text-[#202124]">Profile</h1>
        <p className="text-[#5F6368] mt-1 text-[14px]">Manage your account settings</p>
      </div>

      <Card>
        <div className="flex items-center gap-4 mb-6 pb-6 border-b border-[#F1F3F4]">
          <div className="w-16 h-16 bg-[#1A73E8] rounded-full flex items-center justify-center text-[24px] font-medium text-white">
            {profile.name.charAt(0).toUpperCase()}
          </div>
          <div>
            <h2 className="text-[18px] font-medium text-[#202124]">{profile.name}</h2>
            <p className="text-[13px] text-[#5F6368]">{profile.email}</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
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

          <div className="pt-2">
            <Button type="submit" disabled={updateProfile.isPending}>
              {updateProfile.isPending ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </form>
      </Card>

      <Card>
        <h2 className="text-[18px] font-medium text-[#202124] mb-6">Account Information</h2>
        <div className="space-y-5">
          <div className="flex items-center gap-3 py-3 border-b border-[#F1F3F4]">
            <Shield size={20} className="text-[#5F6368]" />
            <div className="flex-1">
              <p className="text-[13px] text-[#5F6368]">Role</p>
              <p className="font-medium text-[#202124] text-[14px]">{profile.role.replace('_', ' ')}</p>
            </div>
          </div>

          <div className="flex items-center gap-3 py-3 border-b border-[#F1F3F4]">
            <User size={20} className="text-[#5F6368]" />
            <div className="flex-1">
              <p className="text-[13px] text-[#5F6368]">User ID</p>
              <p className="font-mono text-[13px] text-[#202124]">{profile.id}</p>
            </div>
          </div>

          <div className="flex items-center gap-3 py-3 border-b border-[#F1F3F4]">
            <Mail size={20} className="text-[#5F6368]" />
            <div className="flex-1">
              <p className="text-[13px] text-[#5F6368]">Member Since</p>
              <p className="text-[14px] text-[#202124]">{new Date(profile.createdAt).toLocaleDateString()}</p>
            </div>
          </div>

          <div className="pt-2">
            <p className="text-[13px] text-[#5F6368] mb-3">City Access</p>
            <div className="flex flex-wrap gap-2">
              {profile.role === 'SUPER_ADMIN' ? (
                <span className="px-3 py-1.5 bg-[#E8F0FE] text-[#1A73E8] rounded-full text-[13px] font-medium">
                  All Cities
                </span>
              ) : profile.cityAccess.length > 0 ? (
                profile.cityAccess.map((cityId) => (
                  <span key={cityId} className="px-3 py-1.5 bg-[#E8F0FE] text-[#1A73E8] rounded-full text-[13px] font-medium">
                    {cityId}
                  </span>
                ))
              ) : (
                <span className="text-[#5F6368] text-[14px]">No cities assigned</span>
              )}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
