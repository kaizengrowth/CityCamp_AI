import React, { useState } from 'react';
import { apiRequest, API_ENDPOINTS } from '../config/api';
import toast from 'react-hot-toast';

interface Representative {
  name: string;
  position: string;
  email: string;
  district?: string;
  phone?: string;
}

interface EmailComposition {
  subject: string;
  body: string;
  tone: 'formal' | 'friendly' | 'urgent';
  representatives: Representative[];
}

export const ContactRepresentativesPage: React.FC = () => {
  const [address, setAddress] = useState('');
  const [issue, setIssue] = useState('');
  const [tone, setTone] = useState<'formal' | 'friendly' | 'urgent'>('friendly');
  const [emailComposition, setEmailComposition] = useState<EmailComposition | null>(null);
  const [loading, setLoading] = useState(false);
  const [representatives, setRepresentatives] = useState<Representative[]>([]);
  const [step, setStep] = useState<1 | 2 | 3>(1);

  // Sample representatives data (would normally come from API)
  const sampleRepresentatives: Representative[] = [
    {
      name: 'Monroe Nichols',
      position: 'Mayor',
      email: 'mayor@cityoftulsa.org',
      phone: '(918) 596-7777'
    },
    {
      name: 'Anthony Archie',
      position: 'City Councilor - District 2',
      email: 'dist2@tulsacouncil.org',
      district: 'District 2'
    }
  ];

  const handleAddressLookup = async () => {
    if (!address.trim()) {
      toast.error('Please enter your address');
      return;
    }

    setLoading(true);
    try {
      console.log('Looking up representatives for address:', address);

      const response = await apiRequest<{
        representatives: Representative[];
        address: string;
        district_info: {
          found: boolean;
          district?: string;
          coordinates?: { lat: number; lng: number };
          councilor?: any;
          error?: string;
          message?: string;
        };
      }>(`${API_ENDPOINTS.findRepresentatives}?address=${encodeURIComponent(address)}`);

      console.log('Representatives lookup result:', response);
      setRepresentatives(response.representatives);

      if (response.district_info.found) {
        toast.success(`Found representatives for ${response.district_info.district}!`);
      } else {
        toast.error(response.district_info.message || 'Using general representatives - consider verifying your address');
      }

    } catch (error) {
      console.error('Error finding representatives:', error);
      toast.error('Unable to find representatives for this address. Using general contacts.');
      // Fallback to sample data
      setRepresentatives(sampleRepresentatives);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateEmail = async () => {
    if (!issue.trim()) {
      toast.error('Please describe the issue you want to address');
      return;
    }

    if (representatives.length === 0) {
      toast.error('Please lookup your representatives first');
      return;
    }

    setLoading(true);
    try {
      const response = await apiRequest<EmailComposition>(API_ENDPOINTS.composeEmail, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          address,
          issue,
          tone,
          representatives
        }),
      });

      setEmailComposition(response);
      setStep(3);
      toast.success('Email composed successfully!');
    } catch (error) {
      console.error('Error composing email:', error);
      toast.error('Unable to compose email. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const openEmailClient = (rep: Representative) => {
    if (!emailComposition) return;

    const subject = encodeURIComponent(emailComposition.subject);
    const body = encodeURIComponent(emailComposition.body);
    const mailtoUrl = `mailto:${rep.email}?subject=${subject}&body=${body}`;

    window.open(mailtoUrl, '_blank');
  };

  return (
    <div className="space-y-8">
      {/* Progress Steps */}
      <div className="flex items-center justify-center space-x-4">
        {[1, 2, 3].map((stepNumber) => (
          <div key={stepNumber} className="flex items-center">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step >= stepNumber
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-600'
              }`}
            >
              {stepNumber}
            </div>
            {stepNumber < 3 && (
              <div
                className={`w-12 h-1 ${
                  step > stepNumber ? 'bg-primary-600' : 'bg-gray-200'
                }`}
              />
            )}
          </div>
        ))}
      </div>

      {/* Step 1: Find Representatives */}
      {step >= 1 && (
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <span className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
              1
            </span>
            Find Your Representatives
          </h2>

          <div className="space-y-4">
            <div>
              <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-2">
                Your Tulsa Address
              </label>
              <div className="flex space-x-3">
                <input
                  type="text"
                  id="address"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="e.g., 123 Main Street, Tulsa, OK 74103"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <button
                  onClick={handleAddressLookup}
                  disabled={loading}
                  className="btn btn-primary px-6 py-2 disabled:opacity-50"
                >
                  {loading ? 'Looking up...' : 'Find Representatives'}
                </button>
              </div>
            </div>

            {/* District Finder Link */}
            <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-blue-800 text-sm">
                💡 <strong>Need more accurate results?</strong> Use our{' '}
                <a href="/contact-representatives/find-district" className="text-blue-600 hover:text-blue-800 underline font-medium">
                  District Finder tool
                </a>{' '}
                to get precise district mapping and representative contact information.
              </p>
            </div>
          </div>

          {representatives.length > 0 && (
            <div className="mt-6">
              <h3 className="font-medium text-gray-900 mb-3">Your Representatives:</h3>
              <div className="grid gap-3">
                {representatives.map((rep, index) => (
                  <div key={index} className="bg-gray-50 p-4 rounded-lg border">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-medium text-gray-900">{rep.name}</h4>
                        <p className="text-sm text-gray-600">{rep.position}</p>
                      </div>
                      <div className="text-right text-sm text-gray-600">
                        <p>{rep.email}</p>
                        {rep.phone && <p>{rep.phone}</p>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <button
                onClick={() => setStep(2)}
                className="mt-4 btn btn-primary"
              >
                Continue to Compose Email
              </button>
            </div>
          )}
        </div>
      )}

      {/* Step 2: Describe Your Concern */}
      {step >= 2 && (
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <span className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
              2
            </span>
            Describe Your Concern
          </h2>

          <div className="space-y-4">
            <div>
              <label htmlFor="issue" className="block text-sm font-medium text-gray-700 mb-2">
                What issue would you like to address?
              </label>
              <textarea
                id="issue"
                value={issue}
                onChange={(e) => setIssue(e.target.value)}
                rows={5}
                placeholder="Describe the issue in detail. Include specific locations, dates, and how it affects you or your community..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">Email Tone</label>
              <div className="flex space-x-4">
                {[
                  { value: 'friendly', label: 'Friendly', desc: 'Conversational and approachable' },
                  { value: 'formal', label: 'Formal', desc: 'Professional and respectful' },
                  { value: 'urgent', label: 'Urgent', desc: 'Serious and requiring immediate attention' }
                ].map((option) => (
                  <label key={option.value} className="flex-1 cursor-pointer">
                    <input
                      type="radio"
                      name="tone"
                      value={option.value}
                      checked={tone === option.value}
                      onChange={(e) => setTone(e.target.value as 'formal' | 'friendly' | 'urgent')}
                      className="sr-only"
                    />
                    <div className={`p-4 rounded-lg border-2 transition-colors ${
                      tone === option.value
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}>
                      <h4 className="font-medium text-gray-900">{option.label}</h4>
                      <p className="text-sm text-gray-600">{option.desc}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <button
              onClick={handleGenerateEmail}
              disabled={loading || !issue.trim() || representatives.length === 0}
              className="btn btn-primary btn-lg w-full disabled:opacity-50"
            >
              {loading ? 'Generating Email...' : '✨ Generate AI-Powered Email'}
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Email Preview */}
      {emailComposition && step >= 3 && (
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <span className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
              3
            </span>
            Your Generated Email
          </h2>

          <div className="space-y-4">
            <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
              <div className="mb-4">
                <h4 className="font-medium text-gray-900 mb-2">Subject:</h4>
                <p className="text-gray-700 font-medium">{emailComposition.subject}</p>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-2">Message:</h4>
                <pre className="whitespace-pre-wrap text-gray-700 text-sm leading-relaxed">
                  {emailComposition.body}
                </pre>
              </div>
            </div>

            <div className="flex flex-col space-y-3">
              <div className="flex space-x-3">
                <button
                  onClick={() => copyToClipboard(`Subject: ${emailComposition.subject}\n\n${emailComposition.body}`)}
                  className="btn btn-outline flex-1"
                >
                  📋 Copy to Clipboard
                </button>
                <button
                  onClick={handleGenerateEmail}
                  disabled={loading}
                  className="btn btn-outline"
                >
                  🔄 Regenerate
                </button>
              </div>

              <div className="space-y-2">
                <h4 className="font-medium text-gray-900">Send to:</h4>
                {representatives.map((rep, index) => (
                  <button
                    key={index}
                    onClick={() => openEmailClient(rep)}
                    className="w-full p-3 text-left bg-primary-50 hover:bg-primary-100 rounded-lg border border-primary-200 transition-colors"
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <h5 className="font-medium text-primary-900">{rep.name}</h5>
                        <p className="text-sm text-primary-700">{rep.position}</p>
                      </div>
                      <div className="text-primary-600">
                        ✉️ Send Email
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tips Section */}
      <div className="bg-blue-50 rounded-xl p-6 border border-blue-200">
        <h3 className="text-xl font-semibold text-blue-900 mb-4">💡 Tips for Effective Communication</h3>
        <ul className="space-y-2 text-blue-800">
          <li className="flex items-start space-x-2">
            <span className="text-blue-600 font-bold">•</span>
            <span>Be specific about your concern and include relevant details</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-600 font-bold">•</span>
            <span>Mention how the issue affects you personally or your community</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-600 font-bold">•</span>
            <span>Suggest potential solutions or ask for specific actions</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-600 font-bold">•</span>
            <span>Include your contact information for follow-up</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-600 font-bold">•</span>
            <span>Follow up if you don't receive a response within 2-3 weeks</span>
          </li>
        </ul>
      </div>
    </div>
  );
};
