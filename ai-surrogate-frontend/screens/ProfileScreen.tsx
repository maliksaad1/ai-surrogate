import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Alert,
  ScrollView,
  TextInput,
  Modal,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { BottomTabNavigationProp } from '@react-navigation/bottom-tabs';

import { Colors, Fonts, Spacing, BorderRadius } from '../constants/theme';
import { supabase } from '../services/supabase';
import { MainTabParamList, User } from '../types';

type ProfileScreenNavigationProp = BottomTabNavigationProp<MainTabParamList, 'Profile'>;

interface Props {
  navigation: ProfileScreenNavigationProp;
}

interface Stat {
  label: string;
  value: string;
  icon: keyof typeof Ionicons.glyphMap;
  color: [string, string];
}

export default function ProfileScreen({ navigation }: Props) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editName, setEditName] = useState('');
  const [conversationCount, setConversationCount] = useState(0);
  const [messageCount, setMessageCount] = useState(0);

  useEffect(() => {
    loadUserProfile();
    loadStats();
  }, []);

  const loadUserProfile = async () => {
    try {
      const { data: { user: authUser } } = await supabase.auth.getUser();
      
      if (!authUser) return;

      const { data, error } = await supabase
        .from('users')
        .select('*')
        .eq('id', authUser.id)
        .single();

      if (error) throw error;
      
      setUser(data);
      setEditName(data.name || '');
    } catch (error) {
      console.error('Error loading user profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const { data: { user: authUser } } = await supabase.auth.getUser();
      
      if (!authUser) return;

      // Get conversation count
      const { count: threadCount } = await supabase
        .from('threads')
        .select('*', { count: 'exact', head: true })
        .eq('user_id', authUser.id);

      // Get message count
      const { count: msgCount } = await supabase
        .from('messages')
        .select('*', { count: 'exact', head: true })
        .in('thread_id', (await supabase
          .from('threads')
          .select('id')
          .eq('user_id', authUser.id)
        ).data?.map(t => t.id) || []);

      setConversationCount(threadCount || 0);
      setMessageCount(msgCount || 0);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const saveProfile = async () => {
    if (!user) return;

    try {
      const { error } = await supabase
        .from('users')
        .update({ name: editName })
        .eq('id', user.id);

      if (error) throw error;

      setUser({ ...user, name: editName });
      setEditModalVisible(false);
      Alert.alert('Success', 'Profile updated successfully');
    } catch (error: any) {
      Alert.alert('Error', 'Failed to update profile');
    }
  };

  const stats: Stat[] = [
    {
      label: 'Conversations',
      value: conversationCount.toString(),
      icon: 'chatbubbles',
      color: [Colors.primary, Colors.secondary],
    },
    {
      label: 'Messages',
      value: messageCount.toString(),
      icon: 'chatbox',
      color: [Colors.secondary, Colors.primary],
    },
    {
      label: 'Days Active',
      value: user ? Math.floor((Date.now() - new Date(user.created_at).getTime()) / (1000 * 60 * 60 * 24)).toString() : '0',
      icon: 'calendar',
      color: [Colors.success, '#00FF88'],
    },
    {
      label: 'Mood Score',
      value: '😊 Positive',
      icon: 'happy',
      color: [Colors.warning, '#FFD700'],
    },
  ];

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContainer} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.avatarContainer}>
            <LinearGradient
              colors={[Colors.primary, Colors.secondary]}
              style={styles.avatar}
            >
              <Text style={styles.avatarText}>
                {user?.name ? user.name.charAt(0).toUpperCase() : user?.email.charAt(0).toUpperCase()}
              </Text>
            </LinearGradient>
            <View style={styles.statusIndicator}>
              <LinearGradient
                colors={[Colors.success, Colors.success]}
                style={styles.statusDot}
              />
            </View>
          </View>

          <Text style={styles.userName}>{user?.name || 'User'}</Text>
          <Text style={styles.userEmail}>{user?.email}</Text>

          <TouchableOpacity
            style={styles.editButton}
            onPress={() => setEditModalVisible(true)}
            activeOpacity={0.8}
          >
            <LinearGradient
              colors={[Colors.primary, Colors.secondary]}
              style={styles.editGradient}
            >
              <Ionicons name="create" size={16} color={Colors.background} />
              <Text style={styles.editText}>Edit Profile</Text>
            </LinearGradient>
          </TouchableOpacity>
        </View>

        {/* Stats Grid */}
        <View style={styles.statsContainer}>
          <Text style={styles.sectionTitle}>Your Journey</Text>
          <View style={styles.statsGrid}>
            {stats.map((stat, index) => (
              <View key={index} style={styles.statCard}>
                <LinearGradient
                  colors={[Colors.surface, Colors.surface + '80']}
                  style={styles.statGradient}
                >
                  <LinearGradient
                    colors={stat.color as [string, string]}
                    style={styles.statIcon}
                  >
                    <Ionicons name={stat.icon} size={24} color={Colors.background} />
                  </LinearGradient>
                  <Text style={styles.statValue}>{stat.value}</Text>
                  <Text style={styles.statLabel}>{stat.label}</Text>
                </LinearGradient>
              </View>
            ))}
          </View>
        </View>

        {/* Quick Actions */}
        <View style={styles.actionsContainer}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          
          <TouchableOpacity
            style={styles.actionItem}
            onPress={() => Alert.alert('Coming Soon', 'Export conversations feature will be available in a future update')}
            activeOpacity={0.7}
          >
            <LinearGradient
              colors={[Colors.surface, Colors.surface + '80']}
              style={styles.actionGradient}
            >
              <Ionicons name="download" size={20} color={Colors.primary} />
              <Text style={styles.actionText}>Export Conversations</Text>
              <Ionicons name="chevron-forward" size={20} color={Colors.textSecondary} />
            </LinearGradient>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionItem}
            onPress={() => Alert.alert('Coming Soon', 'Memory management feature will be available in a future update')}
            activeOpacity={0.7}
          >
            <LinearGradient
              colors={[Colors.surface, Colors.surface + '80']}
              style={styles.actionGradient}
            >
              <Ionicons name="archive" size={20} color={Colors.primary} />
              <Text style={styles.actionText}>Manage Memory</Text>
              <Ionicons name="chevron-forward" size={20} color={Colors.textSecondary} />
            </LinearGradient>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionItem}
            onPress={() => Alert.alert('Coming Soon', 'Backup feature will be available in a future update')}
            activeOpacity={0.7}
          >
            <LinearGradient
              colors={[Colors.surface, Colors.surface + '80']}
              style={styles.actionGradient}
            >
              <Ionicons name="cloud-upload" size={20} color={Colors.primary} />
              <Text style={styles.actionText}>Backup Data</Text>
              <Ionicons name="chevron-forward" size={20} color={Colors.textSecondary} />
            </LinearGradient>
          </TouchableOpacity>
        </View>
      </ScrollView>

      {/* Edit Profile Modal */}
      <Modal
        visible={editModalVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setEditModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContainer}>
            <LinearGradient
              colors={[Colors.surface, Colors.background]}
              style={styles.modalGradient}
            >
              <Text style={styles.modalTitle}>Edit Profile</Text>
              
              <TextInput
                style={styles.modalInput}
                value={editName}
                onChangeText={setEditName}
                placeholder="Enter your name"
                placeholderTextColor={Colors.textSecondary}
              />

              <View style={styles.modalButtons}>
                <TouchableOpacity
                  style={styles.modalButton}
                  onPress={() => setEditModalVisible(false)}
                >
                  <Text style={styles.cancelButtonText}>Cancel</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.modalButton}
                  onPress={saveProfile}
                >
                  <LinearGradient
                    colors={[Colors.primary, Colors.secondary]}
                    style={styles.saveButtonGradient}
                  >
                    <Text style={styles.saveButtonText}>Save</Text>
                  </LinearGradient>
                </TouchableOpacity>
              </View>
            </LinearGradient>
          </View>
        </View>
      </Modal>
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: Colors.text,
    fontSize: Fonts.sizes.lg,
  },
  header: {
    alignItems: 'center',
    paddingVertical: Spacing.xl,
    paddingHorizontal: Spacing.lg,
  },
  avatarContainer: {
    position: 'relative',
    marginBottom: Spacing.lg,
  },
  avatar: {
    width: 120,
    height: 120,
    borderRadius: 60,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 16,
    elevation: 8,
  },
  avatarText: {
    fontSize: 48,
    fontWeight: 'bold',
    color: Colors.background,
  },
  statusIndicator: {
    position: 'absolute',
    bottom: 8,
    right: 8,
  },
  statusDot: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 3,
    borderColor: Colors.background,
  },
  userName: {
    fontSize: Fonts.sizes.xxl,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: Spacing.xs,
  },
  userEmail: {
    fontSize: Fonts.sizes.md,
    color: Colors.textSecondary,
    marginBottom: Spacing.lg,
  },
  editButton: {
    marginTop: Spacing.sm,
  },
  editGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.lg,
    borderRadius: BorderRadius.md,
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  editText: {
    color: Colors.background,
    fontSize: Fonts.sizes.sm,
    fontWeight: '600',
    marginLeft: Spacing.xs,
  },
  statsContainer: {
    paddingHorizontal: Spacing.lg,
    marginBottom: Spacing.xl,
  },
  sectionTitle: {
    fontSize: Fonts.sizes.lg,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: Spacing.lg,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statCard: {
    width: '48%',
    marginBottom: Spacing.md,
  },
  statGradient: {
    padding: Spacing.lg,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  statIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.sm,
  },
  statValue: {
    fontSize: Fonts.sizes.xl,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: Spacing.xs,
  },
  statLabel: {
    fontSize: Fonts.sizes.sm,
    color: Colors.textSecondary,
    textAlign: 'center',
  },
  actionsContainer: {
    paddingHorizontal: Spacing.lg,
  },
  actionItem: {
    marginBottom: Spacing.md,
  },
  actionGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: Spacing.lg,
    borderRadius: BorderRadius.md,
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  actionText: {
    flex: 1,
    fontSize: Fonts.sizes.md,
    color: Colors.text,
    marginLeft: Spacing.md,
    fontWeight: '500',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContainer: {
    width: '90%',
    maxWidth: 400,
    borderRadius: BorderRadius.lg,
    overflow: 'hidden',
  },
  modalGradient: {
    padding: Spacing.xl,
  },
  modalTitle: {
    fontSize: Fonts.sizes.xl,
    fontWeight: 'bold',
    color: Colors.text,
    textAlign: 'center',
    marginBottom: Spacing.lg,
  },
  modalInput: {
    backgroundColor: Colors.background,
    borderWidth: 1,
    borderColor: Colors.primary + '30',
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
    fontSize: Fonts.sizes.md,
    color: Colors.text,
    marginBottom: Spacing.lg,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  modalButton: {
    flex: 1,
    marginHorizontal: Spacing.xs,
  },
  cancelButtonText: {
    color: Colors.textSecondary,
    fontSize: Fonts.sizes.md,
    fontWeight: '600',
    textAlign: 'center',
    paddingVertical: Spacing.md,
  },
  saveButtonGradient: {
    paddingVertical: Spacing.md,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
  },
  saveButtonText: {
    color: Colors.background,
    fontSize: Fonts.sizes.md,
    fontWeight: '600',
  },
});