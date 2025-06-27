import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../config/api';
import toast from 'react-hot-toast';
import { PlusIcon, EyeIcon, TrashIcon, UserGroupIcon, DocumentArrowDownIcon } from '@heroicons/react/24/outline';

const CandidateList = () => {
  const [candidates, setCandidates] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJobId, setSelectedJobId] = useState('all');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [candidatesResponse, jobsResponse] = await Promise.all([
        api.get('/api/candidates/'),
        api.get('/api/jobs/')
      ]);
      setCandidates(candidatesResponse.data);
      setJobs(jobsResponse.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to load candidates');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (candidateId) => {
    if (!window.confirm('Are you sure you want to delete this candidate?')) {
      return;
    }

    try {
      await api.delete(`/api/candidates/${candidateId}`);
      toast.success('Candidate deleted successfully');
      fetchData();
    } catch (error) {
      console.error('Error deleting candidate:', error);
      toast.error('Failed to delete candidate');
    }
  };

  const handleDownloadResume = async (candidateId, filename) => {
    try {
      const response = await api.get(`/api/candidates/${candidateId}/resume`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename || 'resume.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading resume:', error);
      toast.error('Failed to download resume');
    }
  };

  const handleDownloadQA = async (candidateId, filename) => {
    try {
      const response = await api.get(`/api/candidates/${candidateId}/qa-document`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename || 'interview_qa.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading Q&A document:', error);
      toast.error('Failed to download Q&A document');
    }
  };

  const filteredCandidates = selectedJobId === 'all' 
    ? candidates 
    : candidates.filter(c => c.job_id === parseInt(selectedJobId));

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Candidates</h1>
          <p className="mt-2 text-sm text-gray-700">
            A list of all candidates who have applied for positions.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <div className="flex items-center space-x-4">
            <select
              value={selectedJobId}
              onChange={(e) => setSelectedJobId(e.target.value)}
              className="block w-40 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
              <option value="all">All Jobs</option>
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  {job.job_name}
                </option>
              ))}
            </select>
            <Link
              to="/candidates/new"
              className="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 whitespace-nowrap"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Add Candidate
            </Link>
          </div>
        </div>
      </div>

      {filteredCandidates.length === 0 ? (
        <div className="mt-8 text-center">
          <UserGroupIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No candidates</h3>
          <p className="mt-1 text-sm text-gray-500">
            {selectedJobId === 'all' 
              ? 'Get started by adding a new candidate.'
              : 'No candidates found for the selected job.'}
          </p>
          <div className="mt-6">
            <Link
              to="/candidates/new"
              className="inline-flex items-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Add Candidate
            </Link>
          </div>
        </div>
      ) : (
        <div className="mt-8 flex flex-col">
          <div className="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
            <div className="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
              <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                <table className="min-w-full divide-y divide-gray-300">
                  <thead className="bg-gray-50">
                    <tr>
                      <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                        Name
                      </th>
                      <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                        Contact
                      </th>
                      <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                        Job
                      </th>
                      <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                        Scores
                      </th>
                      <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                        Documents
                      </th>
                      <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                        <span className="sr-only">Actions</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 bg-white">
                    {filteredCandidates.map((candidate) => {
                      const job = jobs.find(j => j.id === candidate.job_id);
                      const avgScore = candidate.skills_match_score 
                        ? ((candidate.skills_match_score + candidate.resume_relevancy_score + candidate.job_description_relevancy_score) / 3).toFixed(1)
                        : 'N/A';
                      
                      return (
                        <tr key={candidate.id}>
                          <td className="whitespace-nowrap px-3 py-4 text-sm">
                            <div className="font-medium text-gray-900">{candidate.name}</div>
                          </td>
                          <td className="px-3 py-4 text-sm text-gray-500">
                            <div>{candidate.email}</div>
                            <div>{candidate.phone}</div>
                          </td>
                          <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                            {job?.job_name || 'Unknown'}
                          </td>
                          <td className="px-3 py-4 text-sm text-gray-500">
                            {candidate.skills_match_score ? (
                              <div className="space-y-1">
                                <div className="text-xs">Skills: {candidate.skills_match_score.toFixed(1)}/10</div>
                                <div className="text-xs">Resume: {candidate.resume_relevancy_score.toFixed(1)}/10</div>
                                <div className="text-xs">Job Match: {candidate.job_description_relevancy_score.toFixed(1)}/10</div>
                                <div className="font-medium">Avg: {avgScore}/10</div>
                              </div>
                            ) : (
                              <span className="text-gray-400">Pending</span>
                            )}
                          </td>
                          <td className="px-3 py-4 text-sm">
                            <div className="flex space-x-2">
                              {candidate.resume_filename && (
                                <button
                                  onClick={() => handleDownloadResume(candidate.id, candidate.resume_filename)}
                                  className="text-indigo-600 hover:text-indigo-900"
                                  title="Download Resume"
                                >
                                  <DocumentArrowDownIcon className="h-5 w-5" />
                                </button>
                              )}
                              {candidate.qa_document_filename && (
                                <button
                                  onClick={() => handleDownloadQA(candidate.id, candidate.qa_document_filename)}
                                  className="text-green-600 hover:text-green-900"
                                  title="Download Q&A Document"
                                >
                                  <DocumentArrowDownIcon className="h-5 w-5" />
                                </button>
                              )}
                            </div>
                          </td>
                          <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                            <Link
                              to={`/candidates/${candidate.id}`}
                              className="text-indigo-600 hover:text-indigo-900 mr-4"
                            >
                              <EyeIcon className="h-4 w-4 inline" />
                            </Link>
                            <button
                              onClick={() => handleDelete(candidate.id)}
                              className="text-red-600 hover:text-red-900"
                            >
                              <TrashIcon className="h-4 w-4 inline" />
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CandidateList;