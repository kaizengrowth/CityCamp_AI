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
  const [tone, setTone] = useState<'formal' | 'friendly' | 'urgent'>('formal');
  const [representatives, setRepresentatives] = useState<Representative[]>([]);
  const [emailComposition, setEmailComposition] = useState<EmailComposition | null>(null);
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

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
          councilor?: Representative;
          error?: string;
          message?: string;
        };
      }>(`${API_ENDPOINTS.findRepresentatives}?address=${encodeURIComponent(address)}`);

      console.log('Representatives lookup result:', response);
      setRepresentatives(response.representatives);

      if (response.district_info.found) {
        toast.success(`Found representatives for ${response.district_info.district}!`);
      } else {
        if (response.representatives.length === 0) {
          toast.error('No representatives found for this address. Please verify your address is within Tulsa city limits.');
        } else {
          toast.error(response.district_info.message || 'Address lookup incomplete - please verify your address');
        }
      }

    } catch (error) {
      console.error('Error finding representatives:', error);
      toast.error('Unable to find representatives for this address. Please try again.');
      // Clear representatives instead of using fallback data
      setRepresentatives([]);
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
                  ? 'bg-brand-red text-white'
                  : 'bg-gray-200 text-gray-600'
              }`}
            >
              {stepNumber}
            </div>
            {stepNumber < 3 && (
              <div
                className={`w-12 h-1 ${
                  step > stepNumber ? 'bg-brand-red' : 'bg-gray-200'
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
            <span className="w-8 h-8 bg-brand-red text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
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
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-dark-blue focus:border-transparent"
                />
                <button
                  onClick={handleAddressLookup}
                  disabled={loading}
                  className="px-4 py-2 bg-brand-dark-blue text-white font-medium rounded-lg hover:bg-brand-red hover:text-white transition-colors disabled:opacity-50 text-sm"
                >
                  {loading ? 'Looking up...' : 'Find Representatives'}
                </button>
              </div>
            </div>

            {/* District Finder Link */}
            <div className="p-3 bg-[#fdf8f3] rounded-lg border border-gray-200">
              <p className="text-brand-dark-blue text-sm">
                💡 <strong>Need more accurate results?</strong> Use our{' '}
                <a href="/contact-representatives/find-district" className="text-brand-dark-blue hover:text-brand-red underline font-medium">
                  District Finder tool
                </a>{' '}
                to get precise district mapping and representative contact information.
              </p>
            </div>
          </div>

          {representatives.length > 0 && (
            <div className="mt-6">
              <div className="text-sm font-medium text-brand-dark-blue mb-3">Your Representatives</div>
              <div className="grid gap-3">
                {representatives.map((rep, index) => (
                  <div key={index} className="bg-gray-50 p-4 rounded-lg border">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-medium text-brand-dark-blue">{rep.name}</h4>
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
              <div className="mt-4 flex justify-end">
                <button
                  onClick={() => setStep(2)}
                  className="px-6 py-2 bg-brand-dark-blue text-white font-semibold rounded-lg hover:bg-brand-red hover:text-white transition-colors"
                >
                  Continue
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Step 2: Describe Your Concern */}
      {step >= 2 && (
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <span className="w-8 h-8 bg-brand-red text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
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
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-dark-blue focus:border-transparent resize-none"
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
                        ? 'border-brand-dark-blue bg-[#fdf8f3]'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}>
                      <h4 className="font-medium text-brand-dark-blue">{option.label}</h4>
                      <p className="text-sm text-gray-600">{option.desc}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <button
              onClick={handleGenerateEmail}
              disabled={loading || !issue.trim() || representatives.length === 0}
              className="px-8 py-3 w-full bg-brand-dark-blue text-white font-semibold rounded-lg hover:bg-brand-red hover:text-white transition-colors disabled:opacity-50"
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
            <span className="w-8 h-8 bg-brand-red text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
              3
            </span>
            Your Generated Email
          </h2>

          <div className="space-y-4">
            <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
              <div className="mb-4">
                <h4 className="font-medium text-brand-dark-blue mb-2">Subject:</h4>
                <p className="text-gray-700 font-medium">{emailComposition.subject}</p>
              </div>

              <div>
                <h4 className="font-medium text-brand-dark-blue mb-2">Message:</h4>
                <pre className="whitespace-pre-wrap text-gray-700 text-sm leading-relaxed">
                  {emailComposition.body}
                </pre>
              </div>
            </div>

            <div className="flex flex-col space-y-3">
              <div className="flex space-x-3">
                <button
                  onClick={() => copyToClipboard(`Subject: ${emailComposition.subject}\n\n${emailComposition.body}`)}
                  className="px-6 py-2 border-2 border-brand-dark-blue text-brand-dark-blue font-semibold rounded-lg hover:bg-button-hover-bg hover:text-brand-red hover:border-brand-red transition-colors flex-1"
                >
                  📋 Copy to Clipboard
                </button>
                <button
                  onClick={handleGenerateEmail}
                  disabled={loading}
                  className="px-6 py-2 border-2 border-brand-dark-blue text-brand-dark-blue font-semibold rounded-lg hover:bg-button-hover-bg hover:text-brand-red hover:border-brand-red transition-colors disabled:opacity-50"
                >
                  🔄 Regenerate
                </button>
              </div>

              <div className="space-y-2">
                <h4 className="font-medium text-brand-dark-blue">Send to:</h4>
                {representatives.map((rep, index) => (
                  <button
                    key={index}
                    onClick={() => openEmailClient(rep)}
                    className="w-full p-3 text-left bg-[#fdf8f3] hover:bg-button-hover-bg rounded-lg border border-gray-200 hover:border-brand-dark-blue transition-colors"
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <h5 className="font-medium text-brand-dark-blue">{rep.name}</h5>
                        <p className="text-sm text-gray-700">{rep.position}</p>
                      </div>
                      <div className="text-brand-dark-blue">
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
        <h3 className="text-xl font-semibold text-blue-900 mb-4"> Tips for Effective Communication</h3>
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
