import { StyleSheet } from 'react-native';
import { colors, spacing, borderRadius, fontSize } from './index';

export const shadows = {
  sm: { shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.05, shadowRadius: 5, elevation: 2 },
  md: { shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.05, shadowRadius: 10, elevation: 3 },
  lg: { shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.05, shadowRadius: 15, elevation: 4 },
};

export const formStyles = StyleSheet.create({
  screenContainer: { flex: 1, backgroundColor: colors.background, padding: spacing.xl, justifyContent: 'center' },
  title: { fontSize: fontSize.title, fontWeight: 'bold', color: colors.primary, textAlign: 'center', marginBottom: spacing.xs },
  subtitle: { fontSize: fontSize.md, color: colors.textSecondary, textAlign: 'center', marginBottom: spacing.xxl },
  card: { backgroundColor: colors.card, padding: spacing.xl, borderRadius: borderRadius.xl, ...shadows.md as any },
  label: { fontSize: fontSize.sm, fontWeight: '600', color: colors.text, marginBottom: spacing.xs },
  input: { borderWidth: 1, borderColor: colors.border, borderRadius: borderRadius.md, padding: spacing.md, marginBottom: spacing.lg, fontSize: fontSize.md, color: colors.text, backgroundColor: colors.card },
  progress: { color: colors.primary, fontWeight: 'bold', marginBottom: spacing.sm },
  footer: { marginTop: spacing.xl },
  linkButton: { marginTop: spacing.xl, alignItems: 'center' },
  linkText: { color: colors.primary, fontSize: fontSize.sm, fontWeight: '600' },
});
