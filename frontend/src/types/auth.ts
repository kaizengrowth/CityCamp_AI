export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  phone_number?: string;
  is_active: boolean;
  is_verified: boolean;
  is_admin: boolean;
  interests: string[];
  zip_code?: string;
  council_district?: string;
  sms_notifications: boolean;
  email_notifications: boolean;
  push_notifications: boolean;
  created_at: string;
  updated_at?: string;
  last_login?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  username: string;
  full_name: string;
  phone_number?: string;
  interests?: string[];
  zip_code?: string;
  council_district?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}
