import React, { useState } from 'react';
import { View, Text, TextInput, Alert } from 'react-native';
import { formStyles } from '../../theme/formStyles';
import LoadingButton from '../../components/common/LoadingButton';
import { schedulePatient } from '../../api/endpoints';
import { useAppDispatch } from '../../hooks/useRedux';
import { setOnboardingCompleted } from '../../store/slices/authSlice';
import { setActivePatient } from '../../store/slices/patientSlice';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { OnboardingStackParamList } from '../../types/navigation';

type Props = NativeStackScreenProps<OnboardingStackParamList, 'Step3'>;

export default function Step3ScheduleScreen({ route }: Props) {
  const { patient_id } = route.params;
  const dispatch = useAppDispatch();
  const [callTime, setCallTime] = useState('');
  const [loading, setLoading] = useState(false);

  const handleFinish = async () => {
    if (!callTime) {
      Alert.alert('Error', 'Please enter a preferred call time');
      return;
    }
    setLoading(true);
    try {
      await schedulePatient({
        patient_id,
        preferred_call_time: callTime,
      });
      // Set active patient and finish onboarding
      dispatch(setActivePatient(patient_id));
      dispatch(setOnboardingCompleted(true));
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to update schedule');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={formStyles.screenContainer}>
      <Text style={formStyles.progress}>Step 3 of 3</Text>
      <Text style={formStyles.title}>Set Call Schedule</Text>
      <Text style={formStyles.subtitle}>When should ClaraCare call your loved one?</Text>

      <View style={formStyles.card}>
        <Text style={formStyles.label}>Preferred Call Time *</Text>
        <TextInput 
          style={formStyles.input} 
          placeholder="e.g., 10:00 AM" 
          value={callTime} 
          onChangeText={setCallTime} 
        />

        <View style={formStyles.footer}>
          <LoadingButton 
            title="Complete Setup" 
            onPress={handleFinish} 
            loading={loading} 
          />
        </View>
      </View>
    </View>
  );
}

