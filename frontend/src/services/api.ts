import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://10.0.2.2:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach token
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('access_token');

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// Refresh token handler
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = await AsyncStorage.getItem('refresh_token');

      if (refreshToken) {
        try {
          const res = await axios.post(
            `${API_BASE_URL}/auth/refresh`,
            { refresh_token: refreshToken }
          );

          const newToken = res.data.access_token;
          await AsyncStorage.setItem('access_token', newToken);

          error.config.headers.Authorization = `Bearer ${newToken}`;
          return axios(error.config);

        } catch {
          await AsyncStorage.removeItem('access_token');
          await AsyncStorage.removeItem('refresh_token');
        }
      }
    }

    return Promise.reject(error);
  }
);

export const authAPI = {
  sendOTP: (data: any) =>
    api.post('/auth/send-otp', data).then(res => res.data),

  verifyOTP: async (data: any) => {
    const res = await api.post('/auth/verify-otp', data);

    await AsyncStorage.setItem('access_token', res.data.access_token);
    await AsyncStorage.setItem('refresh_token', res.data.refresh_token);

    return res.data;
  },

  completeProfile: (data: any) =>
    api.post('/auth/complete-profile', data).then(res => res.data),

  getProfile: () =>
    api.get('/auth/me').then(res => res.data),
};

export default api;