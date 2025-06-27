import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../config/api';
import toast from 'react-hot-toast';
import { BriefcaseIcon, UserGroupIcon, PlusIcon } from '@heroicons/react/24/outline';

const Dashboard = () => {
  const { userProfile } = useAuth();
  const [jobs, setJobs] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalJobs: 0,
    totalCandidates: 0,
    averageScore: 0
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [jobsResponse, candidatesResponse] = await Promise.all([
        api.get('/api/jobs/'),
        api.get('/api/candidates/')
      ]);

      setJobs(jobsResponse.data);
      setCandidates(candidatesResponse.data);

      // Calculate stats
      const totalCandidates = candidatesResponse.data.length;
      const averageScore = totalCandidates > 0
        ? candidatesResponse.data.reduce((acc, candidate) => {
            const score = (candidate.skills_match_score || 0) + 
                         (candidate.resume_relevancy_score || 0) + 
                         (candidate.job_description_relevancy_score || 0);
            return acc + score / 3;
          }, 0) / totalCandidates
        : 0;

      setStats({
        totalJobs: jobsResponse.data.length,
        totalCandidates,
        averageScore: averageScore.toFixed(1)
      });
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {userProfile?.email}!
        </h1>
        <p className="mt-2 text-gray-600">
          Here's an overview of your recruitment pipeline
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-indigo-500 rounded-md p-3">
              <BriefcaseIcon className="h-6 w-6 text-white" />
            </div>
            <div className="ml-5">
              <p className="text-sm font-medium text-gray-500">Total Jobs</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.totalJobs}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-green-500 rounded-md p-3">
              <UserGroupIcon className="h-6 w-6 text-white" />
            </div>
            <div className="ml-5">
              <p className="text-sm font-medium text-gray-500">Total Candidates</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.totalCandidates}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-yellow-500 rounded-md p-3">
              <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div className="ml-5">
              <p className="text-sm font-medium text-gray-500">Average Score</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.averageScore}/10</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Jobs */}
      <div className="bg-white shadow rounded-lg mb-8">
        <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
          <h2 className="text-lg font-medium text-gray-900">Recent Jobs</h2>
          <Link
            to="/jobs/new"
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <PlusIcon className="h-4 w-4 mr-1" />
            New Job
          </Link>
        </div>
        <div className="border-t border-gray-200">
          {jobs.length === 0 ? (
            <div className="px-4 py-8 text-center text-gray-500">
              No jobs posted yet. <Link to="/jobs/new" className="text-indigo-600 hover:text-indigo-500">Create your first job</Link>
            </div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {jobs.slice(0, 5).map((job) => (
                <li key={job.id} className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                  <Link to={`/jobs/${job.id}`} className="block">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-indigo-600 truncate">
                          {job.job_name}
                        </p>
                        <p className="mt-1 text-sm text-gray-500">
                          {job.expected_skills.slice(0, 3).join(', ')}
                          {job.expected_skills.length > 3 && '...'}
                        </p>
                      </div>
                      <div className="ml-2 flex-shrink-0 flex">
                        <p className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          Active
                        </p>
                      </div>
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}
          {jobs.length > 5 && (
            <div className="bg-gray-50 px-4 py-3 sm:px-6">
              <Link to="/jobs" className="text-sm text-indigo-600 hover:text-indigo-500">
                View all jobs →
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Recent Candidates */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
          <h2 className="text-lg font-medium text-gray-900">Recent Candidates</h2>
          <Link
            to="/candidates/new"
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <PlusIcon className="h-4 w-4 mr-1" />
            Add Candidate
          </Link>
        </div>
        <div className="border-t border-gray-200">
          {candidates.length === 0 ? (
            <div className="px-4 py-8 text-center text-gray-500">
              No candidates added yet. <Link to="/candidates/new" className="text-indigo-600 hover:text-indigo-500">Add your first candidate</Link>
            </div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {candidates.slice(0, 5).map((candidate) => (
                <li key={candidate.id} className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                  <Link to={`/candidates/${candidate.id}`} className="block">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-indigo-600 truncate">
                          {candidate.name}
                        </p>
                        <p className="mt-1 text-sm text-gray-500">
                          {candidate.email} • Applied for: {jobs.find(j => j.id === candidate.job_id)?.job_name || 'Unknown'}
                        </p>
                      </div>
                      <div className="ml-2 flex-shrink-0">
                        {candidate.skills_match_score && (
                          <p className="text-sm text-gray-900">
                            Score: {((candidate.skills_match_score + candidate.resume_relevancy_score + candidate.job_description_relevancy_score) / 3).toFixed(1)}/10
                          </p>
                        )}
                      </div>
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}
          {candidates.length > 5 && (
            <div className="bg-gray-50 px-4 py-3 sm:px-6">
              <Link to="/candidates" className="text-sm text-indigo-600 hover:text-indigo-500">
                View all candidates →
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;