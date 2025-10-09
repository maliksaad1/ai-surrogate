import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Switch,
  Alert,
  ScrollView,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { BottomTabNavigationProp } from '@react-navigation/bottom-tabs';

import { Colors, Fonts, Spacing, BorderRadius } from '../constants/theme';
import { supabase } from '../services/supabase';
import { MainTabParamList } from '../types';

type SettingsScreenNavigationProp = BottomTabNavigationProp<MainTabParamList, 'Settings'>;

interface Props {
  navigation: SettingsScreenNavigationProp;
}

interface SettingsOption {
  id: string;
  title: string;
  subtitle?: string;
  type: 'toggle' | 'action' | 'dropdown';
  value?: boolean;
  options?: string[];
  icon: keyof typeof Ionicons.glyphMap;
  onPress?: () => void;
  onToggle?: (value: boolean) => void;
}

export default function SettingsScreen({ navigation }: Props) {
  const [voiceMode, setVoiceMode] = useState(true);
  const [memorySync, setMemorySync] = useState(true);
  const [darkMode, setDarkMode] = useState(true);
  const [language, setLanguage] = useState('English');
  const [theme, setTheme] = useState('Cyan Neon');

  const handleSignOut = async () => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Sign Out',
          style: 'destructive',
          onPress: async () => {
            try {
              const { error } = await supabase.auth.signOut();
              if (error) throw error;
              // Navigation will be handled by auth state change
            } catch (error: any) {
              Alert.alert('Error', 'Failed to sign out');
            }
          },
        },
      ]
    );
  };

  const settings: SettingsOption[] = [
    {
      id: 'voice',
      title: 'Voice Mode',
      subtitle: 'Enable voice input and output',
      type: 'toggle',
      value: voiceMode,
      icon: 'mic',
      onToggle: setVoiceMode,
    },
    {
      id: 'memory',
      title: 'Memory Sync',
      subtitle: 'Allow AI to remember conversations',
      type: 'toggle',
      value: memorySync,
      icon: 'cloud-upload',
      onToggle: setMemorySync,
    },
    {
      id: 'darkMode',
      title: 'Dark Mode',
      subtitle: 'Use dark theme',
      type: 'toggle',
      value: darkMode,
      icon: 'moon',
      onToggle: setDarkMode,
    },
    {
      id: 'language',
      title: 'Language',
      subtitle: language,
      type: 'dropdown',
      icon: 'language',
      options: ['English', 'Spanish', 'French', 'German'],
      onPress: () => Alert.alert('Coming Soon', 'Language selection will be available in a future update'),
    },
    {
      id: 'theme',
      title: 'Theme',
      subtitle: theme,
      type: 'dropdown',
      icon: 'color-palette',
      options: ['Cyan Neon', 'Purple Glow', 'Green Matrix', 'Orange Sunset'],
      onPress: () => Alert.alert('Coming Soon', 'Theme selection will be available in a future update'),
    },
    {
      id: 'notifications',
      title: 'Notifications',
      subtitle: 'Manage notification preferences',
      type: 'action',
      icon: 'notifications',
      onPress: () => Alert.alert('Coming Soon', 'Notification settings will be available in a future update'),
    },
    {
      id: 'privacy',
      title: 'Privacy & Security',
      subtitle: 'Data and privacy settings',
      type: 'action',
      icon: 'shield-checkmark',
      onPress: () => Alert.alert('Coming Soon', 'Privacy settings will be available in a future update'),
    },
    {
      id: 'help',
      title: 'Help & Support',
      subtitle: 'Get help and contact support',
      type: 'action',
      icon: 'help-circle',
      onPress: () => Alert.alert('Help', 'For support, please contact us at support@aisurrogate.com'),
    },
    {
      id: 'about',
      title: 'About',
      subtitle: 'App version and information',
      type: 'action',
      icon: 'information-circle',
      onPress: () => Alert.alert('About', 'AI Surrogate v1.0.0\nYour personal AI companion'),
    },
    {
      id: 'signout',
      title: 'Sign Out',
      subtitle: 'Sign out of your account',
      type: 'action',
      icon: 'log-out',
      onPress: handleSignOut,
    },
  ];

  const renderSettingItem = (setting: SettingsOption) => (
    <TouchableOpacity
      key={setting.id}
      style={styles.settingItem}
      onPress={setting.onPress}
      activeOpacity={setting.type === 'toggle' ? 1 : 0.7}
    >
      <LinearGradient
        colors={[Colors.surface, Colors.surface + '80']}
        style={styles.settingGradient}
      >
        <View style={styles.settingIcon}>
          <LinearGradient
            colors={[Colors.primary, Colors.secondary]}
            style={styles.iconGradient}
          >
            <Ionicons name={setting.icon} size={20} color={Colors.background} />
          </LinearGradient>
        </View>
        
        <View style={styles.settingContent}>
          <Text style={styles.settingTitle}>{setting.title}</Text>
          {setting.subtitle && (
            <Text style={styles.settingSubtitle}>{setting.subtitle}</Text>
          )}
        </View>

        <View style={styles.settingAction}>
          {setting.type === 'toggle' ? (
            <Switch
              value={setting.value}
              onValueChange={setting.onToggle}
              trackColor={{ false: Colors.textSecondary, true: Colors.primary }}
              thumbColor={setting.value ? Colors.background : Colors.surface}
            />
          ) : (
            <Ionicons name="chevron-forward" size={20} color={Colors.textSecondary} />
          )}
        </View>
      </LinearGradient>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContainer} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Settings</Text>
          <Text style={styles.headerSubtitle}>Customize your AI Surrogate experience</Text>
        </View>

        <View style={styles.settingsContainer}>
          {settings.map(renderSettingItem)}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  scrollContainer: {
    paddingBottom: Spacing.xl,
  },
  header: {
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.xl,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: Fonts.sizes.xxl,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: Spacing.xs,
  },
  headerSubtitle: {
    fontSize: Fonts.sizes.md,
    color: Colors.textSecondary,
    textAlign: 'center',
  },
  settingsContainer: {
    paddingHorizontal: Spacing.md,
  },
  settingItem: {
    marginBottom: Spacing.md,
  },
  settingGradient: {
    borderRadius: BorderRadius.md,
    padding: Spacing.lg,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  settingIcon: {
    marginRight: Spacing.md,
  },
  iconGradient: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  settingContent: {
    flex: 1,
  },
  settingTitle: {
    fontSize: Fonts.sizes.lg,
    fontWeight: '600',
    color: Colors.text,
    marginBottom: Spacing.xs,
  },
  settingSubtitle: {
    fontSize: Fonts.sizes.sm,
    color: Colors.textSecondary,
    lineHeight: 18,
  },
  settingAction: {
    marginLeft: Spacing.md,
  },
});