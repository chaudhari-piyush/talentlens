import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../../config/api';
import toast from 'react-hot-toast';
import { PencilIcon, TrashIcon, UserPlusIcon, DocumentTextIcon } from '@heroicons/react/24/outline';

const JobDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJobDetails();
  }, [id]);

  const fetchJobDetails = async () => {
    try {
      setLoading(true);
      const [jobResponse, candidatesResponse] = await Promise.all([
        api.get(`/api/jobs/${id}`),
        api.get('/api/candidates/')
      ]);
      
      setJob(jobResponse.data);
      // Filter candidates for this job
      const jobCandidates = candidatesResponse.data.filter(c => c.job_id === parseInt(id));
      setCandidates(jobCandidates);
    } catch (error) {
      console.error('Error fetching job details:', error);
      toast.error('Failed to load job details');
      navigate('/jobs');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this job? This will also delete all associated candidates.')) {
      return;
    }

    try {
      await api.delete(`/api/jobs/${id}`);
      toast.success('Job deleted successfully');
      navigate('/jobs');
    } catch (error) {
      console.error('Error deleting job:', error);
      toast.error('Failed to delete job');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!job) {
    return null;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Job Header */}
      <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
        <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
          <div>
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              {job.job_name}
            </h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              Job ID: {job.id}
            </p>
          </div>
          <div className="flex space-x-3">
            <Link
              to={`/jobs/${id}/edit`}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              <PencilIcon className="h-4 w-4 mr-2" />
              Edit
            </Link>
            <button
              onClick={handleDelete}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              <TrashIcon className="h-4 w-4 mr-2" />
              Delete
            </button>
          </div>
        </div>
        <div className="border-t border-gray-200">
          <dl>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Created Date</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {job.created_at ? new Date(job.created_at).toLocaleString() : 'N/A'}
              </dd>
            </div>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Expected Skills</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="flex flex-wrap gap-2">
                  {job.expected_skills.map((skill, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center rounded-full bg-indigo-100 px-3 py-1 text-sm font-medium text-indigo-700"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </dd>
            </div>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Job Description</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2 whitespace-pre-wrap">
                {job.job_description}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      {/* Candidates Section */}
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
          <div>
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Candidates ({candidates.length})
            </h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              All candidates who have applied for this position
            </p>
          </div>
          <Link
            to={`/candidates/new?job_id=${id}`}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <UserPlusIcon className="h-4 w-4 mr-2" />
            Add Candidate
          </Link>
        </div>
        <div className="border-t border-gray-200">
          {candidates.length === 0 ? (
            <div className="px-4 py-8 text-center text-gray-500">
              No candidates have applied for this job yet.
            </div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {candidates.map((candidate) => (
                <li key={candidate.id} className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                  <Link to={`/candidates/${candidate.id}`} className="block">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center">
                          <p className="text-sm font-medium text-indigo-600 truncate">
                            {candidate.name}
                          </p>
                          {candidate.qa_document_filename && (
                            <DocumentTextIcon className="ml-2 h-4 w-4 text-gray-400" title="Q&A Document Available" />
                          )}
                        </div>
                        <p className="mt-1 text-sm text-gray-500">
                          {candidate.email} • {candidate.phone}
                        </p>
                        {candidate.skills_match_score && (
                          <div className="mt-2 flex items-center text-sm text-gray-500">
                            <span className="font-medium">Scores:</span>
                            <span className="ml-2">
                              Skills: {candidate.skills_match_score?.toFixed(1)}/10
                            </span>
                            <span className="ml-2">
                              Resume: {candidate.resume_relevancy_score?.toFixed(1)}/10
                            </span>
                            <span className="ml-2">
                              Job Match: {candidate.job_description_relevancy_score?.toFixed(1)}/10
                            </span>
                          </div>
                        )}
                      </div>
                      <div className="ml-4 flex-shrink-0">
                        <span className="text-sm text-gray-500">
                          Average: {((candidate.skills_match_score + candidate.resume_relevancy_score + candidate.job_description_relevancy_score) / 3).toFixed(1)}/10
                        </span>
                      </div>
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default JobDetail;