import React, { useState, useEffect, useRef } from 'react';
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
} from 'react-native';
import { GiftedChat, IMessage, Bubble, InputToolbar, Send } from 'react-native-gifted-chat';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { Audio } from 'expo-av';
import AudioRecorderPlayer from 'react-native-audio-recorder-player';
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

// Note: AudioRecorderPlayer needs to be properly initialized
// const audioRecorderPlayer = new AudioRecorderPlayer();

export default function ChatScreen({ route, navigation }: Props) {
  const { threadId } = route.params;
  const [messages, setMessages] = useState<IMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingPath, setRecordingPath] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [thread, setThread] = useState<Thread | null>(null);
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    loadThread();
    loadMessages();
    setupAudio();

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

  const setupAudio = async () => {
    try {
      await Audio.requestPermissionsAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });
    } catch (error) {
      console.error('Error setting up audio:', error);
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
    const formattedMessage = {
      _id: newMessage.id,
      text: newMessage.content,
      createdAt: new Date(newMessage.created_at),
      user: {
        _id: newMessage.role === 'user' ? 1 : 2,
        name: newMessage.role === 'user' ? 'You' : 'AI Surrogate',
        avatar: newMessage.role === 'user' ? undefined : 'https://via.placeholder.com/40x40/00FFFF/FFFFFF?text=AI',
      },
      audio: newMessage.audio_url,
    };

    setMessages((previousMessages) =>
      GiftedChat.append(previousMessages, [formattedMessage])
    );
    setIsTyping(false);
  };

  const sendMessage = async (messages: IMessage[]) => {
    const message = messages[0];
    setIsTyping(true);

    try {
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) return;

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

      // Send to backend API for AI response
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          thread_id: threadId,
          message: message.text,
          user_id: user.id,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get AI response');
      }

      // AI response will be handled by real-time subscription
    } catch (error: any) {
      console.error('Error sending message:', error);
      Alert.alert('Error', 'Failed to send message');
      setIsTyping(false);
    }
  };

  const startRecording = async () => {
    try {
      const path = `recording_${Date.now()}.m4a`;
      const result = await audioRecorderPlayer.startRecorder(path);
      setRecordingPath(result);
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      Alert.alert('Error', 'Failed to start recording');
    }
  };

  const stopRecording = async () => {
    try {
      const result = await audioRecorderPlayer.stopRecorder();
      setIsRecording(false);
      setRecordingPath('');

      // Send audio to backend for transcription
      const formData = new FormData();
      formData.append('audio', {
        uri: result,
        type: 'audio/m4a',
        name: 'recording.m4a',
      } as any);
      if (threadId) {
        formData.append('thread_id', threadId);
      }

      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        formData.append('user_id', user.id);
      }

      const response = await fetch('http://localhost:8000/voice', {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to process voice message');
      }

      setIsTyping(true);
    } catch (error: any) {
      console.error('Error stopping recording:', error);
      Alert.alert('Error', 'Failed to process voice message');
    }
  };

  const playAudio = async (audioUrl: string) => {
    try {
      if (isPlaying) {
        await audioRecorderPlayer.stopPlayer();
        setIsPlaying(false);
      } else {
        await audioRecorderPlayer.startPlayer(audioUrl);
        setIsPlaying(true);
        
        audioRecorderPlayer.addPlayBackListener((e: any) => {
          if (e.currentPosition === e.duration) {
            setIsPlaying(false);
          }
        });
      }
    } catch (error) {
      console.error('Error playing audio:', error);
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

  const renderAccessory = () => (
    <View style={styles.accessory}>
      <TouchableOpacity
        style={[styles.micButton, isRecording && styles.micButtonActive]}
        onPressIn={startRecording}
        onPressOut={stopRecording}
        activeOpacity={0.8}
      >
        <LinearGradient
          colors={isRecording ? [Colors.error, '#FF6B6B'] : [Colors.primary, Colors.secondary]}
          style={styles.micGradient}
        >
          <Ionicons 
            name={isRecording ? "stop" : "mic"} 
            size={24} 
            color={Colors.background} 
          />
        </LinearGradient>
      </TouchableOpacity>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
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
          renderAccessory={renderAccessory}
          isTyping={isTyping}
          messagesContainerStyle={styles.messagesContainer}
          // textInputStyle={styles.textInput}
          placeholder="Type a message or hold mic to record..."
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
  accessory: {
    height: 60,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: Colors.surface,
  },
  micButton: {
    width: 50,
    height: 50,
  },
  micButtonActive: {
    transform: [{ scale: 1.1 }],
  },
  micGradient: {
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
});