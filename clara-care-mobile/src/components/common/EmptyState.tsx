import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, spacing, fontSize } from '../../theme';

export default function EmptyState({ icon = '📭', message }: { icon?: string; message: string }) {
  return (
    <View style={styles.container}>
      <Text style={styles.icon}>{icon}</Text>
      <Text style={styles.message}>{message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    justifyContent: 'center', 
    alignItems: 'center', 
    padding: spacing.xl 
  },
  icon: { 
    fontSize: 48, 
    marginBottom: spacing.md 
  },
  message: { 
    fontSize: fontSize.md, 
    color: colors.textSecondary, 
    textAlign: 'center' 
  },
});
