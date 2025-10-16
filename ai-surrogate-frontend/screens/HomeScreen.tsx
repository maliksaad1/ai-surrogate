import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Alert,
  RefreshControl,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { StackNavigationProp } from '@react-navigation/stack';
import { CompositeNavigationProp } from '@react-navigation/native';
import { BottomTabNavigationProp } from '@react-navigation/bottom-tabs';

import { Colors, Fonts, Spacing, BorderRadius } from '../constants/theme';
import { Thread } from '../types';
import { supabase } from '../services/supabase';
import { RootStackParamList, MainTabParamList } from '../types';

type HomeScreenNavigationProp = CompositeNavigationProp<
  BottomTabNavigationProp<MainTabParamList, 'Home'>,
  StackNavigationProp<RootStackParamList>
>;

interface Props {
  navigation: HomeScreenNavigationProp;
}

export default function HomeScreen({ navigation }: Props) {
  const [threads, setThreads] = useState<Thread[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadThreads = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) {
        navigation.navigate('Auth');
        return;
      }

      const { data, error } = await supabase
        .from('threads')
        .select(`
          *,
          messages(content, created_at)
        `)
        .eq('user_id', user.id)
        .order('last_message_at', { ascending: false });

      if (error) throw error;

      setThreads(data || []);
    } catch (error: any) {
      Alert.alert('Error', 'Failed to load conversations');
      console.error('Error loading threads:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadThreads();
  };

  useFocusEffect(
    useCallback(() => {
      loadThreads();
    }, [])
  );

  const createNewThread = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) {
        navigation.navigate('Auth');
        return;
      }

      const { data, error } = await supabase
        .from('threads')
        .insert([
          {
            user_id: user.id,
            title: 'New Chat',
          },
        ])
        .select()
        .single();

      if (error) throw error;

      navigation.navigate('Chat', { threadId: data.id });
    } catch (error: any) {
      Alert.alert('Error', 'Failed to create new chat');
      console.error('Error creating thread:', error);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    if (diffInMinutes < 10080) return `${Math.floor(diffInMinutes / 1440)}d ago`;
    
    return date.toLocaleDateString();
  };

  const getLastMessage = (thread: Thread) => {
    if (thread.messages && thread.messages.length > 0) {
      const lastMessage = thread.messages[0];
      return lastMessage.content.length > 50 
        ? lastMessage.content.substring(0, 50) + '...'
        : lastMessage.content;
    }
    return 'No messages yet';
  };

  const deleteThread = async (threadId: string) => {
    Alert.alert(
      'Delete Chat',
      'Are you sure you want to delete this conversation? This action cannot be undone.',
      [
        {
          text: 'No',
          style: 'cancel',
        },
        {
          text: 'Yes',
          style: 'destructive',
          onPress: async () => {
            try {
              // Delete all messages in the thread first
              const { error: messagesError } = await supabase
                .from('messages')
                .delete()
                .eq('thread_id', threadId);

              if (messagesError) throw messagesError;

              // Then delete the thread
              const { error: threadError } = await supabase
                .from('threads')
                .delete()
                .eq('id', threadId);

              if (threadError) throw threadError;

              // Refresh the thread list
              loadThreads();
              
              Alert.alert('Success', 'Chat deleted successfully');
            } catch (error: any) {
              Alert.alert('Error', 'Failed to delete chat');
              console.error('Error deleting thread:', error);
            }
          },
        },
      ],
      { cancelable: true }
    );
  };

  const renderThread = ({ item }: { item: Thread }) => (
    <View style={styles.threadItem}>
      <TouchableOpacity
        style={styles.threadTouchable}
        onPress={() => navigation.navigate('Chat', { threadId: item.id })}
        activeOpacity={0.7}
      >
        <LinearGradient
          colors={[Colors.surface, Colors.surface + '80']}
          style={styles.threadGradient}
        >
          <View style={styles.threadContent}>
            <View style={styles.threadHeader}>
              <Text style={styles.threadTitle}>{item.title}</Text>
              <Text style={styles.threadTime}>
                {formatDate(item.last_message_at)}
              </Text>
            </View>
            <Text style={styles.threadPreview}>
              {getLastMessage(item)}
            </Text>
          </View>
          <View style={styles.threadIndicator}>
            <LinearGradient
              colors={[Colors.primary, Colors.secondary]}
              style={styles.indicator}
            />
          </View>
        </LinearGradient>
      </TouchableOpacity>
      
      {/* Delete Button */}
      <TouchableOpacity
        style={styles.deleteButton}
        onPress={() => deleteThread(item.id)}
        activeOpacity={0.7}
      >
        <LinearGradient
          colors={['#FF4444', '#CC0000']}
          style={styles.deleteGradient}
        >
          <Ionicons name="trash-outline" size={20} color={Colors.background} />
        </LinearGradient>
      </TouchableOpacity>
    </View>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <LinearGradient
        colors={[Colors.primary, Colors.secondary]}
        style={styles.emptyIcon}
      >
        <Ionicons name="chatbubbles-outline" size={48} color={Colors.background} />
      </LinearGradient>
      <Text style={styles.emptyTitle}>No Conversations Yet</Text>
      <Text style={styles.emptySubtitle}>
        Start your first conversation with your AI companion
      </Text>
      <TouchableOpacity style={styles.emptyButton} onPress={createNewThread}>
        <LinearGradient
          colors={[Colors.primary, Colors.secondary]}
          style={styles.emptyButtonGradient}
        >
          <Text style={styles.emptyButtonText}>Start Chatting</Text>
        </LinearGradient>
      </TouchableOpacity>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>AI Surrogate</Text>
        <TouchableOpacity style={styles.headerButton}>
          <Ionicons name="notifications-outline" size={24} color={Colors.primary} />
        </TouchableOpacity>
      </View>

      {threads.length === 0 && !loading ? (
        renderEmptyState()
      ) : (
        <FlatList
          data={threads}
          renderItem={renderThread}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContainer}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor={Colors.primary}
              colors={[Colors.primary]}
            />
          }
          showsVerticalScrollIndicator={false}
        />
      )}

      {/* Floating Action Button */}
      <TouchableOpacity
        style={styles.fab}
        onPress={createNewThread}
        activeOpacity={0.8}
      >
        <LinearGradient
          colors={[Colors.primary, Colors.secondary]}
          style={styles.fabGradient}
        >
          <Ionicons name="add" size={28} color={Colors.background} />
        </LinearGradient>
      </TouchableOpacity>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: Colors.surface,
  },
  headerTitle: {
    fontSize: Fonts.sizes.xl,
    fontWeight: 'bold',
    color: Colors.text,
  },
  headerButton: {
    padding: Spacing.sm,
  },
  listContainer: {
    padding: Spacing.md,
  },
  threadItem: {
    marginBottom: Spacing.md,
    position: 'relative',
  },
  threadTouchable: {
    flex: 1,
  },
  threadGradient: {
    borderRadius: BorderRadius.md,
    padding: Spacing.lg,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  threadContent: {
    flex: 1,
  },
  threadHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.xs,
  },
  threadTitle: {
    fontSize: Fonts.sizes.lg,
    fontWeight: '600',
    color: Colors.text,
    flex: 1,
  },
  threadTime: {
    fontSize: Fonts.sizes.sm,
    color: Colors.textSecondary,
  },
  threadPreview: {
    fontSize: Fonts.sizes.sm,
    color: Colors.textSecondary,
    lineHeight: 20,
  },
  threadIndicator: {
    marginLeft: Spacing.md,
  },
  indicator: {
    width: 4,
    height: 40,
    borderRadius: 2,
  },
  deleteButton: {
    position: 'absolute',
    top: 8,
    right: 8,
    zIndex: 10,
  },
  deleteGradient: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#FF0000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 4,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: Spacing.xl,
  },
  emptyIcon: {
    width: 120,
    height: 120,
    borderRadius: 60,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.xl,
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
  },
  emptyTitle: {
    fontSize: Fonts.sizes.xl,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: Spacing.sm,
    textAlign: 'center',
  },
  emptySubtitle: {
    fontSize: Fonts.sizes.md,
    color: Colors.textSecondary,
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: Spacing.xl,
  },
  emptyButton: {
    marginTop: Spacing.lg,
  },
  emptyButtonGradient: {
    paddingVertical: Spacing.lg,
    paddingHorizontal: Spacing.xl,
    borderRadius: BorderRadius.md,
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 6,
  },
  emptyButtonText: {
    fontSize: Fonts.sizes.lg,
    fontWeight: 'bold',
    color: Colors.background,
  },
  fab: {
    position: 'absolute',
    bottom: Spacing.xl,
    right: Spacing.xl,
    zIndex: 1000,
  },
  fabGradient: {
    width: 64,
    height: 64,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 16,
    elevation: 8,
  },
});