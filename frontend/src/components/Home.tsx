import type { FC } from 'react';
import { Link } from 'react-router-dom';
import logo from '../assets/paramountlogo.png';

const Homepage: FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-paramount-blue-800 to-paramount-blue-900 flex flex-col">
      <header className="py-6">
        <div className="paramount-container">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <img 
              src={logo} 
              alt="Paramount IT Logo" 
              className="h-12 w-12"
              />
              <h1 className="text-white font-bold text-xl">Paramount IT Support Management</h1>
            </div>
            
            <div className="space-x-4">
              <Link to="/login" className="text-white hover:text-paramount-yellow-200">
                Login
              </Link>
              <Link to="/register" className="bg-paramount-yellow-500 hover:bg-paramount-yellow-600 text-paramount-blue-900 px-4 py-2 rounded-md font-medium">
                Register
              </Link>
            </div>
          </div>
        </div>
      </header>
      
      <main className="flex-grow flex items-center">
        <div className="paramount-container">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="text-white space-y-6">
              <h1 className="text-4xl sm:text-5xl font-bold leading-tight">
                IT Issue Management <span className="text-paramount-yellow-400">Simplified</span>
              </h1>
              <p className="text-paramount-blue-100 text-lg sm:text-xl">
                A streamlined platform for logging, tracking, and resolving IT issues for Paramount Bank staff.
              </p>
              <div className="pt-4 flex flex-col sm:flex-row gap-4">
                <Link
                  to="/register"
                  className="bg-paramount-yellow-500 hover:bg-paramount-yellow-600 text-paramount-blue-900 px-6 py-3 rounded-md font-medium text-center"
                >
                  Get Started
                </Link>
                <Link
                  to="/login"
                  className="bg-white/10 hover:bg-white/20 text-white border border-white/30 px-6 py-3 rounded-md font-medium text-center"
                >
                  Login to Account
                </Link>
              </div>
              
              <div className="pt-8">
                <p className="text-paramount-blue-200 text-sm mb-3">Key Features:</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {[
                    'Easy Issue Submission',
                    'Real-time Status Updates',
                    'Detailed IT Reports',
                    'Secure OTP Authentication',
                    'Priority-based Resolution',
                    'File Attachment Support'
                  ].map((feature, index) => (
                    <div key={index} className="flex items-center">
                      <div className="bg-paramount-yellow-500/20 rounded-full p-1 mr-2">
                        <svg
                          className="h-4 w-4 text-paramount-yellow-400"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M5 13l4 4L19 7"
                          ></path>
                        </svg>
                      </div>
                      <span className="text-sm">{feature}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="hidden lg:block">
              <div className="bg-white p-6 rounded-xl shadow-2xl transform rotate-1">
                <div className="bg-paramount-blue-50 p-4 rounded-lg border border-paramount-blue-100">
                  <div className="space-y-4">
                    <div className="flex items-start space-x-3">
                      <div className="h-10 w-10 flex-shrink-0 rounded-full bg-paramount-blue-200 flex items-center justify-center">
                        <span className="font-bold text-paramount-blue-800">PI</span>
                      </div>
                      <div className="flex-1">
                        <h3 className="font-medium text-paramount-blue-800">Network Connectivity Issue</h3>
                        <p className="text-sm text-gray-600">Status: <span className="text-blue-600">In Progress</span></p>
                      </div>
                      <div className="bg-paramount-yellow-100 text-paramount-yellow-800 px-2 py-1 text-xs rounded-full">
                        High
                      </div>
                    </div>
                    
                    <div className="text-sm text-gray-600 border-t border-b border-gray-200 py-3">
                      <p>Wi-Fi connectivity issues on the 3rd floor. Users are experiencing intermittent drops in connection.</p>
                    </div>
                    
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-gray-500">May 19, 2025</span>
                      <button className="text-paramount-blue-600 font-medium">Update</button>
                    </div>
                  </div>
                </div>
                
                <div className="mt-6 flex justify-between items-center">
                  <div className="space-y-1">
                    <div className="h-2 bg-paramount-blue-200 rounded w-24"></div>
                    <div className="h-2 bg-paramount-blue-200 rounded w-32"></div>
                  </div>
                  <div className="h-8 w-20 bg-paramount-yellow-500 rounded"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
      
      <footer className="bg-paramount-blue-900 text-paramount-blue-200 py-8 border-t border-paramount-blue-700">
        <div className="paramount-container">
          <div className="text-center">
            <p>© {new Date().getFullYear()} Paramount IT. All rights reserved.</p>
            <p className="mt-2 text-sm">A secure platform for IT issue management.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Homepage



