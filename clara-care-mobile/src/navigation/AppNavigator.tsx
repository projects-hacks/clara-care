import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { ActivityIndicator, View } from 'react-native';

import { useAppSelector, useAppDispatch } from '../hooks/useRedux';
import { setAuthSession, setOnboardingCompleted } from '../store/slices/authSlice';
import { fetchPatients } from '../store/slices/patientSlice';
import { supabase } from '../api/supabase';
import { colors } from '../theme';

import LoginScreen from '../screens/auth/LoginScreen';
import SignupScreen from '../screens/auth/SignupScreen';
import MainTabs from './MainTabs';
import OnboardingNavigator from './OnboardingNavigator';
import { RootStackParamList } from '../types/navigation';

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function AppNavigator() {
  const dispatch = useAppDispatch();
  const { isAuthenticated, isInitializing, onboardingCompleted } = useAppSelector((state) => state.auth);

  useEffect(() => {
    // Check active session
    supabase.auth.getSession().then(({ data: { session } }) => {
      dispatch(setAuthSession({ user: session?.user ?? null }));
      if (session?.user) {
        dispatch(fetchPatients()).then((result: any) => {
          if (result.payload && result.payload.length > 0) {
            dispatch(setOnboardingCompleted(true));
          }
        });
      }
    });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      dispatch(setAuthSession({ user: session?.user ?? null }));
    });

    return () => subscription.unsubscribe();
  }, [dispatch]);

  if (isInitializing) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isAuthenticated ? (
          onboardingCompleted ? (
            <Stack.Screen name="Main" component={MainTabs} />
          ) : (
            <Stack.Screen name="Onboarding" component={OnboardingNavigator} />
          )
        ) : (
          <>
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="Signup" component={SignupScreen} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
