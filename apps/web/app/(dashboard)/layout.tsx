'use client';

import Sidebar from '@/components/layout/Sidebar';
import Navbar from '@/components/layout/Navbar';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-[#F9FAFB]">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Navbar />
          <main className="flex-1 overflow-y-auto p-6 bg-white">
            {children}
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
