import { DefaultTheme } from '@react-navigation/native';

export const Colors = {
  primary: '#00FFFF',      // Cyan
  secondary: '#007BFF',    // Blue
  background: '#0A0A0A',   // Dark background
  surface: '#1A1A1A',     // Card/surface background
  text: '#FFFFFF',         // Primary text
  textSecondary: '#B0B0B0', // Secondary text
  success: '#00FF88',      // Success green
  warning: '#FFB800',      // Warning orange
  error: '#FF4757',        // Error red
  transparent: 'transparent',
  
  // Gradient colors
  gradientStart: '#00FFFF',
  gradientEnd: '#007BFF',
  
  // Chat bubble colors
  userBubble: '#333333',
  aiBubble: ['#00FFFF', '#007BFF'], // Gradient
  
  // Glow effects
  glow: '#00FFFF80', // 50% opacity cyan
};

export const Theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: Colors.primary,
    background: Colors.background,
    card: Colors.surface,
    text: Colors.text,
    border: Colors.primary,
    notification: Colors.primary,
  },
};

export const Fonts = {
  regular: 'Inter_400Regular',
  medium: 'Inter_500Medium',
  semiBold: 'Inter_600SemiBold',
  bold: 'Inter_700Bold',
  
  sizes: {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 20,
    xxl: 24,
    xxxl: 32,
  },
};

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const BorderRadius = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  full: 9999,
};

export const Shadows = {
  small: {
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 2,
  },
  medium: {
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
    elevation: 4,
  },
  large: {
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.5,
    shadowRadius: 16,
    elevation: 8,
  },
};