import React, { useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { colors, spacing, borderRadius, fontSize } from '../../theme';
import { useAppDispatch, useAppSelector } from '../../hooks/useRedux';
import { fetchPatientDetail } from '../../store/slices/patientSlice';

export default function DashboardScreen() {
  const dispatch = useAppDispatch();
  const { activePatientId, detail, loading } = useAppSelector(state => state.patient);
  const [refreshing, setRefreshing] = React.useState(false);

  useEffect(() => {
    if (activePatientId) {
      dispatch(fetchPatientDetail(activePatientId));
    }
  }, [activePatientId, dispatch]);

  const onRefresh = React.useCallback(async () => {
    if (activePatientId) {
      setRefreshing(true);
      await dispatch(fetchPatientDetail(activePatientId));
      setRefreshing(false);
    }
  }, [activePatientId, dispatch]);

  const firstName = detail?.patient?.preferred_name || detail?.patient?.name?.split(' ')[0] || 'There';
  const score = detail?.latest_digest?.cognitive_score || '--';
  const trend = detail?.latest_digest?.cognitive_trend || 'No data yet';

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.greeting}>Good Morning,</Text>
        <Text style={styles.patientName}>{firstName}</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Cognitive Score</Text>
        <View style={styles.scoreContainer}>
          <Text style={styles.score}>{score}</Text>
          <Text style={styles.trendLabel}>/100</Text>
        </View>
        <Text style={styles.trendText}>Trend: {trend}</Text>
      </View>

      <Text style={styles.sectionTitle}>Recent Activity</Text>
      {detail?.recent_conversations && detail.recent_conversations.length > 0 ? (
        detail.recent_conversations.slice(0, 3).map((conv: any) => (
          <View key={conv.id} style={styles.activityCard}>
            <Text style={styles.activityTitle}>Conversation</Text>
            <Text style={styles.activityTime}>{new Date(conv.timestamp).toLocaleString()}</Text>
            <Text style={styles.activityDesc} numberOfLines={2}>{conv.summary}</Text>
          </View>
        ))
      ) : (
        <View style={styles.activityCard}>
            <Text style={styles.activityDesc}>No recent activity found.</Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    padding: spacing.xl,
    backgroundColor: colors.primary,
    borderBottomLeftRadius: borderRadius.xl,
    borderBottomRightRadius: borderRadius.xl,
    marginBottom: spacing.lg,
  },
  greeting: {
    fontSize: fontSize.md,
    color: colors.gray[100],
  },
  patientName: {
    fontSize: fontSize.title,
    fontWeight: 'bold',
    color: colors.card,
  },
  card: {
    marginHorizontal: spacing.lg,
    padding: spacing.xl,
    backgroundColor: colors.card,
    borderRadius: borderRadius.lg,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 2,
    marginBottom: spacing.lg,
  },
  cardTitle: {
    fontSize: fontSize.md,
    fontWeight: '600',
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  scoreContainer: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  score: {
    fontSize: fontSize.title * 1.5,
    fontWeight: 'bold',
    color: colors.primary,
  },
  trendLabel: {
    fontSize: fontSize.md,
    color: colors.textSecondary,
    marginLeft: spacing.xs,
  },
  trendText: {
    fontSize: fontSize.sm,
    color: colors.success,
    marginTop: spacing.sm,
    fontWeight: '500',
  },
  sectionTitle: {
    fontSize: fontSize.lg,
    fontWeight: 'bold',
    color: colors.text,
    marginHorizontal: spacing.lg,
    marginBottom: spacing.md,
  },
  activityCard: {
    marginHorizontal: spacing.lg,
    padding: spacing.md,
    backgroundColor: colors.card,
    borderRadius: borderRadius.md,
    marginBottom: spacing.sm,
    borderLeftWidth: 4,
    borderLeftColor: colors.secondary,
  },
  activityTitle: {
    fontSize: fontSize.md,
    fontWeight: 'bold',
    color: colors.text,
  },
  activityTime: {
    fontSize: fontSize.xs,
    color: colors.textSecondary,
    marginTop: spacing.xs,
    marginBottom: spacing.sm,
  },
  activityDesc: {
    fontSize: fontSize.sm,
    color: colors.text,
  },
});
