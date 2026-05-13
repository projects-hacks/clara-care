import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import Step1PatientScreen from '../screens/onboarding/Step1PatientScreen';
import Step2PersonalizeScreen from '../screens/onboarding/Step2PersonalizeScreen';
import Step3ScheduleScreen from '../screens/onboarding/Step3ScheduleScreen';
import { OnboardingStackParamList } from '../types/navigation';

const Stack = createNativeStackNavigator<OnboardingStackParamList>();

export default function OnboardingNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Step1" component={Step1PatientScreen} />
      <Stack.Screen name="Step2" component={Step2PersonalizeScreen} />
      <Stack.Screen name="Step3" component={Step3ScheduleScreen} />
    </Stack.Navigator>
  );
}
