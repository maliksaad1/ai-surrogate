import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  SafeAreaView,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../types';
import { Colors, Fonts, Spacing, BorderRadius } from '../constants/theme';

type OnboardingScreenNavigationProp = StackNavigationProp<
  RootStackParamList,
  'Onboarding'
>;

interface Props {
  navigation: OnboardingScreenNavigationProp;
}

const { width, height } = Dimensions.get('window');

export default function OnboardingScreen({ navigation }: Props) {
  const handleGetStarted = () => {
    navigation.navigate('Auth');
  };

  return (
    <LinearGradient
      colors={[Colors.gradientStart, Colors.gradientEnd]}
      style={styles.container}
    >
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.content}>
          {/* Logo/Icon placeholder */}
          <View style={styles.logoContainer}>
            <LinearGradient
              colors={[Colors.primary, Colors.secondary]}
              style={styles.logo}
            >
              <Text style={styles.logoText}>AI</Text>
            </LinearGradient>
          </View>

          {/* Title */}
          <Text style={styles.title}>Your AI Surrogate Companion</Text>

          {/* Subtitle */}
          <Text style={styles.subtitle}>
            Talk, feel, and grow with your personal AI.
          </Text>

          {/* Features */}
          <View style={styles.featuresContainer}>
            <View style={styles.feature}>
              <Text style={styles.featureIcon}>💬</Text>
              <Text style={styles.featureText}>Voice & Text Chat</Text>
            </View>
            <View style={styles.feature}>
              <Text style={styles.featureIcon}>🧠</Text>
              <Text style={styles.featureText}>Emotional Intelligence</Text>
            </View>
            <View style={styles.feature}>
              <Text style={styles.featureIcon}>📝</Text>
              <Text style={styles.featureText}>Memory & Context</Text>
            </View>
          </View>

          {/* Get Started Button */}
          <TouchableOpacity
            style={styles.button}
            onPress={handleGetStarted}
            activeOpacity={0.8}
          >
            <LinearGradient
              colors={[Colors.primary, Colors.secondary]}
              style={styles.buttonGradient}
            >
              <Text style={styles.buttonText}>Get Started</Text>
            </LinearGradient>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: Spacing.xl,
  },
  logoContainer: {
    marginBottom: Spacing.xxl,
  },
  logo: {
    width: 120,
    height: 120,
    borderRadius: 60,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.5,
    shadowRadius: 20,
    elevation: 10,
  },
  logoText: {
    fontSize: 48,
    fontWeight: 'bold',
    color: Colors.background,
  },
  title: {
    fontSize: Fonts.sizes.xxxl,
    fontWeight: 'bold',
    color: Colors.background,
    textAlign: 'center',
    marginBottom: Spacing.md,
    textShadowColor: 'rgba(0, 0, 0, 0.3)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  subtitle: {
    fontSize: Fonts.sizes.lg,
    color: Colors.background,
    textAlign: 'center',
    marginBottom: Spacing.xxl,
    opacity: 0.9,
    lineHeight: 24,
  },
  featuresContainer: {
    width: '100%',
    marginBottom: Spacing.xxl,
  },
  feature: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.lg,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    padding: Spacing.md,
    borderRadius: BorderRadius.md,
  },
  featureIcon: {
    fontSize: 24,
    marginRight: Spacing.md,
  },
  featureText: {
    fontSize: Fonts.sizes.md,
    color: Colors.background,
    fontWeight: '600',
  },
  button: {
    width: '100%',
    marginTop: Spacing.lg,
  },
  buttonGradient: {
    paddingVertical: Spacing.lg,
    paddingHorizontal: Spacing.xl,
    borderRadius: BorderRadius.lg,
    alignItems: 'center',
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 16,
    elevation: 8,
  },
  buttonText: {
    fontSize: Fonts.sizes.lg,
    fontWeight: 'bold',
    color: Colors.background,
  },
});