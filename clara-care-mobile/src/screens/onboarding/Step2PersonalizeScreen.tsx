import React, { useState } from 'react';
import {
  View, Text, TextInput, Alert,
  KeyboardAvoidingView, TouchableWithoutFeedback, Keyboard, Platform, ScrollView,
} from 'react-native';
import { formStyles } from '../../theme/formStyles';
import { colors } from '../../theme';
import LoadingButton from '../../components/common/LoadingButton';
import { personalizePatient } from '../../api/endpoints';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { OnboardingStackParamList } from '../../types/navigation';

type Props = NativeStackScreenProps<OnboardingStackParamList, 'Step2'>;

export default function Step2PersonalizeScreen({ route, navigation }: Props) {
  const { patient_id } = route.params;
  const [topics, setTopics] = useState('');
  const [loading, setLoading] = useState(false);

  const handleNext = async () => {
    setLoading(true);
    try {
      await personalizePatient({
        patient_id,
        favorite_topics: topics.split(',').map(t => t.trim()).filter(Boolean),
      });
      navigation.navigate('Step3', { patient_id });
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to update preferences');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={{ flex: 1 }}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
        <ScrollView
          contentContainerStyle={[formStyles.screenContainer, { flexGrow: 1 }]}
          keyboardShouldPersistTaps="handled"
        >
          <Text style={formStyles.progress}>Step 2 of 3</Text>
          <Text style={formStyles.title}>Personalize Conversations</Text>
          <Text style={formStyles.subtitle}>What does your loved one enjoy talking about?</Text>

          <View style={formStyles.card}>
            <Text style={formStyles.label}>Favorite Topics (comma separated)</Text>
            <TextInput
              style={[formStyles.input, { minHeight: 100, textAlignVertical: 'top' }]}
              placeholder="e.g., gardening, baking, 1970s music"
              placeholderTextColor={colors.gray[400]}
              value={topics}
              onChangeText={setTopics}
              multiline
            />

            <View style={formStyles.footer}>
              <LoadingButton
                title="Next Step"
                onPress={handleNext}
                loading={loading}
              />
            </View>
          </View>
        </ScrollView>
      </TouchableWithoutFeedback>
    </KeyboardAvoidingView>
  );
}
