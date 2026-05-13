import React, { useState } from 'react';
import {
  View, Text, TextInput, Alert, StyleSheet, Modal, TouchableOpacity,
  KeyboardAvoidingView, TouchableWithoutFeedback, Keyboard, Platform, ScrollView,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { formStyles } from '../../theme/formStyles';
import { colors, spacing, borderRadius, fontSize } from '../../theme';
import LoadingButton from '../../components/common/LoadingButton';
import { createPatient } from '../../api/endpoints';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { OnboardingStackParamList } from '../../types/navigation';

type Props = NativeStackScreenProps<OnboardingStackParamList, 'Step1'>;

/** Generate years from 1900 to 2000 (elder care target range) */
const YEARS = Array.from({ length: 101 }, (_, i) => 2000 - i); // 2000, 1999, ... 1900

export default function Step1PatientScreen({ navigation }: Props) {
  const [name, setName] = useState('');
  const [preferredName, setPreferredName] = useState('');
  const [birthYear, setBirthYear] = useState<number | null>(null);
  const [phone, setPhone] = useState('');
  const [showYearPicker, setShowYearPicker] = useState(false);
  const [tempYear, setTempYear] = useState(1950);
  const [loading, setLoading] = useState(false);

  /** Only allow digits, max 10 chars */
  const handlePhoneChange = (text: string) => {
    const digits = text.replace(/\D/g, '').slice(0, 10);
    setPhone(digits);
  };

  /** Format for display: (555) 123-4567 */
  const formatPhone = (digits: string) => {
    if (digits.length <= 3) return digits;
    if (digits.length <= 6) return `(${digits.slice(0, 3)}) ${digits.slice(3)}`;
    return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
  };

  const handleNext = async () => {
    if (!name || !birthYear || !phone) {
      Alert.alert('Missing Fields', 'Please fill in all required fields.');
      return;
    }

    if (phone.length !== 10) {
      Alert.alert('Invalid Phone', 'Please enter a 10-digit US phone number.');
      return;
    }

    setLoading(true);
    try {
      const { patient_id } = await createPatient({
        name,
        preferred_name: preferredName || name.split(' ')[0],
        birth_year: birthYear,
        phone_number: `+1${phone}`,
      });
      navigation.navigate('Step2', { patient_id });
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to create patient');
    } finally {
      setLoading(false);
    }
  };

  const openYearPicker = () => {
    Keyboard.dismiss();
    setTempYear(birthYear || 1950);
    setShowYearPicker(true);
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
          <Text style={formStyles.progress}>Step 1 of 3</Text>
          <Text style={formStyles.title}>Who are we caring for?</Text>
          <Text style={formStyles.subtitle}>Let's set up a profile for your loved one.</Text>

          <View style={formStyles.card}>
            <Text style={formStyles.label}>Full Name *</Text>
            <TextInput
              style={formStyles.input}
              placeholder="e.g., Dorothy Smith"
              placeholderTextColor={colors.gray[400]}
              value={name}
              onChangeText={setName}
              returnKeyType="next"
            />

            <Text style={formStyles.label}>Preferred Name</Text>
            <TextInput
              style={formStyles.input}
              placeholder="e.g., Dot"
              placeholderTextColor={colors.gray[400]}
              value={preferredName}
              onChangeText={setPreferredName}
              returnKeyType="next"
            />

            <Text style={formStyles.label}>Birth Year *</Text>
            <TouchableOpacity
              style={[formStyles.input, styles.pickerButton]}
              onPress={openYearPicker}
              activeOpacity={0.7}
            >
              <Text style={birthYear ? styles.pickerValue : styles.pickerPlaceholder}>
                {birthYear ? String(birthYear) : 'Select birth year'}
              </Text>
              <Text style={styles.pickerChevron}>▼</Text>
            </TouchableOpacity>

            <Text style={formStyles.label}>Phone Number *</Text>
            <View style={styles.phoneRow}>
              <View style={styles.countryCode}>
                <Text style={styles.flag}>🇺🇸</Text>
                <Text style={styles.codeText}>+1</Text>
              </View>
              <TextInput
                style={[formStyles.input, styles.phoneInput]}
                placeholder="(555) 123-4567"
                placeholderTextColor={colors.gray[400]}
                keyboardType="number-pad"
                value={formatPhone(phone)}
                onChangeText={handlePhoneChange}
                maxLength={14}
                returnKeyType="done"
                onSubmitEditing={handleNext}
              />
            </View>

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

      {/* Year Picker Modal */}
      <Modal visible={showYearPicker} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <TouchableOpacity onPress={() => setShowYearPicker(false)}>
                <Text style={styles.modalCancel}>Cancel</Text>
              </TouchableOpacity>
              <Text style={styles.modalTitle}>Birth Year</Text>
              <TouchableOpacity
                onPress={() => {
                  setBirthYear(tempYear);
                  setShowYearPicker(false);
                }}
              >
                <Text style={styles.modalDone}>Done</Text>
              </TouchableOpacity>
            </View>

            <Picker
              selectedValue={tempYear}
              onValueChange={(val) => setTempYear(val as number)}
              style={{ height: 200 }}
              itemStyle={{ fontSize: 22, color: colors.text }}
            >
              {YEARS.map((year) => (
                <Picker.Item key={year} label={String(year)} value={year} color={colors.text} />
              ))}
            </Picker>
          </View>
        </View>
      </Modal>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  phoneRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: spacing.lg,
  },
  countryCode: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: borderRadius.md,
    paddingHorizontal: spacing.md,
    height: 50,
    marginRight: spacing.sm,
    backgroundColor: colors.gray[50],
  },
  flag: {
    fontSize: 20,
    marginRight: 6,
  },
  codeText: {
    fontSize: fontSize.md,
    fontWeight: '600',
    color: colors.text,
  },
  phoneInput: {
    flex: 1,
    marginBottom: 0,
  },
  pickerButton: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  pickerValue: {
    fontSize: fontSize.md,
    color: colors.text,
  },
  pickerPlaceholder: {
    fontSize: fontSize.md,
    color: colors.gray[400],
  },
  pickerChevron: {
    fontSize: 12,
    color: colors.gray[400],
  },
  modalOverlay: {
    flex: 1,
    justifyContent: 'flex-end',
    backgroundColor: 'rgba(0,0,0,0.4)',
  },
  modalContent: {
    backgroundColor: colors.card,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    paddingBottom: 34, // safe area
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  modalTitle: {
    fontSize: fontSize.md,
    fontWeight: '600',
    color: colors.text,
  },
  modalCancel: {
    fontSize: fontSize.md,
    color: colors.gray[500],
  },
  modalDone: {
    fontSize: fontSize.md,
    fontWeight: '600',
    color: colors.primary,
  },
});
