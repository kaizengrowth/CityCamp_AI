import React, { useState, useEffect } from 'react';
import { apiRequest, API_BASE_URL } from '../config/api';
import toast from 'react-hot-toast';

interface FormData {
  full_name: string;
  email: string;
  phone_number: string;
  zip_code: string;
  interested_topics: string[];
  meeting_types: string[];
  sms_notifications: boolean;
  email_notifications: boolean;
  advance_notice_hours: number;
}

const MEETING_TYPES = [
  { value: 'regular_council', label: 'Regular City Council', description: 'Monthly city council meetings' },
  { value: 'public_works_committee', label: 'Public Works Committee', description: 'Infrastructure and utilities' },
  { value: 'urban_economic_committee', label: 'Economic Development', description: 'Business and urban planning' },
  { value: 'budget_committee', label: 'Budget Committee', description: 'City budget discussions' },
  { value: 'planning_commission', label: 'Planning Commission', description: 'Zoning and development' },
  { value: 'public_hearing', label: 'Public Hearings', description: 'Special public input sessions' },
];

interface Topic {
  id: number;
  name: string;
  display_name: string;
  description: string;
  category: string;
  icon: string;
}

interface StepProps {
  formData: FormData;
  updateFormData: (data: Partial<FormData>) => void;
  onNext: () => void;
  onBack: () => void;
}

