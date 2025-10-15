import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { GiftedChat, IMessage, Bubble, InputToolbar, Send } from 'react-native-gifted-chat';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { RouteProp } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';

import { Colors, Fonts, Spacing, BorderRadius } from '../constants/theme';
import { Message, Thread } from '../types';
import { supabase } from '../services/supabase';
import { RootStackParamList } from '../types';
import { API_BASE_URL } from '../config/api';

type ChatScreenRouteProp = RouteProp<RootStackParamList, 'Chat'>;
type ChatScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Chat'>;

interface Props {
  route: ChatScreenRouteProp;
  navigation: ChatScreenNavigationProp;
}

export default function ChatScreen({ route, navigation }: Props) {
  const { threadId } = route.params;
  const [messages, setMessages] = useState<IMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [thread, setThread] = useState<Thread | null>(null);
  const [isTyping, setIsTyping] = useState(false);
  const [activeAgent, setActiveAgent] = useState<{name: string, icon: string} | null>(null);

  useEffect(() => {
    loadThread();
    loadMessages();

    // Subscribe to real-time message updates
    const subscription = supabase
      .channel('messages')
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'messages',
          filter: `thread_id=eq.${threadId}`,
        },
        handleNewMessage
      )
      .subscribe();

    return () => {
      subscription.unsubscribe();
    };
  }, [threadId]);

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
        .order('created_at', { ascending: false });

      if (error) throw error;

      const formattedMessages = data.map((message: Message) => ({
        _id: message.id,
        text: message.content,
        createdAt: new Date(message.created_at),
        user: {
          _id: message.role === 'user' ? 1 : 2,
          name: message.role === 'user' ? 'You' : 'AI Surrogate',
          avatar: message.role === 'user' ? undefined : 'https://via.placeholder.com/40x40/00FFFF/FFFFFF?text=AI',
        },
        audio: message.audio_url,
      }));

      setMessages(formattedMessages);
    } catch (error) {
      console.error('Error loading messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNewMessage = (payload: any) => {
    const newMessage = payload.new;
    
    // Extract agent information from metadata if available
    let agentInfo = null;
    if (newMessage.metadata) {
      try {
        const metadata = typeof newMessage.metadata === 'string' 
          ? JSON.parse(newMessage.metadata) 
          : newMessage.metadata;
        
        if (metadata.agent_display_name && metadata.agent_icon) {
          agentInfo = {
            name: metadata.agent_display_name,
            icon: metadata.agent_icon,
            agent: metadata.primary_agent
          };
        }
      } catch (e) {
        console.error('Error parsing metadata:', e);
      }
    }
    
    const formattedMessage = {
      _id: newMessage.id,
      text: newMessage.content,
      createdAt: new Date(newMessage.created_at),
      user: {
        _id: newMessage.role === 'user' ? 1 : 2,
        name: newMessage.role === 'user' ? 'You' : (agentInfo?.name || 'AI Surrogate'),
        avatar: newMessage.role === 'user' ? undefined : 'https://via.placeholder.com/40x40/00FFFF/FFFFFF?text=AI',
      },
      audio: newMessage.audio_url,
      metadata: agentInfo,
    };

    setMessages((previousMessages) =>
      GiftedChat.append(previousMessages, [formattedMessage])
    );
    setIsTyping(false);
    setActiveAgent(null);  // Clear active agent when response is received
  };

  const sendMessage = async (messages: IMessage[]) => {
    const message = messages[0];
    setIsTyping(true);
    setActiveAgent({name: 'Analyzing', icon: '🔍'});  // Show analyzing status

    try {
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session || !session.user) {
        Alert.alert('Error', 'Please log in to send messages');
        setIsTyping(false);
        setActiveAgent(null);
        return;
      }

      const user = session.user;

      // Save user message
      const { error: messageError } = await supabase
        .from('messages')
        .insert([
          {
            thread_id: threadId,
            role: 'user',
            content: message.text,
          },
        ]);

      if (messageError) throw messageError;

      // Update status to show processing
      setActiveAgent({name: 'Processing', icon: '⚙️'});

      // Send to backend API for AI response with auth token
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          thread_id: threadId,
          message: message.text,
          user_id: user.id,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to get AI response' }));
        throw new Error(errorData.detail || 'Failed to get AI response');
      }
      
      // Try to extract agent info from response
      try {
        const responseData = await response.json();
        if (responseData.metadata) {
          setActiveAgent({
            name: responseData.metadata.agent_display_name || 'AI Assistant',
            icon: responseData.metadata.agent_icon || '🤖'
          });
        }
      } catch (e) {
        // Response already consumed or not JSON
        console.log('Could not parse response for agent info');
      }

      // AI response will be handled by real-time subscription
    } catch (error: any) {
      console.error('Error sending message:', error);
      Alert.alert('Error', error.message || 'Failed to send message');
      setIsTyping(false);
      setActiveAgent(null);
    }
  };

  const renderBubble = (props: any) => (
    <Bubble
      {...props}
      wrapperStyle={{
        right: {
          backgroundColor: Colors.userBubble,
          borderTopRightRadius: BorderRadius.sm,
        },
        left: {
          backgroundColor: 'transparent',
          borderTopLeftRadius: BorderRadius.sm,
        },
      }}
      renderMessageText={(textProps: any) => {
        if (textProps.currentMessage.user._id === 2) {
          return (
            <LinearGradient
              colors={[Colors.primary, Colors.secondary]}
              style={styles.aiBubble}
            >
              <Text style={[textProps.textStyle, { color: Colors.background }]}>
                {textProps.currentMessage.text}
              </Text>
            </LinearGradient>
          );
        }
        return (
          <Text style={[textProps.textStyle, { color: Colors.text }]}>
            {textProps.currentMessage.text}
          </Text>
        );
      }}
    />
  );

  const renderInputToolbar = (props: any) => (
    <InputToolbar
      {...props}
      containerStyle={styles.inputToolbar}
      primaryStyle={styles.inputPrimary}
    />
  );

  const renderSend = (props: any) => (
    <Send {...props}>
      <View style={styles.sendButton}>
        <Ionicons name="send" size={20} color={Colors.primary} />
      </View>
    </Send>
  );

  return (
    <SafeAreaView style={styles.container}>
      {/* Agent Status Indicator */}
      {activeAgent && (
        <View style={styles.agentStatus}>
          <LinearGradient
            colors={[Colors.primary, Colors.secondary]}
            style={styles.agentStatusGradient}
            start={{x: 0, y: 0}}
            end={{x: 1, y: 0}}
          >
            <Text style={styles.agentIcon}>{activeAgent.icon}</Text>
            <Text style={styles.agentName}>{activeAgent.name} is working...</Text>
            <View style={styles.loadingDots}>
              <View style={[styles.dot, styles.dot1]} />
              <View style={[styles.dot, styles.dot2]} />
              <View style={[styles.dot, styles.dot3]} />
            </View>
          </LinearGradient>
        </View>
      )}
      
      <KeyboardAvoidingView
        style={styles.keyboardView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 88 : 0}
      >
        <GiftedChat
          messages={messages}
          onSend={sendMessage}
          user={{ _id: 1 }}
          renderBubble={renderBubble}
          renderInputToolbar={renderInputToolbar}
          renderSend={renderSend}
          isTyping={isTyping}
          messagesContainerStyle={styles.messagesContainer}
          placeholder="Type a message..."
        />
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
  messagesContainer: {
    backgroundColor: Colors.background,
  },
  aiBubble: {
    padding: Spacing.md,
    borderRadius: BorderRadius.md,
    borderTopLeftRadius: BorderRadius.sm,
  },
  inputToolbar: {
    backgroundColor: Colors.surface,
    borderTopColor: Colors.primary + '30',
    paddingVertical: Spacing.xs,
  },
  inputPrimary: {
    alignItems: 'center',
  },
  textInput: {
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.primary + '30',
    borderRadius: BorderRadius.lg,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    marginHorizontal: Spacing.sm,
    color: Colors.text,
    fontSize: Fonts.sizes.md,
  },
  sendButton: {
    marginRight: Spacing.md,
    marginBottom: Spacing.sm,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: Colors.surface,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: Colors.primary + '30',
  },
  agentStatus: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 1000,
  },
  agentStatusGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.md,
  },
  agentIcon: {
    fontSize: 20,
    marginRight: Spacing.xs,
  },
  agentName: {
    color: Colors.background,
    fontSize: Fonts.sizes.sm,
    fontWeight: '600',
    marginRight: Spacing.xs,
  },
  loadingDots: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: Colors.background,
    marginHorizontal: 2,
  },
  dot1: {
    opacity: 0.4,
  },
  dot2: {
    opacity: 0.7,
  },
  dot3: {
    opacity: 1,
  },
});