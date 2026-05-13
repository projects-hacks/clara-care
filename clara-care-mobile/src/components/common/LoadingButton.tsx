import React from 'react';
import { TouchableOpacity, Text, ActivityIndicator, StyleSheet, ViewStyle } from 'react-native';
import { colors, spacing, borderRadius, fontSize } from '../../theme';

interface Props {
  title: string;
  onPress: () => void;
  loading?: boolean;
  disabled?: boolean;
  style?: ViewStyle;
}

export default function LoadingButton({ title, onPress, loading, disabled, style }: Props) {
  return (
    <TouchableOpacity 
      style={[styles.button, style]} 
      onPress={onPress} 
      disabled={disabled || loading}
    >
      {loading ? <ActivityIndicator color={colors.card} /> : <Text style={styles.text}>{title}</Text>}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: { 
    backgroundColor: colors.primary, 
    padding: spacing.md, 
    borderRadius: borderRadius.md, 
    alignItems: 'center',
    marginTop: spacing.sm,
  },
  text: { 
    color: colors.card, 
    fontSize: fontSize.md, 
    fontWeight: 'bold' 
  },
});
