import React, { useState } from 'react';
import './DashboardLayout.css';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import { Outlet, useNavigate } from 'react-router-dom';

export function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchValue, setSearchValue] = useState('');
  const navigate = useNavigate();

  const handleSearchSubmit = (query) => {
    if (query.trim()) {
      navigate(`/standards?search=${encodeURIComponent(query)}`);
    }
  };

  return (
    <div className="dashboard-layout">
      <Navbar
        onMenuToggle={() => setSidebarOpen((prev) => !prev)}
        searchValue={searchValue}
        onSearchChange={setSearchValue}
        onSearchSubmit={handleSearchSubmit}
      />

      <div className="dashboard-body">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <main className="dashboard-content">
          <div className="dashboard-container">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

export default DashboardLayout;
