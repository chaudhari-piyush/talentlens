import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '../../config/api';
import toast from 'react-hot-toast';
import { DocumentArrowUpIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

const CandidateForm = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const preselectedJobId = queryParams.get('job_id');

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    job_id: preselectedJobId || ''
  });
  const [resumeFile, setResumeFile] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processingStage, setProcessingStage] = useState('');

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      setFetching(true);
      const response = await api.get('/api/jobs/');
      setJobs(response.data);
    } catch (error) {
      console.error('Error fetching jobs:', error);
      toast.error('Failed to load jobs');
    } finally {
      setFetching(false);
    }
  };

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        toast.error('Please upload a PDF file');
        e.target.value = '';
        return;
      }
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        toast.error('File size must be less than 10MB');
        e.target.value = '';
        return;
      }
      setResumeFile(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!resumeFile) {
      toast.error('Please upload a resume');
      return;
    }

    setLoading(true);
    setUploadProgress(0);
    setProcessingStage('Uploading resume...');
    
    try {
      const submitData = new FormData();
      submitData.append('name', formData.name);
      submitData.append('email', formData.email);
      submitData.append('phone', formData.phone);
      submitData.append('job_id', formData.job_id);
      submitData.append('resume', resumeFile);

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const response = await api.post('/api/candidates/', submitData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      clearInterval(progressInterval);
      setUploadProgress(100);
      setProcessingStage('Analyzing resume with AI...');

      // Wait a bit to show the completion
      await new Promise(resolve => setTimeout(resolve, 1000));

      toast.success('Candidate created successfully! Resume analysis has started.');
      navigate('/candidates');
    } catch (error) {
      console.error('Error creating candidate:', error);
      toast.error(error.response?.data?.detail || 'Failed to create candidate');
      setLoading(false);
      setUploadProgress(0);
      setProcessingStage('');
    }
  };

  if (fetching) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium leading-6 text-gray-900">
            Add New Candidate
          </h3>
          <div className="mt-2 max-w-xl text-sm text-gray-500">
            <p>Fill in the candidate details and upload their resume. The system will automatically analyze the resume and generate interview questions.</p>
          </div>

          <form onSubmit={handleSubmit} className="mt-5 space-y-6">
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div className="sm:col-span-2">
                <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                  Full Name
                </label>
                <input
                  type="text"
                  name="name"
                  id="name"
                  required
                  value={formData.name}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  placeholder="John Doe"
                />
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  id="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  placeholder="john.doe@example.com"
                />
              </div>

              <div>
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                  Phone Number
                </label>
                <input
                  type="tel"
                  name="phone"
                  id="phone"
                  required
                  value={formData.phone}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  placeholder="+1 (555) 123-4567"
                />
              </div>

              <div className="sm:col-span-2">
                <label htmlFor="job_id" className="block text-sm font-medium text-gray-700">
                  Job Position
                </label>
                <select
                  name="job_id"
                  id="job_id"
                  required
                  value={formData.job_id}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                >
                  <option value="">Select a job position</option>
                  {jobs.map((job) => (
                    <option key={job.id} value={job.id}>
                      {job.job_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="sm:col-span-2">
                <label htmlFor="resume" className="block text-sm font-medium text-gray-700">
                  Resume (PDF)
                </label>
                <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                  <div className="space-y-1 text-center">
                    <DocumentArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
                    <div className="flex text-sm text-gray-600">
                      <label
                        htmlFor="resume"
                        className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500"
                      >
                        <span>Upload a file</span>
                        <input
                          id="resume"
                          name="resume"
                          type="file"
                          className="sr-only"
                          accept=".pdf"
                          onChange={handleFileChange}
                          required
                        />
                      </label>
                      <p className="pl-1">or drag and drop</p>
                    </div>
                    <p className="text-xs text-gray-500">PDF up to 10MB</p>
                    {resumeFile && (
                      <p className="text-sm text-gray-900 mt-2">
                        Selected: {resumeFile.name}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => navigate('/candidates')}
                className="rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Creating...' : 'Create Candidate'}
              </button>
            </div>
          </form>

          {/* Progress Modal */}
          {loading && (
            <div className="fixed inset-0 z-50 overflow-y-auto">
              <div className="flex min-h-full items-center justify-center p-4 text-center">
                <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
                
                <div className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-sm sm:p-6">
                  <div>
                    <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100">
                      {uploadProgress === 100 ? (
                        <CheckCircleIcon className="h-6 w-6 text-indigo-600" />
                      ) : (
                        <DocumentArrowUpIcon className="h-6 w-6 text-indigo-600" />
                      )}
                    </div>
                    <div className="mt-3 text-center sm:mt-5">
                      <h3 className="text-lg font-medium leading-6 text-gray-900">
                        Processing Candidate
                      </h3>
                      <div className="mt-2">
                        <p className="text-sm text-gray-500">{processingStage}</p>
                      </div>
                    </div>
                  </div>
                  
                  {/* Progress Bar */}
                  <div className="mt-6">
                    <div className="relative pt-1">
                      <div className="mb-2 flex items-center justify-between">
                        <div>
                          <span className="inline-block py-1 px-2 text-xs font-semibold uppercase text-indigo-600">
                            Progress
                          </span>
                        </div>
                        <div className="text-right">
                          <span className="inline-block text-xs font-semibold text-indigo-600">
                            {uploadProgress}%
                          </span>
                        </div>
                      </div>
                      <div className="mb-4 flex h-2 overflow-hidden rounded bg-indigo-100 text-xs">
                        <div
                          style={{ width: `${uploadProgress}%` }}
                          className="flex flex-col justify-center whitespace-nowrap bg-indigo-600 text-center text-white shadow-none transition-all duration-500"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Processing Steps */}
                  <div className="mt-4">
                    <ul className="space-y-2 text-sm">
                      <li className={`flex items-center ${uploadProgress >= 33 ? 'text-indigo-600' : 'text-gray-400'}`}>
                        <CheckCircleIcon className={`mr-2 h-4 w-4 ${uploadProgress >= 33 ? 'text-indigo-600' : 'text-gray-300'}`} />
                        Uploading resume
                      </li>
                      <li className={`flex items-center ${uploadProgress >= 66 ? 'text-indigo-600' : 'text-gray-400'}`}>
                        <CheckCircleIcon className={`mr-2 h-4 w-4 ${uploadProgress >= 66 ? 'text-indigo-600' : 'text-gray-300'}`} />
                        Extracting text from PDF
                      </li>
                      <li className={`flex items-center ${uploadProgress >= 100 ? 'text-indigo-600' : 'text-gray-400'}`}>
                        <CheckCircleIcon className={`mr-2 h-4 w-4 ${uploadProgress >= 100 ? 'text-indigo-600' : 'text-gray-300'}`} />
                        AI analysis in progress
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CandidateForm;