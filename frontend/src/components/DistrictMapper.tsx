import React, { useState } from 'react';
import { apiRequest, API_ENDPOINTS } from '../config/api';
import toast from 'react-hot-toast';

interface DistrictInfo {
  found: boolean;
  district?: string;
  coordinates?: { lat: number; lng: number };
  councilor?: {
    name: string;
    email: string;
    phone?: string;
  };
  error?: string;
  message?: string;
}

interface DistrictLookupResult {
  representatives: Array<{
    name: string;
    position: string;
    email: string;
    phone?: string;
    district?: string;
  }>;
  address: string;
  district_info: DistrictInfo;
}

export const DistrictMapper: React.FC = () => {
  const [address, setAddress] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DistrictLookupResult | null>(null);

  const handleAddressLookup = async () => {
    if (!address.trim()) {
      toast.error('Please enter your address');
      return;
    }

    setLoading(true);
    try {
      console.log('Looking up district for address:', address);

      const response = await apiRequest<DistrictLookupResult>(
        `${API_ENDPOINTS.findRepresentatives}?address=${encodeURIComponent(address)}`
      );

      console.log('District lookup result:', response);
      setResult(response);

      if (response.district_info.found) {
        toast.success(`Found you in ${response.district_info.district}!`);
      } else {
        toast.error(response.district_info.message || 'Could not determine district');
      }

    } catch (error) {
      console.error('Error looking up district:', error);
      toast.error('Unable to lookup district. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="text-2xl font-semibold mb-4 flex items-center text-brand-dark-blue">
          <span className="w-8 h-8 bg-brand-red text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
            🗺️
          </span>
          Find Your City Council District
        </h2>

        <p className="text-gray-600 mb-6">
          Enter your Tulsa address to find your City Council district and representative.
        </p>

        <div className="space-y-4">
          <div>
            <label htmlFor="district-address" className="block text-sm font-medium text-gray-700 mb-2">
              Your Tulsa Address
            </label>
            <div className="flex space-x-3">
              <input
                type="text"
                id="district-address"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="e.g., 123 Main Street, Tulsa, OK 74103"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-dark-blue focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && handleAddressLookup()}
              />
              <button
                onClick={handleAddressLookup}
                disabled={loading}
                className="px-4 py-2 bg-brand-dark-blue text-white font-medium rounded-lg hover:bg-brand-red hover:text-white transition-colors disabled:opacity-50 text-sm"
              >
                {loading ? 'Finding...' : 'Find District'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {result && (
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="text-xl font-semibold mb-4 text-brand-dark-blue">District Lookup Results</h3>

          {result.district_info.found ? (
            <div className="space-y-4">
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <h4 className="font-medium text-green-800 mb-2">
                  ✅ District Found: {result.district_info.district}
                </h4>
                <p className="text-green-700 text-sm">
                  Address: {result.address}
                </p>
                {result.district_info.coordinates && (
                  <p className="text-green-600 text-sm">
                    Location: {result.district_info.coordinates.lat.toFixed(4)}, {result.district_info.coordinates.lng.toFixed(4)}
                  </p>
                )}
              </div>

              {/* Representatives */}
              <div>
                <div className="text-sm font-medium text-brand-dark-blue mb-3">Your Representatives</div>
                <div className="grid gap-3">
                  {result.representatives.map((rep, index) => (
                    <div key={index} className="bg-gray-50 p-4 rounded-lg border">
                      <div className="flex justify-between items-start">
                        <div>
                          <h5 className="font-medium text-brand-dark-blue">{rep.name}</h5>
                          <p className="text-sm text-gray-600 mb-2">
                            {rep.position}
                          </p>
                        </div>
                        <div className="text-right text-sm text-gray-600">
                          <p>
                            <a href={`mailto:${rep.email}`} className="text-blue-600 hover:text-blue-800">
                              {rep.email}
                            </a>
                          </p>
                          {rep.phone && <p>{rep.phone}</p>}
                        </div>
                      </div>

                      <div className="mt-3 flex space-x-2">
                        <a
                          href={`mailto:${rep.email}?subject=Constituent Inquiry`}
                          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                        >
                          Send Email
                        </a>
                        <span className="text-gray-300">|</span>
                        <a
                          href={`/contact-representatives?prefill=${encodeURIComponent(rep.name)}`}
                          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                        >
                          AI Compose Email
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Interactive Map Placeholder */}
              <div className="bg-gray-100 p-6 rounded-lg text-center">
                <h4 className="font-medium text-gray-700 mb-2">District Map</h4>
                <p className="text-gray-600 text-sm mb-4">
                  Interactive map showing your district boundaries would appear here.
                </p>
                <a
                  href="https://cityoftulsa.maps.arcgis.com/apps/webappviewer/index.html?id=d0d03cae97d348b9a67ed1eff92d6ca0"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm"
                >
                  View Official District Map
                </a>
              </div>
            </div>
          ) : (
            <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
              <h4 className="font-medium text-yellow-800 mb-2">
                ⚠️ District Not Found
              </h4>
              <p className="text-yellow-700 text-sm mb-3">
                {result.district_info.message}
              </p>
              {result.district_info.error && (
                <p className="text-yellow-600 text-sm">
                  Technical details: {result.district_info.error}
                </p>
              )}

              {/* Fallback Representatives */}
              <div className="mt-4">
                <h5 className="font-medium text-yellow-800 mb-2">Contact These Representatives:</h5>
                <div className="grid gap-2">
                  {result.representatives.map((rep, index) => (
                    <div key={index} className="bg-white p-3 rounded border">
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="font-medium">{rep.name}</p>
                          <p className="text-sm text-gray-600">{rep.position}</p>
                        </div>
                        <div className="text-right text-sm">
                          <a href={`mailto:${rep.email}`} className="text-blue-600 hover:text-blue-800">
                            {rep.email}
                          </a>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Tips for Accurate Results */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h4 className="font-medium text-blue-800 mb-2">💡 Tips for Accurate Results</h4>
            <ul className="text-blue-700 text-sm space-y-1">
              <li>• Include your full street address (number and street name)</li>
              <li>• Make sure your address is within Tulsa city limits</li>
              <li>• Try including ZIP code for better accuracy</li>
              <li>• Use the official <a href="https://www.tulsacouncil.org/district-finder" target="_blank" rel="noopener noreferrer" className="underline">District Finder</a> for verification</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
