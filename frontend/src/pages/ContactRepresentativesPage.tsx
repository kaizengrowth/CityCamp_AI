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

  // Sample representatives data (would normally come from API)
  const sampleRepresentatives: Representative[] = [
    {
      name: 'G.T. Bynum',
      position: 'Mayor',
      email: 'mayor@cityoftulsa.org',
      phone: '(918) 596-7777'
    },
    {
      name: 'Vanessa Hall-Harper',
      position: 'City Councilor - District 1',
      email: 'vhall-harper@cityoftulsa.org',
      district: 'District 1'
    },
    {
      name: 'Jeannie Cue',
      position: 'City Councilor - District 2',
      email: 'jcue@cityoftulsa.org',
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
      // In a real implementation, this would call an API to determine representatives based on address
      // For now, we'll use sample data
      setRepresentatives(sampleRepresentatives);
      toast.success('Representatives found for your area');
    } catch (error) {
      console.error('Error finding representatives:', error);
      toast.error('Unable to find representatives for this address');
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
      toast.success('Email composition generated!');
    } catch (error) {
      console.error('Error generating email:', error);

      // Fallback to local generation if API is not available
      const fallbackEmail: EmailComposition = {
        subject: generateSubject(issue, tone),
        body: generateEmailBody(issue, tone, representatives[0]),
        tone,
        representatives
      };

      setEmailComposition(fallbackEmail);
      toast.success('Email composition generated (offline mode)');
    } finally {
      setLoading(false);
    }
  };

  const generateSubject = (issue: string, tone: 'formal' | 'friendly' | 'urgent'): string => {
    const keywords = issue.toLowerCase();
    let subject = '';

    if (tone === 'urgent') {
      subject = 'URGENT: ';
    }

    if (keywords.includes('pothole') || keywords.includes('road')) {
      subject += 'Road Maintenance Concern';
    } else if (keywords.includes('park') || keywords.includes('recreation')) {
      subject += 'Parks and Recreation Matter';
    } else if (keywords.includes('traffic') || keywords.includes('light')) {
      subject += 'Traffic Safety Issue';
    } else if (keywords.includes('budget') || keywords.includes('tax')) {
      subject += 'Budget and Taxation Concern';
    } else {
      subject += 'Community Concern from Constituent';
    }

    return subject;
  };

  const generateEmailBody = (issue: string, tone: 'formal' | 'friendly' | 'urgent', rep: Representative): string => {
    const greeting = tone === 'formal' ?
      `Dear ${rep.position} ${rep.name.split(' ').slice(-1)[0]},` :
      `Hello ${rep.name.split(' ')[0]},`;

    const intro = tone === 'formal' ?
      'I am writing to bring to your attention an important matter affecting our community.' :
      tone === 'urgent' ?
      'I am reaching out regarding an urgent matter that requires immediate attention.' :
      'I hope this message finds you well. I wanted to share a concern that affects our neighborhood.';

    const body = `${greeting}\n\n${intro}\n\n${issue}\n\nI would appreciate your consideration of this matter and any action you might be able to take to address this concern. As a constituent, I value your leadership and commitment to improving our community.\n\nThank you for your time and service to Tulsa.`;

    const closing = tone === 'formal' ?
      'Respectfully,' :
      'Best regards,';

    return `${body}\n\n${closing}\n[Your Name]\n[Your Address]\n[Your Phone Number]\n[Your Email]`;
  };

  const copyEmailToClipboard = () => {
    if (!emailComposition) return;

    const emailText = `Subject: ${emailComposition.subject}\n\n${emailComposition.body}`;
    navigator.clipboard.writeText(emailText);
    toast.success('Email copied to clipboard!');
  };

  const openEmailClient = (rep: Representative) => {
    if (!emailComposition) return;

    const subject = encodeURIComponent(emailComposition.subject);
    const body = encodeURIComponent(emailComposition.body);
    const mailtoLink = `mailto:${rep.email}?subject=${subject}&body=${body}`;

    window.open(mailtoLink, '_blank');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-gray-900">Contact Your Representatives</h1>
        <p className="text-xl text-gray-600">
          AI-powered email composition to help you effectively communicate with your elected officials
        </p>
      </div>

      {/* Step 1: Address Lookup */}
      <div className="bg-white rounded-xl p-8 shadow-sm">
        <h2 className="text-2xl font-semibold mb-6 flex items-center">
          <span className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">1</span>
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
        </div>

        {/* Representatives Display */}
        {representatives.length > 0 && (
          <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
            <h3 className="text-lg font-medium text-green-800 mb-3">Your Representatives:</h3>
            <div className="grid gap-3">
              {representatives.map((rep, index) => (
                <div key={index} className="bg-white p-3 rounded-lg border border-green-200">
                  <div className="flex justify-between items-center">
                    <div>
                      <h4 className="font-medium text-gray-900">{rep.name}</h4>
                      <p className="text-sm text-gray-600">
                        {rep.position} {rep.district && `(${rep.district})`}
                      </p>
                    </div>
                    <div className="text-right text-sm text-gray-600">
                      <p>{rep.email}</p>
                      {rep.phone && <p>{rep.phone}</p>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Step 2: Compose Email */}
      <div className="bg-white rounded-xl p-8 shadow-sm">
        <h2 className="text-2xl font-semibold mb-6 flex items-center">
          <span className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">2</span>
          Describe Your Concern
        </h2>

        <div className="space-y-6">
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

      {/* Step 3: Email Preview */}
      {emailComposition && (
        <div className="bg-white rounded-xl p-8 shadow-sm">
          <h2 className="text-2xl font-semibold mb-6 flex items-center">
            <span className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">3</span>
            Your Generated Email
          </h2>

          <div className="space-y-6">
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
                  onClick={copyEmailToClipboard}
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
      <div className="bg-blue-50 rounded-xl p-8 border border-blue-200">
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
