import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';

import { Theme, Colors } from './constants/theme';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { RootStackParamList, MainTabParamList } from './types';

// Screens
import OnboardingScreen from './screens/OnboardingScreen';
import AuthScreen from './screens/AuthScreen';
import HomeScreen from './screens/HomeScreen';
import ChatScreen from './screens/ChatScreenSimple';
import SettingsScreen from './screens/SettingsScreen';
import ProfileScreen from './screens/ProfileScreen';

const Stack = createStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<MainTabParamList>();

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          if (route.name === 'Home') {
            iconName = focused ? 'chatbubbles' : 'chatbubbles-outline';
          } else if (route.name === 'Settings') {
            iconName = focused ? 'settings' : 'settings-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline';
          } else {
            iconName = 'help-circle-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: Colors.primary,
        tabBarInactiveTintColor: Colors.textSecondary,
        tabBarStyle: {
          backgroundColor: Colors.surface,
          borderTopColor: Colors.primary,
          borderTopWidth: 1,
        },
        headerStyle: {
          backgroundColor: Colors.background,
        },
        headerTintColor: Colors.text,
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{ title: 'Chats' }}
      />
      <Tab.Screen 
        name="Settings" 
        component={SettingsScreen}
        options={{ title: 'Settings' }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{ title: 'Profile' }}
      />
    </Tab.Navigator>
  );
}

function Navigation() {
  const { session, loading } = useAuth();

  if (loading) {
    return null; // Or a loading screen
  }

  return (
    <NavigationContainer theme={Theme}>
      <StatusBar style="light" backgroundColor={Colors.background} />
      <Stack.Navigator
        screenOptions={{
          headerStyle: {
            backgroundColor: Colors.background,
          },
          headerTintColor: Colors.text,
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        {session ? (
          // Authenticated stack
          <>
            <Stack.Screen 
              name="Main" 
              component={MainTabs}
              options={{ headerShown: false }}
            />
            <Stack.Screen 
              name="Chat" 
              component={ChatScreen}
              options={{ 
                title: 'AI Surrogate',
              }}
            />
          </>
        ) : (
          // Unauthenticated stack
          <>
            <Stack.Screen 
              name="Onboarding" 
              component={OnboardingScreen}
              options={{ headerShown: false }}
            />
            <Stack.Screen 
              name="Auth" 
              component={AuthScreen}
              options={{ headerShown: false }}
            />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Navigation />
    </AuthProvider>
  );
}
