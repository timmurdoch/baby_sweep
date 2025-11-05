import React, { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Menu, X, Home, Users, Settings, TrendingUp, FileText, Bell, Search, ChevronDown, Plus } from 'lucide-react';

export default function AdminPanel() {
  const [sidebarOpen, setSidebarOpen] = useState(false); // Start closed on mobile
  const [currentView, setCurrentView] = useState('dashboard');
  const [selectedUser, setSelectedUser] = useState(null);
  const [isMobile, setIsMobile] = useState(false);

  // Detect screen size
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
      if (window.innerWidth >= 1024) {
        setSidebarOpen(true);
      } else {
        setSidebarOpen(false);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Sample data
  const revenueData = [
    { month: 'Jan', revenue: 45000 },
    { month: 'Feb', revenue: 52000 },
    { month: 'Mar', revenue: 48000 },
    { month: 'Apr', revenue: 61000 },
    { month: 'May', revenue: 55000 },
    { month: 'Jun', revenue: 67000 },
  ];

  const userActivityData = [
    { day: 'Mon', active: 234 },
    { day: 'Tue', active: 267 },
    { day: 'Wed', active: 289 },
    { day: 'Thu', active: 312 },
    { day: 'Fri', active: 298 },
    { day: 'Sat', active: 187 },
    { day: 'Sun', active: 165 },
  ];

  const users = [
    { id: 1, name: 'Sarah Johnson', email: 'sarah.j@example.com', role: 'Admin', status: 'Active', lastLogin: '2 hours ago' },
    { id: 2, name: 'Mike Chen', email: 'mike.c@example.com', role: 'Editor', status: 'Active', lastLogin: '5 hours ago' },
    { id: 3, name: 'Emma Davis', email: 'emma.d@example.com', role: 'Viewer', status: 'Inactive', lastLogin: '2 days ago' },
    { id: 4, name: 'James Wilson', email: 'james.w@example.com', role: 'Editor', status: 'Active', lastLogin: '1 hour ago' },
    { id: 5, name: 'Lisa Anderson', email: 'lisa.a@example.com', role: 'Admin', status: 'Active', lastLogin: '30 mins ago' },
  ];

  const recentActivities = [
    { id: 1, user: 'Sarah Johnson', action: 'Updated user permissions', time: '5 minutes ago' },
    { id: 2, user: 'Mike Chen', action: 'Created new report', time: '15 minutes ago' },
    { id: 3, user: 'Emma Davis', action: 'Logged in', time: '1 hour ago' },
    { id: 4, user: 'James Wilson', action: 'Modified settings', time: '2 hours ago' },
  ];

  const stats = [
    { label: 'Total Users', value: '2,543', change: '+12%', positive: true },
    { label: 'Active Sessions', value: '1,234', change: '+5%', positive: true },
    { label: 'Revenue', value: '$67,543', change: '+18%', positive: true },
    { label: 'Avg Response Time', value: '1.2s', change: '-8%', positive: true },
  ];

  const NavItem = ({ icon: Icon, label, view }) => (
    <button
      onClick={() => {
        setCurrentView(view);
        // Close sidebar on mobile after navigation
        if (isMobile) {
          setSidebarOpen(false);
        }
      }}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
        currentView === view
          ? 'bg-blue-500 text-white'
          : 'text-gray-700 hover:bg-gray-100'
      }`}
    >
      <Icon size={20} />
      <span className="font-medium">{label}</span>
    </button>
  );

  const DashboardView = () => (
    <div className="space-y-4 md:space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-6">
        {stats.map((stat, index) => (
          <div key={index} className="bg-white rounded-lg shadow-sm p-4 md:p-6 border border-gray-200">
            <div className="text-xs md:text-sm text-gray-600 mb-1">{stat.label}</div>
            <div className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">{stat.value}</div>
            <div className={`text-xs md:text-sm font-medium ${stat.positive ? 'text-green-600' : 'text-red-600'}`}>
              {stat.change} from last month
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
        <div className="bg-white rounded-lg shadow-sm p-4 md:p-6 border border-gray-200">
          <h3 className="text-base md:text-lg font-semibold text-gray-900 mb-4">Revenue Overview</h3>
          <div className="w-full overflow-x-auto">
            <ResponsiveContainer width="100%" height={200} minWidth={300}>
              <LineChart data={revenueData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="month" stroke="#666" style={{ fontSize: '12px' }} />
                <YAxis stroke="#666" style={{ fontSize: '12px' }} />
                <Tooltip />
                <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-4 md:p-6 border border-gray-200">
          <h3 className="text-base md:text-lg font-semibold text-gray-900 mb-4">User Activity</h3>
          <div className="w-full overflow-x-auto">
            <ResponsiveContainer width="100%" height={200} minWidth={300}>
              <BarChart data={userActivityData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="day" stroke="#666" style={{ fontSize: '12px' }} />
                <YAxis stroke="#666" style={{ fontSize: '12px' }} />
                <Tooltip />
                <Bar dataKey="active" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-4 md:p-6 border-b border-gray-200">
          <h3 className="text-base md:text-lg font-semibold text-gray-900">Recent Activity</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {recentActivities.map((activity) => (
            <div key={activity.id} className="p-3 md:p-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-gray-900 text-sm md:text-base truncate">{activity.user}</div>
                  <div className="text-xs md:text-sm text-gray-600">{activity.action}</div>
                </div>
                <div className="text-xs md:text-sm text-gray-500 whitespace-nowrap">{activity.time}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const UsersView = () => (
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <h2 className="text-xl md:text-2xl font-bold text-gray-900">User Management</h2>
        <button className="flex items-center justify-center gap-2 bg-blue-500 text-white px-4 py-2.5 rounded-lg hover:bg-blue-600 transition-colors text-sm md:text-base">
          <Plus size={18} />
          <span>Add User</span>
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-3 md:p-4 border-b border-gray-200">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search users..."
              className="w-full pl-10 pr-4 py-2 text-sm md:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px]">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden sm:table-cell">Last Login</th>
                <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-3 md:px-6 py-3 md:py-4">
                    <div>
                      <div className="font-medium text-gray-900 text-sm md:text-base">{user.name}</div>
                      <div className="text-xs md:text-sm text-gray-500 truncate max-w-[150px] md:max-w-none">{user.email}</div>
                    </div>
                  </td>
                  <td className="px-3 md:px-6 py-3 md:py-4">
                    <span className="px-2 md:px-3 py-1 text-xs md:text-sm rounded-full bg-blue-100 text-blue-800 whitespace-nowrap">
                      {user.role}
                    </span>
                  </td>
                  <td className="px-3 md:px-6 py-3 md:py-4">
                    <span className={`px-2 md:px-3 py-1 text-xs md:text-sm rounded-full whitespace-nowrap ${
                      user.status === 'Active'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {user.status}
                    </span>
                  </td>
                  <td className="px-3 md:px-6 py-3 md:py-4 text-xs md:text-sm text-gray-600 hidden sm:table-cell">{user.lastLogin}</td>
                  <td className="px-3 md:px-6 py-3 md:py-4">
                    <button
                      onClick={() => setSelectedUser(user)}
                      className="text-blue-600 hover:text-blue-800 font-medium text-xs md:text-sm"
                    >
                      Edit
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl p-4 md:p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg md:text-xl font-bold text-gray-900">Edit User</h3>
              <button
                onClick={() => setSelectedUser(null)}
                className="text-gray-400 hover:text-gray-600 p-1"
                aria-label="Close"
              >
                <X size={24} />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  defaultValue={selectedUser.name}
                  className="w-full px-4 py-2.5 text-sm md:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  defaultValue={selectedUser.email}
                  className="w-full px-4 py-2.5 text-sm md:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                <select
                  defaultValue={selectedUser.role}
                  className="w-full px-4 py-2.5 text-sm md:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option>Admin</option>
                  <option>Editor</option>
                  <option>Viewer</option>
                </select>
              </div>
              <div className="flex flex-col sm:flex-row gap-3 pt-4">
                <button className="flex-1 bg-blue-500 text-white px-4 py-2.5 rounded-lg hover:bg-blue-600 transition-colors text-sm md:text-base font-medium">
                  Save Changes
                </button>
                <button
                  onClick={() => setSelectedUser(null)}
                  className="flex-1 bg-gray-200 text-gray-700 px-4 py-2.5 rounded-lg hover:bg-gray-300 transition-colors text-sm md:text-base font-medium"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const SettingsView = () => (
    <div className="space-y-4 md:space-y-6">
      <h2 className="text-xl md:text-2xl font-bold text-gray-900">Settings</h2>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 md:p-6">
        <h3 className="text-base md:text-lg font-semibold text-gray-900 mb-4">General Settings</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Site Name</label>
            <input
              type="text"
              defaultValue="Admin Dashboard"
              className="w-full px-4 py-2.5 text-sm md:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Admin Email</label>
            <input
              type="email"
              defaultValue="admin@example.com"
              className="w-full px-4 py-2.5 text-sm md:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex items-center gap-3">
            <input type="checkbox" id="notifications" className="h-5 w-5 text-blue-500 rounded" defaultChecked />
            <label htmlFor="notifications" className="text-sm md:text-base text-gray-700">Enable email notifications</label>
          </div>
          <div className="flex items-center gap-3">
            <input type="checkbox" id="maintenance" className="h-5 w-5 text-blue-500 rounded" />
            <label htmlFor="maintenance" className="text-sm md:text-base text-gray-700">Maintenance mode</label>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 md:p-6">
        <h3 className="text-base md:text-lg font-semibold text-gray-900 mb-4">Security</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Session Timeout (minutes)</label>
            <input
              type="number"
              defaultValue="30"
              className="w-full px-4 py-2.5 text-sm md:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex items-center gap-3">
            <input type="checkbox" id="2fa" className="h-5 w-5 text-blue-500 rounded" defaultChecked />
            <label htmlFor="2fa" className="text-sm md:text-base text-gray-700">Require two-factor authentication</label>
          </div>
          <div className="flex items-center gap-3">
            <input type="checkbox" id="password-policy" className="h-5 w-5 text-blue-500 rounded" defaultChecked />
            <label htmlFor="password-policy" className="text-sm md:text-base text-gray-700">Enforce strong password policy</label>
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button className="w-full sm:w-auto bg-blue-500 text-white px-6 py-2.5 rounded-lg hover:bg-blue-600 transition-colors text-sm md:text-base font-medium">
          Save Settings
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile overlay backdrop */}
      {sidebarOpen && isMobile && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`fixed left-0 top-0 h-full bg-white border-r border-gray-200 transition-all duration-300 ${
        sidebarOpen ? 'w-64' : 'w-0'
      } overflow-hidden z-40`}>
        <div className="p-4 md:p-6 border-b border-gray-200">
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">Admin Panel</h1>
        </div>
        <nav className="p-3 md:p-4 space-y-2">
          <NavItem icon={Home} label="Dashboard" view="dashboard" />
          <NavItem icon={Users} label="Users" view="users" />
          <NavItem icon={TrendingUp} label="Analytics" view="dashboard" />
          <NavItem icon={FileText} label="Reports" view="dashboard" />
          <NavItem icon={Settings} label="Settings" view="settings" />
        </nav>
      </div>

      {/* Main Content */}
      <div className={`transition-all duration-300 ${sidebarOpen && !isMobile ? 'ml-64' : 'ml-0'}`}>
        {/* Header */}
        <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
          <div className="flex items-center justify-between px-3 md:px-6 py-3 md:py-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors touch-manipulation"
              aria-label="Toggle sidebar"
            >
              {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
            </button>

            <div className="flex items-center gap-2 md:gap-4">
              <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors relative touch-manipulation" aria-label="Notifications">
                <Bell size={20} />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
              <div className="flex items-center gap-2 md:gap-3">
                <div className="w-8 h-8 md:w-10 md:h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-semibold text-sm md:text-base">
                  AD
                </div>
                <div className="hidden sm:block">
                  <div className="font-medium text-gray-900 text-sm md:text-base">Admin User</div>
                  <div className="text-xs md:text-sm text-gray-500">Administrator</div>
                </div>
                <ChevronDown size={18} className="text-gray-400 hidden sm:block" />
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-3 md:p-6">
          {currentView === 'dashboard' && <DashboardView />}
          {currentView === 'users' && <UsersView />}
          {currentView === 'settings' && <SettingsView />}
        </main>
      </div>
    </div>
  );
}