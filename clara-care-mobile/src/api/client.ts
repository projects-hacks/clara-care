import axios from 'axios';
import { supabase } from './supabase';

// FastAPI backend URL
const API_URL = process.env.EXPO_PUBLIC_API_URL || 'https://api.claracare.me';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attach Supabase JWT to every request
apiClient.interceptors.request.use(
  async (config) => {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: global error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Optionally handle 401s by dispatching a logout action
    if (error.response?.status === 401) {
      console.warn('Unauthorized request, token may be expired.');
    }
    return Promise.reject(error);
  }
);

export default apiClient;
