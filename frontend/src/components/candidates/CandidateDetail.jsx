import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../config/api';
import toast from 'react-hot-toast';
import { 
  TrashIcon, 
  DocumentArrowDownIcon, 
  EnvelopeIcon, 
  PhoneIcon,
  BriefcaseIcon,
  ChartBarIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

const CandidateDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [candidate, setCandidate] = useState(null);
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCandidateDetails();
  }, [id]);

  const fetchCandidateDetails = async () => {
    try {
      setLoading(true);
      const candidateResponse = await api.get(`/api/candidates/${id}`);
      const candidateData = candidateResponse.data;
      setCandidate(candidateData);

      // Fetch job details
      if (candidateData.job_id) {
        const jobResponse = await api.get(`/api/jobs/${candidateData.job_id}`);
        setJob(jobResponse.data);
      }
    } catch (error) {
      console.error('Error fetching candidate details:', error);
      toast.error('Failed to load candidate details');
      navigate('/candidates');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this candidate?')) {
      return;
    }

    try {
      await api.delete(`/api/candidates/${id}`);
      toast.success('Candidate deleted successfully');
      navigate('/candidates');
    } catch (error) {
      console.error('Error deleting candidate:', error);
      toast.error('Failed to delete candidate');
    }
  };

  const handleDownloadResume = async () => {
    try {
      const response = await api.get(`/api/candidates/${id}/resume`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', candidate.resume_filename || 'resume.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading resume:', error);
      toast.error('Failed to download resume');
    }
  };

  const handleDownloadQA = async () => {
    try {
      const response = await api.get(`/api/candidates/${id}/qa-document`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', candidate.qa_document_filename || 'interview_qa.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading Q&A document:', error);
      toast.error('Failed to download Q&A document');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!candidate) {
    return null;
  }

  const averageScore = candidate.skills_match_score 
    ? ((candidate.skills_match_score + candidate.resume_relevancy_score + candidate.job_description_relevancy_score) / 3).toFixed(1)
    : null;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Candidate Header */}
      <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
        <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
          <div>
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              {candidate.name}
            </h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              Candidate ID: {candidate.id}
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleDelete}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              <TrashIcon className="h-4 w-4 mr-2" />
              Delete
            </button>
          </div>
        </div>

        {/* Basic Information */}
        <div className="border-t border-gray-200">
          <dl>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500 flex items-center">
                <EnvelopeIcon className="h-4 w-4 mr-2" />
                Email
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <a href={`mailto:${candidate.email}`} className="text-indigo-600 hover:text-indigo-500">
                  {candidate.email}
                </a>
              </dd>
            </div>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500 flex items-center">
                <PhoneIcon className="h-4 w-4 mr-2" />
                Phone
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <a href={`tel:${candidate.phone}`} className="text-indigo-600 hover:text-indigo-500">
                  {candidate.phone}
                </a>
              </dd>
            </div>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500 flex items-center">
                <BriefcaseIcon className="h-4 w-4 mr-2" />
                Applied Position
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {job?.job_name || 'Unknown Position'}
              </dd>
            </div>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500 flex items-center">
                <ClockIcon className="h-4 w-4 mr-2" />
                Applied Date
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {candidate.created_at ? new Date(candidate.created_at).toLocaleString() : 'N/A'}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      {/* Scores Section */}
      {candidate.skills_match_score && (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 flex items-center">
              <ChartBarIcon className="h-5 w-5 mr-2" />
              Assessment Scores
            </h3>
          </div>
          <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div className="bg-gray-50 rounded-lg p-4">
                <dt className="text-sm font-medium text-gray-500">Skills Match</dt>
                <dd className="mt-1 text-3xl font-semibold text-indigo-600">
                  {candidate.skills_match_score.toFixed(1)}/10
                </dd>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <dt className="text-sm font-medium text-gray-500">Resume Relevancy</dt>
                <dd className="mt-1 text-3xl font-semibold text-indigo-600">
                  {candidate.resume_relevancy_score.toFixed(1)}/10
                </dd>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <dt className="text-sm font-medium text-gray-500">Job Description Match</dt>
                <dd className="mt-1 text-3xl font-semibold text-indigo-600">
                  {candidate.job_description_relevancy_score.toFixed(1)}/10
                </dd>
              </div>
            </div>
            <div className="mt-4 bg-indigo-50 rounded-lg p-4 text-center">
              <dt className="text-sm font-medium text-gray-500">Overall Score</dt>
              <dd className="mt-1 text-4xl font-bold text-indigo-700">
                {averageScore}/10
              </dd>
            </div>
          </div>
        </div>
      )}

      {/* Documents Section */}
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Documents
          </h3>
        </div>
        <div className="border-t border-gray-200">
          <ul className="divide-y divide-gray-200">
            {candidate.resume_filename && (
              <li className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <DocumentArrowDownIcon className="h-5 w-5 text-gray-400 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Resume</p>
                      <p className="text-sm text-gray-500">{candidate.resume_filename}</p>
                    </div>
                  </div>
                  <button
                    onClick={handleDownloadResume}
                    className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Download
                  </button>
                </div>
              </li>
            )}
            {candidate.qa_document_filename && (
              <li className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <DocumentArrowDownIcon className="h-5 w-5 text-gray-400 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Interview Q&A Document</p>
                      <p className="text-sm text-gray-500">{candidate.qa_document_filename}</p>
                    </div>
                  </div>
                  <button
                    onClick={handleDownloadQA}
                    className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Download
                  </button>
                </div>
              </li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default CandidateDetail;