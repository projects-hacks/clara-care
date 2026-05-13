import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert } from 'react-native';
import { supabase } from '../../api/supabase';
import { formStyles } from '../../theme/formStyles';
import LoadingButton from '../../components/common/LoadingButton';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../../types/navigation';

type Props = NativeStackScreenProps<RootStackParamList, 'Signup'>;

export default function SignupScreen({ navigation }: Props) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSignup = async () => {
    if (!email || !password || !fullName) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    setLoading(true);
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
        },
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
    <View style={formStyles.screenContainer}>
      <Text style={formStyles.title}>Create Account</Text>
      <Text style={formStyles.subtitle}>Join ClaraCare to support your loved ones</Text>

      <View style={formStyles.card}>
        <Text style={formStyles.label}>Full Name</Text>
        <TextInput
          style={formStyles.input}
          placeholder="Jane Doe"
          value={fullName}
          onChangeText={setFullName}
        />

        <Text style={formStyles.label}>Email Address</Text>
        <TextInput
          style={formStyles.input}
          placeholder="you@example.com"
          value={email}
          onChangeText={setEmail}
          autoCapitalize="none"
          keyboardType="email-address"
        />

        <Text style={formStyles.label}>Password</Text>
        <TextInput
          style={formStyles.input}
          placeholder="••••••••"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
        />

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
    </View>
  );
}

