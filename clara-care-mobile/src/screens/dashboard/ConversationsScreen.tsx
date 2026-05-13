import React, { useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, RefreshControl } from 'react-native';
import { colors, spacing, borderRadius, fontSize } from '../../theme';
import { useAppDispatch, useAppSelector } from '../../hooks/useRedux';
import { fetchConversations } from '../../store/slices/patientSlice';
import EmptyState from '../../components/common/EmptyState';

export default function ConversationsScreen() {
  const dispatch = useAppDispatch();
  const { activePatientId, conversations, loading } = useAppSelector(state => state.patient);
  const [refreshing, setRefreshing] = React.useState(false);

  useEffect(() => {
    if (activePatientId) {
      dispatch(fetchConversations(activePatientId));
    }
  }, [activePatientId, dispatch]);

  const onRefresh = React.useCallback(async () => {
    if (activePatientId) {
      setRefreshing(true);
      await dispatch(fetchConversations(activePatientId));
      setRefreshing(false);
    }
  }, [activePatientId, dispatch]);

  const renderItem = ({ item }: any) => (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.date}>{new Date(item.timestamp).toLocaleString()}</Text>
        <Text style={styles.duration}>{Math.round(item.duration / 60)} min</Text>
      </View>
      <Text style={styles.summary}>{item.summary}</Text>
      <View style={styles.badge}>
        <Text style={styles.badgeText}>{item.detected_mood || 'Neutral'}</Text>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={conversations}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />
        }
        ListEmptyComponent={
          !loading ? <EmptyState icon="💬" message="No conversations yet" /> : null
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  list: {
    padding: spacing.lg,
  },
  card: {
    backgroundColor: colors.card,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.md,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 5,
    elevation: 2,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  date: {
    fontSize: fontSize.sm,
    fontWeight: 'bold',
    color: colors.text,
  },
  duration: {
    fontSize: fontSize.sm,
    color: colors.textSecondary,
  },
  summary: {
    fontSize: fontSize.md,
    color: colors.text,
    marginBottom: spacing.md,
  },
  badge: {
    alignSelf: 'flex-start',
    backgroundColor: colors.secondary + '20', // transparent secondary
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: borderRadius.full,
  },
  badgeText: {
    color: colors.secondary,
    fontSize: fontSize.xs,
    fontWeight: 'bold',
  },
});