const TopicSelectionStep: React.FC<StepProps> = ({ formData, updateFormData, onNext, onBack }) => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['education', 'health', 'community'])); // Start with high-priority categories expanded

  const fetchTopics = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/subscriptions/topics`);
      if (response.ok) {
        const data = await response.json();
        setTopics(data);
      } else {
        toast.error('Failed to load topics');
      }
    } catch (error) {
      console.error('Error fetching topics:', error);
      toast.error('Failed to load topics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTopics();
  }, []);

  const toggleTopic = (topicId: number) => {
    const currentTopics = formData.interested_topics || [];
    const topicIdStr = topicId.toString();
    const newTopics = currentTopics.includes(topicIdStr)
      ? currentTopics.filter(id => id !== topicIdStr)
      : [...currentTopics, topicIdStr];
    updateFormData({ interested_topics: newTopics });
  };

  const toggleCategory = (categoryId: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(categoryId)) {
      newExpanded.delete(categoryId);
    } else {
      newExpanded.add(categoryId);
    }
    setExpandedCategories(newExpanded);
  };

  const selectAllInCategory = (categoryId: string) => {
    const categoryTopics = topics
      .filter(topic => topic.category === categoryId)
      .map(topic => topic.id.toString());
    const currentTopics = formData.interested_topics || [];
    const allCategorySelected = categoryTopics.every(id => currentTopics.includes(id));

    let newTopics;
    if (allCategorySelected) {
      // Remove all category topics
      newTopics = currentTopics.filter(id => !categoryTopics.includes(id));
    } else {
      // Add all category topics
      newTopics = [...new Set([...currentTopics, ...categoryTopics])];
    }
    updateFormData({ interested_topics: newTopics });
  };

  const handleNext = () => {
    if (!formData.interested_topics || formData.interested_topics.length === 0) {
      toast.error('Please select at least one topic of interest');
      return;
    }
    onNext();
  };

  const groupedTopics = [
    {
      id: 'education',
      name: 'Education & Schools',
      description: 'School programs, funding, and educational services',
      icon: '📚',
      color: 'bg-purple-50 border-purple-200',
      textColor: 'text-purple-800'
    },
    {
      id: 'health',
      name: 'Health & Social Services',
      description: 'Healthcare, senior services, and family support',
      icon: '🏥',
      color: 'bg-red-50 border-red-200',
      textColor: 'text-red-800'
    },
    {
      id: 'community',
      name: 'Housing & Community',
      description: 'Housing, neighborhood development, and community programs',
      icon: '🏠',
      color: 'bg-green-50 border-green-200',
      textColor: 'text-green-800'
    },
    {
      id: 'environment',
      name: 'Environment & Recreation',
      description: 'Parks, utilities, environmental issues, and recreation',
      icon: '🌳',
      color: 'bg-emerald-50 border-emerald-200',
      textColor: 'text-emerald-800'
    },
    {
      id: 'culture',
      name: 'Arts, Culture & Events',
      description: 'Cultural events, festivals, libraries, and community activities',
      icon: '🎭',
      color: 'bg-indigo-50 border-indigo-200',
      textColor: 'text-indigo-800'
    },
    {
      id: 'infrastructure',
      name: 'Transportation',
      description: 'Roads, traffic, public transit, and transportation services',
      icon: '🚗',
      color: 'bg-blue-50 border-blue-200',
      textColor: 'text-blue-800'
    },
    {
      id: 'safety',
      name: 'Public Safety',
      description: 'Police, fire, emergency services, and community safety',
      icon: '🚓',
      color: 'bg-red-50 border-red-200',
      textColor: 'text-red-800'
    },
    {
      id: 'social',
      name: 'Immigration & Social Justice',
      description: 'Immigration services, civil rights, and social equity programs',
      icon: '🤝',
      color: 'bg-cyan-50 border-cyan-200',
      textColor: 'text-cyan-800'
    },
    {
      id: 'finance',
      name: 'City Budget & Taxes',
      description: 'City budget, taxes, and public spending',
      icon: '💰',
      color: 'bg-yellow-50 border-yellow-200',
      textColor: 'text-yellow-800'
    },
    {
      id: 'economic',
      name: 'Economic Development',
      description: 'Business development, jobs, and economic growth',
      icon: '📈',
      color: 'bg-cyan-50 border-cyan-200',
      textColor: 'text-cyan-800'
    },
    {
      id: 'planning',
      name: 'Zoning & Development',
      description: 'Land use planning, zoning, and development projects',
      icon: '🏗️',
      color: 'bg-purple-50 border-purple-200',
      textColor: 'text-purple-800'
    }
  ].map(category => ({
    ...category,
    topics: topics.filter(topic => topic.category === category.id)
  })).filter(category => category.topics.length > 0);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          What topics interest you most?
        </h2>
        <p className="text-gray-600">
          Select the topics you'd like to receive notifications about. We've organized them by everyday impact.
        </p>
      </div>

      <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
        {groupedTopics.map((category) => {
          const categoryTopics = category.topics;
          const selectedInCategory = categoryTopics.filter(topic =>
            formData.interested_topics?.includes(topic.id.toString())
          ).length;
          const isExpanded = expandedCategories.has(category.id);

          return (
            <div key={category.id} className={`border-2 rounded-lg ${category.color}`}>
              <div
                className="p-4 cursor-pointer"
                onClick={() => toggleCategory(category.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{category.icon}</span>
                    <div>
                      <h3 className={`font-semibold text-lg ${category.textColor}`}>
                        {category.name}
                      </h3>
                      <p className="text-sm text-gray-600">{category.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {selectedInCategory > 0 && (
                      <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                        {selectedInCategory} selected
                      </span>
                    )}
                    <button
                      className={`text-sm px-3 py-1 rounded-full border transition-colors ${
                        selectedInCategory === categoryTopics.length
                          ? 'bg-blue-100 text-blue-800 border-blue-300'
                          : 'bg-gray-100 text-gray-600 border-gray-300 hover:bg-gray-200'
                      }`}
                      onClick={(e) => {
                        e.stopPropagation();
                        selectAllInCategory(category.id);
                      }}
                    >
                      {selectedInCategory === categoryTopics.length ? 'Deselect All' : 'Select All'}
                    </button>
                    <svg
                      className={`w-5 h-5 transition-transform ${isExpanded ? 'rotate-180' : ''} ${category.textColor}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              </div>

              {isExpanded && (
                <div className="px-4 pb-4 border-t border-gray-200 bg-white/50">
                  <div className="grid grid-cols-1 gap-2 mt-3">
                    {categoryTopics.map((topic) => {
                      const isSelected = formData.interested_topics?.includes(topic.id.toString());
                      return (
                        <div
                          key={topic.id}
                          className={`flex items-start space-x-3 p-3 rounded-md cursor-pointer transition-all ${
                            isSelected
                              ? 'bg-blue-50 border border-blue-200'
                              : 'bg-white border border-gray-200 hover:border-gray-300'
                          }`}
                          onClick={() => toggleTopic(topic.id)}
                        >
                          <div className={`flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center mt-0.5 ${
                            isSelected
                              ? 'bg-blue-600 border-blue-600'
                              : 'border-gray-300'
                          }`}>
                            {isSelected && (
                              <span className="text-white text-xs font-bold">✓</span>
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center space-x-2">
                              <span className="text-lg">{topic.icon}</span>
                              <h4 className="text-sm font-medium text-gray-900">
                                {topic.display_name}
                              </h4>
                            </div>
                            <p className="text-xs text-gray-600 mt-1">
                              {topic.description}
                            </p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="flex justify-between pt-6 mt-6 border-t">
        <button
          onClick={onBack}
          className="px-6 py-2 text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
        >
          Back
        </button>
        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-600">
            {formData.interested_topics?.length || 0} topics selected
          </span>
          <button
            onClick={handleNext}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  );
};

export const NotificationSignup: React.FC = () => {
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    full_name: '',
    email: '',
    phone_number: '',
    zip_code: '',
    interested_topics: [],
    meeting_types: ['regular_council'],
    sms_notifications: true,
    email_notifications: true,
    advance_notice_hours: 24,
  });

  const [currentStep, setCurrentStep] = useState(1);
  const [subscriptionSuccess, setSubscriptionSuccess] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData(prev => ({ ...prev, [name]: checked }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };



  const handleMeetingTypeToggle = (meetingType: string) => {
    setFormData(prev => ({
      ...prev,
      meeting_types: prev.meeting_types.includes(meetingType)
        ? prev.meeting_types.filter(t => t !== meetingType)
        : [...prev.meeting_types, meetingType]
    }));
  };

  const validateStep1 = () => {
    if (!formData.full_name.trim() || !formData.email.trim()) {
      toast.error('Please fill in your name and email address.');
      return false;
    }
    if (formData.email && !/\S+@\S+\.\S+/.test(formData.email)) {
      toast.error('Please enter a valid email address.');
      return false;
    }
    return true;
  };

  const validateStep2 = () => {
    if (formData.interested_topics.length === 0) {
      toast.error('Please select at least one topic of interest.');
      return false;
    }
    return true;
  };

  const handleNext = () => {
    if (currentStep === 1 && validateStep1()) {
      setCurrentStep(2);
    } else if (currentStep === 2 && validateStep2()) {
      setCurrentStep(3);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateStep1() || !validateStep2()) return;

    if (!formData.sms_notifications && !formData.email_notifications) {
      toast.error('Please enable at least one notification method (SMS or Email).');
      return;
    }

    setSubmitting(true);

    try {
      await apiRequest('/api/v1/subscriptions/signup', {
        method: 'POST',
        body: JSON.stringify({
          ...formData,
          phone_number: formData.phone_number || null,
          zip_code: formData.zip_code || null,
        }),
      });

      setSubscriptionSuccess(true);
      toast.success('🎉 Signup successful! Please check your email to confirm your subscription.');
    } catch (error: any) {
      console.error('Subscription error:', error);
      if (error.message?.includes('already subscribed')) {
        toast.error('This email is already subscribed. Check your email for a link to update your preferences.');
      } else {
        toast.error('Signup failed. Please try again or contact support.');
      }
    } finally {
      setSubmitting(false);
    }
  };



  if (subscriptionSuccess) {
    return (
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-8 text-center">
        <div className="text-6xl mb-4">🎉</div>
        <h2 className="text-2xl font-bold text-green-600 mb-4">
          Subscription Successful!
        </h2>
        <p className="text-gray-600 mb-6">
          Thank you for signing up for Tulsa City Council meeting notifications!
          We've sent a confirmation email to <strong>{formData.email}</strong>.
        </p>
        <p className="text-sm text-gray-500 mb-6">
          Please check your email and click the confirmation link to activate your notifications.
          Don't forget to check your spam folder if you don't see it in your inbox.
        </p>
        <button
          onClick={() => {
            setSubscriptionSuccess(false);
            setCurrentStep(1);
            setFormData({
              full_name: '',
              email: '',
              phone_number: '',
              zip_code: '',
              interested_topics: [],
              meeting_types: ['regular_council'],
              sms_notifications: true,
              email_notifications: true,
              advance_notice_hours: 24,
            });
          }}
          className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 transition-colors"
        >
          Sign Up Another Person
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Progress indicator */}
      <div className="bg-gray-50 px-8 py-4">
        <div className="flex items-center justify-between">
          {[1, 2, 3].map((step) => (
            <div key={step} className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step <= currentStep
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}
              >
                {step}
              </div>
              <span className={`ml-2 text-sm ${step <= currentStep ? 'text-primary-600' : 'text-gray-500'}`}>
                {step === 1 && 'Contact Info'}
                {step === 2 && 'Topics'}
                {step === 3 && 'Preferences'}
              </span>
              {step < 3 && (
                <div className={`ml-4 w-16 h-1 ${step < currentStep ? 'bg-primary-600' : 'bg-gray-200'}`} />
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="p-8">
        <form onSubmit={handleSubmit}>
          {/* Step 1: Contact Information */}
          {currentStep === 1 && (
            <div className="space-y-6">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                  Stay Informed About Tulsa City Council
                </h2>
                <p className="text-lg text-gray-600">
                  Get notified about upcoming meetings on topics that matter to you
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    id="full_name"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Your full name"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address *
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="your@email.com"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="phone_number" className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number <span className="text-gray-500">(for SMS notifications)</span>
                  </label>
                  <input
                    type="tel"
                    id="phone_number"
                    name="phone_number"
                    value={formData.phone_number}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="(555) 123-4567"
                  />
                </div>

                <div>
                  <label htmlFor="zip_code" className="block text-sm font-medium text-gray-700 mb-2">
                    Zip Code <span className="text-gray-500">(optional)</span>
                  </label>
                  <input
                    type="text"
                    id="zip_code"
                    name="zip_code"
                    value={formData.zip_code}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="74101"
                  />
                </div>
              </div>

              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={handleNext}
                  className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 transition-colors"
                >
                  Next: Select Topics →
                </button>
              </div>
            </div>
          )}

          {/* Step 2: Topic Selection */}
          {currentStep === 2 && (
            <TopicSelectionStep
              formData={formData}
              updateFormData={(data) => setFormData(prev => ({ ...prev, ...data }))}
              onNext={handleNext}
              onBack={() => setCurrentStep(1)}
            />
          )}

          {/* Step 3: Notification Preferences */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Notification Preferences
                </h2>
                <p className="text-gray-600">
                  Choose how and when you'd like to be notified
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Meeting Types */}
                <div className="bg-gray-50 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Meeting Types</h3>
                  <div className="space-y-3">
                    {MEETING_TYPES.map((type) => (
                      <label key={type.value} className="flex items-start space-x-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={formData.meeting_types.includes(type.value)}
                          onChange={() => handleMeetingTypeToggle(type.value)}
                          className="mt-1 h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                        />
                        <div>
                          <div className="font-medium text-gray-900">{type.label}</div>
                          <div className="text-sm text-gray-600">{type.description}</div>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Notification Settings */}
                <div className="space-y-6">
                  <div className="bg-gray-50 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">How to notify you</h3>
                    <div className="space-y-4">
                      <label className="flex items-center space-x-3 cursor-pointer">
                        <input
                          type="checkbox"
                          name="email_notifications"
                          checked={formData.email_notifications}
                          onChange={handleInputChange}
                          className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                        />
                        <span className="font-medium text-gray-900">Email notifications</span>
                      </label>

                      <label className="flex items-center space-x-3 cursor-pointer">
                        <input
                          type="checkbox"
                          name="sms_notifications"
                          checked={formData.sms_notifications}
                          onChange={handleInputChange}
                          className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                          disabled={!formData.phone_number}
                        />
                        <div>
                          <span className={`font-medium ${!formData.phone_number ? 'text-gray-400' : 'text-gray-900'}`}>
                            SMS notifications
                          </span>
                          {!formData.phone_number && (
                            <div className="text-sm text-gray-500">Requires phone number</div>
                          )}
                        </div>
                      </label>
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-6">
                    <label htmlFor="advance_notice_hours" className="block text-sm font-medium text-gray-700 mb-2">
                      Advance Notice
                    </label>
                    <select
                      id="advance_notice_hours"
                      name="advance_notice_hours"
                      value={formData.advance_notice_hours}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value={1}>1 hour before</option>
                      <option value={4}>4 hours before</option>
                      <option value={12}>12 hours before</option>
                      <option value={24}>24 hours before (recommended)</option>
                      <option value={48}>2 days before</option>
                      <option value={168}>1 week before</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">📋 Summary</h4>
                <div className="text-sm text-blue-800">
                  <p><strong>Topics:</strong> {formData.interested_topics.length} selected</p>
                  <p><strong>Meeting Types:</strong> {formData.meeting_types.length} selected</p>
                  <p><strong>Notifications:</strong>
                    {formData.email_notifications && ' Email'}
                    {formData.email_notifications && formData.sms_notifications && ' +'}
                    {formData.sms_notifications && ' SMS'}
                  </p>
                </div>
              </div>

              <div className="flex justify-between">
                <button
                  type="button"
                  onClick={() => setCurrentStep(2)}
                  className="bg-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-400 transition-colors"
                >
                  ← Back
                </button>
                <button
                  type="submit"
                  disabled={submitting || (!formData.sms_notifications && !formData.email_notifications)}
                  className="bg-primary-600 text-white px-8 py-2 rounded-lg hover:bg-primary-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {submitting ? (
                    <>
                      <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Signing up...
                    </>
                  ) : (
                    'Complete Signup 🎉'
                  )}
                </button>
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  );
};
