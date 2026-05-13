import React, { useState } from 'react';
import { View, Text, TextInput, Alert } from 'react-native';
import { formStyles } from '../../theme/formStyles';
import LoadingButton from '../../components/common/LoadingButton';
import { createPatient } from '../../api/endpoints';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { OnboardingStackParamList } from '../../types/navigation';

type Props = NativeStackScreenProps<OnboardingStackParamList, 'Step1'>;

export default function Step1PatientScreen({ navigation }: Props) {
  const [name, setName] = useState('');
  const [preferredName, setPreferredName] = useState('');
  const [birthYear, setBirthYear] = useState('');
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);

  const handleNext = async () => {
    if (!name || !birthYear || !phone) {
      Alert.alert('Error', 'Please fill in the required fields');
      return;
    }
    setLoading(true);
    try {
      const { patient_id } = await createPatient({
        name,
        preferred_name: preferredName || name.split(' ')[0],
        birth_year: parseInt(birthYear),
        phone_number: phone,
      });
      navigation.navigate('Step2', { patient_id });
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to create patient');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={formStyles.screenContainer}>
      <Text style={formStyles.progress}>Step 1 of 3</Text>
      <Text style={formStyles.title}>Who are we caring for?</Text>
      <Text style={formStyles.subtitle}>Let's set up a profile for your loved one.</Text>

      <View style={formStyles.card}>
        <Text style={formStyles.label}>Full Name *</Text>
        <TextInput style={formStyles.input} placeholder="e.g., Dorothy Smith" value={name} onChangeText={setName} />

        <Text style={formStyles.label}>Preferred Name</Text>
        <TextInput style={formStyles.input} placeholder="e.g., Dot" value={preferredName} onChangeText={setPreferredName} />

        <Text style={formStyles.label}>Birth Year *</Text>
        <TextInput style={formStyles.input} placeholder="e.g., 1950" keyboardType="number-pad" value={birthYear} onChangeText={setBirthYear} />

        <Text style={formStyles.label}>Phone Number *</Text>
        <TextInput style={formStyles.input} placeholder="e.g., +1234567890" keyboardType="phone-pad" value={phone} onChangeText={setPhone} />

        <View style={formStyles.footer}>
          <LoadingButton 
            title="Next Step" 
            onPress={handleNext} 
            loading={loading} 
          />
        </View>
      </View>
    </View>
  );
}

