import React, { useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, RefreshControl, Alert } from 'react-native';
import { colors, spacing, borderRadius, fontSize } from '../../theme';
import { useAppDispatch, useAppSelector } from '../../hooks/useRedux';
import { fetchAlerts } from '../../store/slices/patientSlice';
import { acknowledgeAlert } from '../../api/endpoints';
import EmptyState from '../../components/common/EmptyState';

export default function AlertsScreen() {
  const dispatch = useAppDispatch();
  const { activePatientId, alerts, loading } = useAppSelector(state => state.patient);
  const { user } = useAppSelector(state => state.auth);
  const [refreshing, setRefreshing] = React.useState(false);
  const [acknowledgingId, setAcknowledgingId] = React.useState<string | null>(null);

  useEffect(() => {
    if (activePatientId) {
      dispatch(fetchAlerts(activePatientId));
    }
  }, [activePatientId, dispatch]);

  const onRefresh = React.useCallback(async () => {
    if (activePatientId) {
      setRefreshing(true);
      await dispatch(fetchAlerts(activePatientId));
      setRefreshing(false);
    }
  }, [activePatientId, dispatch]);

  const handleAcknowledge = async (alertId: string) => {
    if (!activePatientId || acknowledgingId) return;
    try {
      setAcknowledgingId(alertId);
      const name = user?.user_metadata?.full_name || user?.email || 'Family Member';
      await acknowledgeAlert(alertId, name);
      await dispatch(fetchAlerts(activePatientId));
    } catch (err) {
      Alert.alert('Error', 'Failed to acknowledge alert');
    } finally {
      setAcknowledgingId(null);
    }
  };

  const renderItem = ({ item }: any) => (
    <View style={[styles.card, { borderLeftColor: item.severity === 'high' ? colors.danger : colors.warning }]}>
      <View style={styles.header}>
        <Text style={styles.type}>{item.alert_type}</Text>
        <Text style={styles.date}>{new Date(item.timestamp).toLocaleString()}</Text>
      </View>
      <Text style={styles.desc}>{item.description}</Text>
      {!item.acknowledged ? (
        <TouchableOpacity 
          style={[styles.button, acknowledgingId === item.id && { opacity: 0.5 }]} 
          onPress={() => handleAcknowledge(item.id)}
          disabled={acknowledgingId === item.id}
        >
          <Text style={styles.buttonText}>
            {acknowledgingId === item.id ? 'Acknowledging...' : 'Acknowledge'}
          </Text>
        </TouchableOpacity>
      ) : (
        <Text style={styles.date}>Acknowledged by {item.acknowledged_by || 'Family Member'}</Text>
      )}
    </View>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={alerts}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />
        }
        ListEmptyComponent={
          !loading ? <EmptyState icon="🔔" message="No active alerts" /> : null
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
    borderRadius: borderRadius.md,
    padding: spacing.lg,
    marginBottom: spacing.md,
    borderLeftWidth: 4,
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
  type: {
    fontSize: fontSize.md,
    fontWeight: 'bold',
    color: colors.text,
  },
  date: {
    fontSize: fontSize.xs,
    color: colors.textSecondary,
  },
  desc: {
    fontSize: fontSize.sm,
    color: colors.text,
    marginBottom: spacing.md,
  },
  button: {
    backgroundColor: colors.gray[100],
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.sm,
    alignSelf: 'flex-start',
  },
  buttonText: {
    color: colors.primary,
    fontWeight: '600',
    fontSize: fontSize.sm,
  },
});
