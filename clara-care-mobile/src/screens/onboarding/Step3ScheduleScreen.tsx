import React, { useState } from 'react';
import {
  View, Text, Alert, TouchableOpacity,
  KeyboardAvoidingView, TouchableWithoutFeedback, Keyboard, Platform, ScrollView, Modal, StyleSheet
} from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';
import { formStyles } from '../../theme/formStyles';
import { colors, spacing, borderRadius } from '../../theme';
import LoadingButton from '../../components/common/LoadingButton';
import { schedulePatient } from '../../api/endpoints';
import { useAppDispatch } from '../../hooks/useRedux';
import { setOnboardingCompleted } from '../../store/slices/authSlice';
import { setActivePatient } from '../../store/slices/patientSlice';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { OnboardingStackParamList } from '../../types/navigation';

type Props = NativeStackScreenProps<OnboardingStackParamList, 'Step3'>;

const formatTime = (date: Date) => {
  let hours = date.getHours();
  let minutes = date.getMinutes();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12; // the hour '0' should be '12'
  const minutesStr = minutes < 10 ? '0' + minutes : minutes;
  return hours + ':' + minutesStr + ' ' + ampm;
};

export default function Step3ScheduleScreen({ route }: Props) {
  const { patient_id } = route.params;
  const dispatch = useAppDispatch();
  
  const [selectedTime, setSelectedTime] = useState<Date>(new Date(new Date().setHours(10, 0, 0, 0)));
  const [callTime, setCallTime] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPicker, setShowPicker] = useState(false);

  const handleFinish = async () => {
    if (!callTime) {
      Alert.alert('Missing Field', 'Please enter a preferred call time.');
      return;
    }
    setLoading(true);
    try {
      await schedulePatient({
        patient_id,
        preferred_call_time: callTime,
      });
      dispatch(setActivePatient(patient_id));
      dispatch(setOnboardingCompleted(true));
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to update schedule');
    } finally {
      setLoading(false);
    }
  };

  const onChange = (event: any, date?: Date) => {
    if (Platform.OS === 'android') {
      setShowPicker(false);
    }
    if (date) {
      setSelectedTime(date);
      setCallTime(formatTime(date));
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
          <Text style={formStyles.progress}>Step 3 of 3</Text>
          <Text style={formStyles.title}>Set Call Schedule</Text>
          <Text style={formStyles.subtitle}>When should ClaraCare call your loved one?</Text>

          <View style={formStyles.card}>
            <Text style={formStyles.label}>Preferred Call Time *</Text>
            <TouchableOpacity
              style={[formStyles.input, { justifyContent: 'center' }]}
              onPress={() => {
                Keyboard.dismiss();
                setShowPicker(true);
              }}
            >
              <Text style={{ color: callTime ? colors.text : colors.gray[400] }}>
                {callTime || 'e.g., 10:00 AM'}
              </Text>
            </TouchableOpacity>

            <View style={formStyles.footer}>
              <LoadingButton
                title="Complete Setup"
                onPress={handleFinish}
                loading={loading}
              />
            </View>
          </View>

          {/* Time Picker Modal for iOS */}
          {Platform.OS === 'ios' ? (
            <Modal
              visible={showPicker}
              transparent
              animationType="slide"
            >
              <View style={styles.modalOverlay}>
                <View style={styles.modalContent}>
                  <View style={styles.modalHeader}>
                    <TouchableOpacity onPress={() => setShowPicker(false)}>
                      <Text style={styles.modalDone}>Done</Text>
                    </TouchableOpacity>
                  </View>
                  <DateTimePicker
                    value={selectedTime}
                    mode="time"
                    display="spinner"
                    onChange={onChange}
                    style={{ height: 200 }}
                    textColor={colors.text}
                  />
                </View>
              </View>
            </Modal>
          ) : (
            showPicker && (
              <DateTimePicker
                value={selectedTime}
                mode="time"
                is24Hour={false}
                display="default"
                onChange={onChange}
              />
            )
          )}
        </ScrollView>
      </TouchableWithoutFeedback>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    justifyContent: 'flex-end',
    backgroundColor: 'rgba(0,0,0,0.4)',
  },
  modalContent: {
    backgroundColor: colors.background,
    borderTopLeftRadius: borderRadius.lg,
    borderTopRightRadius: borderRadius.lg,
    paddingBottom: spacing.xl,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    padding: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  modalDone: {
    color: colors.primary,
    fontWeight: 'bold',
    fontSize: 16,
  },
});
