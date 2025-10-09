import { Platform } from 'react-native';

// Configuration for different environments
const config = {
  development: {
    API_BASE_URL: Platform.select({
      web: 'http://localhost:8000',
      default: 'http://10.0.2.2:8000', // Android emulator
      // For physical device, use your computer's IP address
      // default: 'http://192.168.1.XXX:8000', // Replace XXX with your IP
    }),
  },
  production: {
    API_BASE_URL: 'https://ai-surrogate.onrender.com', // Your deployed backend URL
  },
};

const currentConfig = __DEV__ ? config.development : config.production;

export const API_BASE_URL = currentConfig.API_BASE_URL;

export default config;