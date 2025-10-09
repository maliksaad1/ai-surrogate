import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Alert,
  KeyboardAvoidingView,
  Platform,
  FlatList,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { RouteProp } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';

import { Colors, Fonts, Spacing, BorderRadius } from '../constants/theme';
import { Message, Thread } from '../types';
import { supabase } from '../services/supabase';
import { RootStackParamList } from '../types';

type ChatScreenRouteProp = RouteProp<RootStackParamList, 'Chat'>;
type ChatScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Chat'>;

interface Props {
  route: ChatScreenRouteProp;
  navigation: ChatScreenNavigationProp;
}

interface ChatMessage {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

export default function ChatScreen({ route, navigation }: Props) {
  const { threadId } = route.params;
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(true);
  const [isTyping, setIsTyping] = useState(false);
  const [thread, setThread] = useState<Thread | null>(null);

  useEffect(() => {
    if (threadId) {
      loadThread();
      loadMessages();
    } else {
      createNewThread();
    }
  }, [threadId]);

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

      setThread(data);
      navigation.setOptions({ title: data.title });
      setLoading(false);
    } catch (error) {
      console.error('Error creating thread:', error);
      setLoading(false);
    }
  };

  const loadThread = async () => {
    try {
      const { data, error } = await supabase
        .from('threads')
        .select('*')
        .eq('id', threadId)
        .single();

      if (error) throw error;
      setThread(data);
      navigation.setOptions({ title: data.title });
    } catch (error) {
      console.error('Error loading thread:', error);
    }
  };

  const loadMessages = async () => {
    try {
      const { data, error } = await supabase
        .from('messages')
        .select('*')
        .eq('thread_id', threadId)
        .order('created_at', { ascending: true });

      if (error) throw error;

      const formattedMessages: ChatMessage[] = data.map((message: Message) => ({
        id: message.id,
        text: message.content,
        isUser: message.role === 'user',
        timestamp: new Date(message.created_at),
      }));

      setMessages(formattedMessages);
    } catch (error) {
      console.error('Error loading messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!inputText.trim() || !thread) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: inputText.trim(),
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);

    try {
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) return;

      // Save user message
      const { error: messageError } = await supabase
        .from('messages')
        .insert([
          {
            thread_id: thread.id,
            role: 'user',
            content: userMessage.text,
          },
        ]);

      if (messageError) throw messageError;

      // Simulate AI response (replace with actual API call)
      setTimeout(async () => {
        const aiMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          text: `I understand your message: "${userMessage.text}". This is a simulated response. The actual AI integration will be implemented in the backend.`,
          isUser: false,
          timestamp: new Date(),
        };

        setMessages(prev => [...prev, aiMessage]);
        setIsTyping(false);

        // Save AI response
        await supabase
          .from('messages')
          .insert([
            {
              thread_id: thread.id,
              role: 'assistant',
              content: aiMessage.text,
            },
          ]);
      }, 1500);

    } catch (error: any) {
      console.error('Error sending message:', error);
      Alert.alert('Error', 'Failed to send message');
      setIsTyping(false);
    }
  };

  const renderMessage = ({ item }: { item: ChatMessage }) => (
    <View style={[styles.messageContainer, item.isUser ? styles.userMessage : styles.aiMessage]}>
      {item.isUser ? (
        <View style={styles.userBubble}>
          <Text style={styles.userText}>{item.text}</Text>
        </View>
      ) : (
        <LinearGradient
          colors={[Colors.primary, Colors.secondary]}
          style={styles.aiBubble}
        >
          <Text style={styles.aiText}>{item.text}</Text>
        </LinearGradient>
      )}
      <Text style={styles.timestamp}>
        {item.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </Text>
    </View>
  );

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
      <KeyboardAvoidingView
        style={styles.keyboardView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 88 : 0}
      >
        <FlatList
          data={messages}
          renderItem={renderMessage}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.messagesContainer}
          showsVerticalScrollIndicator={false}
        />

        {isTyping && (
          <View style={styles.typingContainer}>
            <LinearGradient
              colors={[Colors.primary, Colors.secondary]}
              style={styles.typingBubble}
            >
              <Text style={styles.typingText}>AI is typing...</Text>
            </LinearGradient>
          </View>
        )}

        <View style={styles.inputContainer}>
          <TextInput
            style={styles.textInput}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Type a message..."
            placeholderTextColor={Colors.textSecondary}
            multiline
            maxLength={1000}
          />
          <TouchableOpacity
            style={styles.sendButton}
            onPress={sendMessage}
            disabled={!inputText.trim()}
            activeOpacity={0.8}
          >
            <LinearGradient
              colors={inputText.trim() ? [Colors.primary, Colors.secondary] : [Colors.textSecondary, Colors.textSecondary]}
              style={styles.sendGradient}
            >
              <Ionicons name="send" size={20} color={Colors.background} />
            </LinearGradient>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  keyboardView: {
    flex: 1,
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
  messagesContainer: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
  },
  messageContainer: {
    marginVertical: Spacing.xs,
    maxWidth: '80%',
  },
  userMessage: {
    alignSelf: 'flex-end',
    alignItems: 'flex-end',
  },
  aiMessage: {
    alignSelf: 'flex-start',
    alignItems: 'flex-start',
  },
  userBubble: {
    backgroundColor: Colors.userBubble,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    borderRadius: BorderRadius.md,
    borderTopRightRadius: BorderRadius.sm,
  },
  aiBubble: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    borderRadius: BorderRadius.md,
    borderTopLeftRadius: BorderRadius.sm,
  },
  userText: {
    color: Colors.text,
    fontSize: Fonts.sizes.md,
    lineHeight: 20,
  },
  aiText: {
    color: Colors.background,
    fontSize: Fonts.sizes.md,
    lineHeight: 20,
  },
  timestamp: {
    color: Colors.textSecondary,
    fontSize: Fonts.sizes.xs,
    marginTop: Spacing.xs,
  },
  typingContainer: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
  },
  typingBubble: {
    alignSelf: 'flex-start',
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    borderRadius: BorderRadius.md,
    borderTopLeftRadius: BorderRadius.sm,
  },
  typingText: {
    color: Colors.background,
    fontSize: Fonts.sizes.sm,
    fontStyle: 'italic',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    backgroundColor: Colors.surface,
    borderTopWidth: 1,
    borderTopColor: Colors.primary + '30',
  },
  textInput: {
    flex: 1,
    backgroundColor: Colors.background,
    borderWidth: 1,
    borderColor: Colors.primary + '30',
    borderRadius: BorderRadius.lg,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    marginRight: Spacing.sm,
    color: Colors.text,
    fontSize: Fonts.sizes.md,
    maxHeight: 120,
  },
  sendButton: {
    width: 44,
    height: 44,
  },
  sendGradient: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 4,
  },
});