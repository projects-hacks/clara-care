import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { colors } from '../theme';

import DashboardScreen from '../screens/dashboard/DashboardScreen';
import ConversationsScreen from '../screens/dashboard/ConversationsScreen';
import AlertsScreen from '../screens/dashboard/AlertsScreen';
import SettingsScreen from '../screens/settings/SettingsScreen';

const Tab = createBottomTabNavigator();

export default function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textSecondary,
        headerShown: true,
      }}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen} 
        options={{ title: 'Home' }}
      />
      <Tab.Screen 
        name="Conversations" 
        component={ConversationsScreen} 
        options={{ title: 'History' }}
      />
      <Tab.Screen 
        name="Alerts" 
        component={AlertsScreen} 
      />
      <Tab.Screen 
        name="Settings" 
        component={SettingsScreen} 
      />
    </Tab.Navigator>
  );
}
