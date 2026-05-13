import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, Alert,
  KeyboardAvoidingView, TouchableWithoutFeedback, Keyboard, Platform, ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { supabase } from '../../api/supabase';
import { formStyles } from '../../theme/formStyles';
import { colors, spacing } from '../../theme';
import LoadingButton from '../../components/common/LoadingButton';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../../types/navigation';

type Props = NativeStackScreenProps<RootStackParamList, 'Signup'>;

export default function SignupScreen({ navigation }: Props) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const isValidEmail = (e: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e);

  const handleSignup = async () => {
    if (!email || !password || !fullName) {
      Alert.alert('Missing Fields', 'Please fill in all fields.');
      return;
    }
    if (fullName.trim().length < 2) {
      Alert.alert('Invalid Name', 'Please enter your full name.');
      return;
    }
    if (!isValidEmail(email)) {
      Alert.alert('Invalid Email', 'Please enter a valid email address.');
      return;
    }
    if (password.length < 6) {
      Alert.alert('Weak Password', 'Password must be at least 6 characters.');
      return;
    }

    setLoading(true);
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { full_name: fullName },
      },
    });

    if (error) {
      Alert.alert('Signup Failed', error.message);
    } else {
      Alert.alert('Success', 'Check your email for the confirmation link', [
        { text: 'OK', onPress: () => navigation.navigate('Login') }
      ]);
    }
    setLoading(false);
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
          <Text style={formStyles.title}>Create Account</Text>
          <Text style={formStyles.subtitle}>Join ClaraCare to support your loved ones</Text>

          <View style={formStyles.card}>
            <Text style={formStyles.label}>Full Name</Text>
            <TextInput
              style={formStyles.input}
              placeholder="Jane Doe"
              placeholderTextColor={colors.gray[400]}
              value={fullName}
              onChangeText={setFullName}
              autoComplete="name"
              returnKeyType="next"
            />

            <Text style={formStyles.label}>Email Address</Text>
            <TextInput
              style={formStyles.input}
              placeholder="you@example.com"
              placeholderTextColor={colors.gray[400]}
              value={email}
              onChangeText={setEmail}
              autoCapitalize="none"
              keyboardType="email-address"
              autoComplete="email"
              returnKeyType="next"
            />

            <Text style={formStyles.label}>Password</Text>
            <View style={{ position: 'relative' }}>
              <TextInput
                style={[formStyles.input, { paddingRight: 48 }]}
                placeholder="Minimum 6 characters"
                placeholderTextColor={colors.gray[400]}
                value={password}
                onChangeText={setPassword}
                secureTextEntry={!showPassword}
                autoComplete="new-password"
                returnKeyType="done"
                onSubmitEditing={handleSignup}
              />
              <TouchableOpacity
                onPress={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: 14,
                  top: 0,
                  bottom: spacing.lg,
                  justifyContent: 'center',
                }}
                hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
              >
                <Ionicons
                  name={showPassword ? 'eye-off-outline' : 'eye-outline'}
                  size={22}
                  color={colors.gray[400]}
                />
              </TouchableOpacity>
            </View>

            <LoadingButton
              title="Sign Up"
              onPress={handleSignup}
              loading={loading}
            />

            <TouchableOpacity
              style={formStyles.linkButton}
              onPress={() => navigation.navigate('Login')}
            >
              <Text style={formStyles.linkText}>Already have an account? Sign in</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </TouchableWithoutFeedback>
    </KeyboardAvoidingView>
  );
}
