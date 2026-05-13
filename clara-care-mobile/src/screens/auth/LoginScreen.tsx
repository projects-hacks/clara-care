import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert } from 'react-native';
import { supabase } from '../../api/supabase';
import { formStyles } from '../../theme/formStyles';
import LoadingButton from '../../components/common/LoadingButton';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../../types/navigation';

type Props = NativeStackScreenProps<RootStackParamList, 'Login'>;

export default function LoginScreen({ navigation }: Props) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    setLoading(true);
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      Alert.alert('Login Failed', error.message);
    }
    setLoading(false);
  };

  return (
    <View style={formStyles.screenContainer}>
      <Text style={formStyles.title}>ClaraCare</Text>
      <Text style={formStyles.subtitle}>Welcome back to ClaraCare</Text>

      <View style={formStyles.card}>
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
          title="Sign In" 
          onPress={handleLogin}
          loading={loading}
        />

        <TouchableOpacity 
          style={formStyles.linkButton} 
          onPress={() => navigation.navigate('Signup')}
        >
          <Text style={formStyles.linkText}>Don't have an account? Sign up</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

