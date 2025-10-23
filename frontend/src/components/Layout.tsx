import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { FiLogOut, FiVideo, FiUser, FiGrid, FiList } from 'react-icons/fi';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-900">
      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-6">
              <Link to="/" className="flex items-center gap-2 text-white font-bold text-xl">
                <FiVideo className="text-2xl" />
                Shinobi Clone
              </Link>

              <div className="flex items-center gap-2">
                <Link
                  to="/"
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg transition ${
                    location.pathname === '/'
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  <FiList />
                  <span className="text-sm">List</span>
                </Link>
                <Link
                  to="/grid"
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg transition ${
                    location.pathname === '/grid'
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  <FiGrid />
                  <span className="text-sm">Grid</span>
                </Link>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-gray-300">
                <FiUser />
                <span>{user?.username}</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 text-gray-300 hover:text-white hover:bg-gray-700 rounded-lg transition"
              >
                <FiLogOut />
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main>{children}</main>

      <footer className="bg-gray-800 border-t border-gray-700 mt-12">
        <div className="container mx-auto px-4 py-6">
          <p className="text-center text-gray-400 text-sm">
            Shinobi Clone - Video Surveillance System
          </p>
        </div>
      </footer>
    </div>
  );
};
