import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './components/auth/PrivateRoute';
import Login from './components/auth/Login';
import SignUp from './components/auth/SignUp';
import Dashboard from './components/Dashboard';
import JobList from './components/jobs/JobList';
import JobForm from './components/jobs/JobForm';
import JobDetail from './components/jobs/JobDetail';
import CandidateList from './components/candidates/CandidateList';
import CandidateForm from './components/candidates/CandidateForm';
import CandidateDetail from './components/candidates/CandidateDetail';
import Layout from './components/Layout';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Toaster position="top-right" />
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<SignUp />} />
            <Route path="/" element={
              <PrivateRoute>
                <Layout />
              </PrivateRoute>
            }>
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="jobs" element={<JobList />} />
              <Route path="jobs/new" element={<JobForm />} />
              <Route path="jobs/:id" element={<JobDetail />} />
              <Route path="jobs/:id/edit" element={<JobForm />} />
              <Route path="candidates" element={<CandidateList />} />
              <Route path="candidates/new" element={<CandidateForm />} />
              <Route path="candidates/:id" element={<CandidateDetail />} />
              <Route index element={<Navigate to="/dashboard" />} />
            </Route>
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;