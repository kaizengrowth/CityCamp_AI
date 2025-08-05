import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import heroImage from '@/assets/images/Hero.png';

export const HomePage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="flex-1">
      {/* Hero Section */}
      <div className="bg-white py-16 w-full">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left side - Text content */}
            <div className="space-y-8">
              <div className="space-y-6">
                <h1 className="text-5xl md:text-6xl font-bold text-brand-dark-blue">
                  CivicSpark AI
                </h1>
                <p className="text-xl text-gray-600 max-w-lg">
                  Connecting Tulsa residents with city government and community organizations
                </p>
              </div>

              {!user && (
                <div className="flex gap-4">
                  <Link
                    to="/register"
                    className="px-8 py-3 bg-brand-dark-blue text-white font-semibold rounded-lg hover:bg-brand-red hover:text-white transition-colors"
                  >
                    Get Started
                  </Link>
                  <Link
                    to="/login"
                    className="px-8 py-3 border-2 border-brand-dark-blue text-brand-dark-blue font-semibold rounded-lg hover:bg-button-hover-bg hover:text-brand-red hover:border-brand-red transition-colors"
                  >
                    Sign In
                  </Link>
                </div>
              )}
            </div>

                                    {/* Right side - Hero Image */}
            <div className="hidden lg:block">
              <img
                src={heroImage}
                alt="CivicSpark AI - Connecting Tulsa residents with city government and civic engagement features"
                className="w-full h-auto"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Explore Section */}
      <div className="py-16 bg-brand-dark-blue">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center text-white mb-12">Explore CivicSpark AI</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Meeting Alerts */}
            <Link
              to="/signup/notifications"
              className="bg-white rounded-lg p-8 text-center hover:shadow-sm hover:scale-105 transition-transform transition-shadow group text-gray-800 hover:text-brand-red"
            >
              <div className="w-16 h-16 bg-button-hover-bg rounded-lg flex items-center justify-center mx-auto mb-6">
                <svg width="45" height="45" viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-gray-600 group-hover:text-brand-yellow">
                  <g clip-path="url(#clip0_8_233)">
                    <path d="M44.1406 3.90625H41.7969V0H37.8906V3.90625H12.1094V0H8.20312V3.90625H5.85938C2.62852 3.90625 0 6.53477 0 9.76562V44.1406C0 47.3715 2.62852 50 5.85938 50H44.1406C47.3715 50 50 47.3715 50 44.1406V9.76562C50 6.53477 47.3715 3.90625 44.1406 3.90625ZM46.0938 44.1406C46.0938 45.2176 45.2176 46.0938 44.1406 46.0938H5.85938C4.78242 46.0938 3.90625 45.2176 3.90625 44.1406V18.3594H46.0938V44.1406ZM46.0938 14.4531H3.90625V9.76562C3.90625 8.68867 4.78242 7.8125 5.85938 7.8125H8.20312V11.7188H12.1094V7.8125H37.8906V11.7188H41.7969V7.8125H44.1406C45.2176 7.8125 46.0938 8.68867 46.0938 9.76562V14.4531Z" fill="currentColor"/>
                    <path d="M11.3281 22.4609H7.42188V26.3672H11.3281V22.4609Z" fill="currentColor"/>
                    <path d="M19.1406 22.4609H15.2344V26.3672H19.1406V22.4609Z" fill="currentColor"/>
                    <path d="M26.9531 22.4609H23.0469V26.3672H26.9531V22.4609Z" fill="currentColor"/>
                    <path d="M34.7656 22.4609H30.8594V26.3672H34.7656V22.4609Z" fill="currentColor"/>
                    <path d="M42.5781 22.4609H38.6719V26.3672H42.5781V22.4609Z" fill="currentColor"/>
                    <path d="M11.3281 30.2734H7.42188V34.1797H11.3281V30.2734Z" fill="currentColor"/>
                    <path d="M19.1406 30.2734H15.2344V34.1797H19.1406V30.2734Z" fill="currentColor"/>
                    <path d="M26.9531 30.2734H23.0469V34.1797H26.9531V30.2734Z" fill="currentColor"/>
                    <path d="M34.7656 30.2734H30.8594V34.1797H34.7656V30.2734Z" fill="currentColor"/>
                    <path d="M11.3281 38.0859H7.42188V41.9922H11.3281V38.0859Z" fill="currentColor"/>
                    <path d="M19.1406 38.0859H15.2344V41.9922H19.1406V38.0859Z" fill="currentColor"/>
                    <path d="M26.9531 38.0859H23.0469V41.9922H26.9531V38.0859Z" fill="currentColor"/>
                    <path d="M34.7656 38.0859H30.8594V41.9922H34.7656V38.0859Z" fill="currentColor"/>
                    <path d="M42.5781 30.2734H38.6719V34.1797H42.5781V30.2734Z" fill="currentColor"/>
                  </g>
                  <defs>
                    <clipPath id="clip0_8_233">
                      <rect width="50" height="50" fill="white"/>
                    </clipPath>
                  </defs>
                </svg>
              </div>
                            <h3 className="text-xl font-bold text-brand-dark-blue mb-3 group-hover:text-brand-red">Meeting Alerts</h3>
              <p className="text-gray-600 leading-relaxed">
                Get notified about Tulsa City Council meetings and agenda items that matter to you
              </p>
            </Link>

            {/* AI Assistant */}
            <div
              className="bg-white rounded-lg p-8 text-center hover:shadow-sm hover:scale-105 transition-transform transition-shadow cursor-pointer group text-gray-800 hover:text-brand-red"
              onClick={() => {
                const chatbotWidget = document.querySelector('.fixed.bottom-4.right-4');
                if (chatbotWidget) {
                  const button = chatbotWidget.querySelector('button');
                  if (button) button.click();
                }
              }}
            >
              <div className="w-16 h-16 bg-button-hover-bg rounded-lg flex items-center justify-center mx-auto mb-6">
                <svg width="60" height="60" viewBox="0 0 66 66" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-gray-600 group-hover:text-brand-yellow">
                  <path d="M40.5404 29.3336C37.8421 29.3336 35.6466 31.529 35.6466 34.2273C35.6466 36.926 37.8421 39.1214 40.5404 39.1214C43.2387 39.1214 45.4341 36.926 45.4341 34.2273C45.4341 31.529 43.2387 29.3336 40.5404 29.3336ZM40.5404 36.3714C39.3581 36.3714 38.3966 35.4096 38.3966 34.2273C38.3966 33.0453 39.358 32.0835 40.5404 32.0835C41.7227 32.0835 42.6841 33.0452 42.6841 34.2273C42.6841 35.4096 41.7227 36.3714 40.5404 36.3714Z" fill="currentColor"/>
                  <path d="M25.4597 29.3336C22.7614 29.3336 20.5659 31.529 20.5659 34.2273C20.5659 36.926 22.7614 39.1214 25.4597 39.1214C28.158 39.1214 30.3534 36.926 30.3534 34.2273C30.3534 31.529 28.158 29.3336 25.4597 29.3336ZM25.4597 36.3714C24.2774 36.3714 23.3159 35.4096 23.3159 34.2273C23.3159 33.0453 24.2773 32.0835 25.4597 32.0835C26.642 32.0835 27.6034 33.0452 27.6034 34.2273C27.6034 35.4096 26.642 36.3714 25.4597 36.3714Z" fill="currentColor"/>
                  <path d="M55.1733 29.0751H54.0359V24.3968C54.0359 21.2672 51.4901 18.7209 48.36 18.7209H34.375V15.5508C36.4991 14.9497 38.0616 12.998 38.0616 10.6841C38.0616 7.89347 35.791 5.62286 33 5.62286C30.209 5.62286 27.9384 7.89347 27.9384 10.6841C27.9384 12.998 29.501 14.9497 31.625 15.5508V18.7209H17.64C14.5101 18.7209 11.9641 21.2671 11.9641 24.3968V29.0751H10.8268C7.77867 29.0751 5.29858 31.5548 5.29858 34.6029V40.8898C5.29858 43.9375 7.77867 46.4173 10.8268 46.4173H11.9641V51.0955C11.9641 54.2251 14.51 56.7714 17.64 56.7714H48.36C51.49 56.7714 54.0359 54.2252 54.0359 51.0955V46.4173H55.1733C58.2214 46.4173 60.7015 43.9375 60.7015 40.8898V34.6029C60.7015 31.5548 58.2213 29.0751 55.1733 29.0751ZM30.6884 10.6841C30.6884 9.40982 31.7257 8.37286 33 8.37286C34.2743 8.37286 35.3116 9.40982 35.3116 10.6841C35.3116 11.9587 34.2743 12.9957 33 12.9957C31.7257 12.9957 30.6884 11.9587 30.6884 10.6841ZM10.8268 43.6673C9.29468 43.6673 8.04858 42.4212 8.04858 40.8898V34.603C8.04858 33.0712 9.29468 31.8251 10.8268 31.8251H11.9641V43.6674L10.8268 43.6673ZM51.2859 51.0956C51.2859 52.7089 49.9734 54.0215 48.36 54.0215H17.64C16.0267 54.0215 14.7141 52.7089 14.7141 51.0956V45.0423V30.4501V24.3968C14.7141 22.7835 16.0267 21.4709 17.64 21.4709H48.36C49.9734 21.4709 51.2859 22.7835 51.2859 24.3968V30.4501V45.0423V51.0956ZM57.9515 40.8898C57.9515 42.4212 56.7054 43.6673 55.1733 43.6673H54.0359V31.8251H55.1733C56.7054 31.8251 57.9515 33.0712 57.9515 34.6029V40.8898Z" fill="currentColor"/>
                </svg>
              </div>
              <h3 className="text-xl font-bold text-brand-dark-blue mb-3 group-hover:text-brand-red">AI Assistant</h3>
              <p className="text-gray-600 leading-relaxed">
                Ask questions about city government, policies, and get instant answers
              </p>
            </div>

            {/* City Council Meetings */}
            <Link
              to="/meetings"
              className="bg-white rounded-lg p-8 text-center hover:shadow-sm hover:scale-105 transition-transform transition-shadow group text-gray-800 hover:text-brand-red"
            >
              <div className="w-16 h-16 bg-button-hover-bg rounded-lg flex items-center justify-center mx-auto mb-6">
                <svg width="60" height="60" viewBox="0 0 66 66" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-gray-600 group-hover:text-brand-yellow">
                  <path d="M58.6107 28.5574C60.5894 27.049 61.875 24.6744 61.875 22C61.875 17.4501 58.1749 13.75 53.625 13.75C49.0751 13.75 45.375 17.4501 45.375 22C45.375 24.684 46.6689 27.0641 48.6585 28.5725C48.4481 28.666 48.2323 28.7457 48.0288 28.8516C47.355 29.2009 47.091 30.0314 47.4402 30.7051C47.7909 31.3802 48.6227 31.6415 49.2937 31.2922C50.6082 30.6102 52.107 30.25 53.625 30.25C58.9311 30.25 63.25 34.5675 63.25 39.875V45.375C63.25 47.6493 61.3993 49.5 59.125 49.5H52.1675C51.4071 49.5 50.7925 50.116 50.7925 50.875C50.7925 51.634 51.4071 52.25 52.1675 52.25H59.125C62.9159 52.25 66 49.1659 66 45.375V39.875C66 34.826 62.9571 30.4796 58.6107 28.5574ZM48.125 22C48.125 18.9667 50.5917 16.5 53.625 16.5C56.6582 16.5 59.125 18.9667 59.125 22C59.125 25.0332 56.6582 27.5 53.625 27.5C50.5917 27.5 48.125 25.0332 48.125 22Z" fill="currentColor"/>
                  <path d="M18.5597 30.7051C18.909 30.0314 18.645 29.2009 17.9712 28.8516C17.7677 28.7457 17.5519 28.666 17.3415 28.5725C19.3311 27.0655 20.625 24.684 20.625 22C20.625 17.4501 16.9249 13.75 12.375 13.75C7.82512 13.75 4.125 17.4501 4.125 22C4.125 24.6744 5.41062 27.049 7.38925 28.5574C3.04288 30.4796 0 34.826 0 39.875V45.375C0 49.1659 3.08413 52.25 6.875 52.25H13.8325C14.5929 52.25 15.2075 51.634 15.2075 50.875C15.2075 50.116 14.5929 49.5 13.8325 49.5H6.875C4.60075 49.5 2.75 47.6493 2.75 45.375V39.875C2.75 34.5675 7.06887 30.25 12.375 30.25C13.893 30.25 15.3917 30.6102 16.7062 31.2922C17.3759 31.6388 18.2091 31.3789 18.5597 30.7051ZM6.875 22C6.875 18.9667 9.34175 16.5 12.375 16.5C15.4082 16.5 17.875 18.9667 17.875 22C17.875 25.0332 15.4082 27.5 12.375 27.5C9.34175 27.5 6.875 25.0332 6.875 22Z" fill="currentColor"/>
                  <path d="M38.4656 27.1631C40.975 25.4237 42.625 22.528 42.625 19.25C42.625 13.9425 38.3061 9.625 33 9.625C27.6939 9.625 23.375 13.9425 23.375 19.25C23.375 22.528 25.025 25.4237 27.5344 27.1631C21.8914 29.3604 17.875 34.8398 17.875 41.25V49.5C17.875 53.2909 20.9591 56.375 24.75 56.375H41.25C45.0409 56.375 48.125 53.2909 48.125 49.5V41.25C48.125 34.8384 44.1086 29.3604 38.4656 27.1631ZM26.125 19.25C26.125 15.4591 29.2091 12.375 33 12.375C36.7909 12.375 39.875 15.4591 39.875 19.25C39.875 23.0409 36.7909 26.125 33 26.125C29.2091 26.125 26.125 23.0409 26.125 19.25ZM45.375 49.5C45.375 51.7743 43.5243 53.625 41.25 53.625H24.75C22.4757 53.625 20.625 51.7743 20.625 49.5V41.25C20.625 34.4272 26.1759 28.875 33 28.875C39.8241 28.875 45.375 34.4272 45.375 41.25V49.5Z" fill="currentColor"/>
                </svg>
              </div>
              <h3 className="text-xl font-bold text-brand-dark-blue mb-3 group-hover:text-brand-red">City Council Meetings</h3>
              <p className="text-gray-600 leading-relaxed">
                Browse upcoming meetings and agendas
              </p>
            </Link>

            {/* Contact Representatives */}
            <Link
              to="/contact-representatives"
              className="bg-white rounded-lg p-8 text-center hover:shadow-sm hover:scale-105 transition-transform transition-shadow group text-gray-800 hover:text-brand-red"
            >
              <div className="w-16 h-16 bg-button-hover-bg rounded-lg flex items-center justify-center mx-auto mb-6">
                <svg width="50" height="50" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-gray-600 group-hover:text-brand-yellow">
                  <path d="M54.7266 8.90625H5.27344C2.3598 8.90625 0 11.2807 0 14.1797V45.8203C0 48.7365 2.37715 51.0938 5.27344 51.0938H54.7266C57.6158 51.0938 60 48.7465 60 45.8203V14.1797C60 11.2859 57.6496 8.90625 54.7266 8.90625ZM53.988 12.4219C52.9106 13.4936 34.3691 31.9375 33.7289 32.5743C32.7328 33.5704 31.4086 34.1188 30 34.1188C28.5914 34.1188 27.2672 33.5702 26.2678 32.571C25.8373 32.1427 7.50035 13.9024 6.01195 12.4219H53.988ZM3.51562 45.1048V14.8975L18.7076 30.0094L3.51562 45.1048ZM6.01418 47.5781L21.2002 32.4887L23.7852 35.0602C25.4453 36.7202 27.6524 37.6344 30 37.6344C32.3476 37.6344 34.5547 36.7202 36.2115 35.0634L38.7998 32.4887L53.9858 47.5781H6.01418ZM56.4844 45.1048L41.2924 30.0094L56.4844 14.8975V45.1048Z" fill="currentColor"/>
                </svg>
              </div>
              <h3 className="text-xl font-bold text-brand-dark-blue mb-3 group-hover:text-brand-red">Contact Representatives</h3>
              <p className="text-gray-600 leading-relaxed">
                Organize and participate in campaigns for issues you care about
              </p>
            </Link>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      {!user && (
        <div className="text-center bg-brand-yellow rounded-md p-12">
          <h2 className="text-3xl font-bold mb-4 text-white">Ready to get involved?</h2>
          <p className="text-xl mb-8 opacity-90 text-brand-dark-blue">Join hundreds of Tulsa residents staying informed and engaged with their city government.</p>
          <Link
            to="/register"
            className="btn bg-white text-brand-dark-blue hover:bg-button-hover-bg btn-lg px-8 py-3 text-lg font-semibold border-2 border-brand-dark-blue hover:text-brand-red hover:border-brand-red transition-colors"
          >
            Create Your Account
          </Link>
        </div>
      )}
    </div>
  );
};
