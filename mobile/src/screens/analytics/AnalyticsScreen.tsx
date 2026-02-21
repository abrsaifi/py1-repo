import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  Text,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/FontAwesome6';
import ApiClient from '../../services/ApiClient';
import { AnalyticsData } from '../../types';

interface AnalyticsScreenProps {
  navigation: any;
}

export const AnalyticsScreen: React.FC<AnalyticsScreenProps> = ({ navigation }) => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const data = await ApiClient.getAnalytics();
      setAnalytics(data);
    } catch (error) {
      Alert.alert('Error', 'Failed to load analytics');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadAnalytics();
    setRefreshing(false);
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#667eea" />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor="#667eea"
          />
        }
      >
        <Text style={styles.header}>Analytics</Text>

        {/* Main Metrics */}
        <View style={styles.metricsGrid}>
          <View style={styles.metricCard}>
            <Icon name="file" size={28} color="#667eea" />
            <Text style={styles.metricValue}>{analytics?.total_files || 0}</Text>
            <Text style={styles.metricLabel}>Total Files</Text>
          </View>

          <View style={styles.metricCard}>
            <Icon name="lightning-bolt" size={28} color="#f59e0b" />
            <Text style={styles.metricValue}>{analytics?.total_operations || 0}</Text>
            <Text style={styles.metricLabel}>Operations</Text>
          </View>

          <View style={styles.metricCard}>
            <Icon name="chart-line" size={28} color="#10b981" />
            <Text style={styles.metricValue}>
              {analytics?.success_rate ? Math.round(analytics.success_rate) : 0}%
            </Text>
            <Text style={styles.metricLabel}>Success Rate</Text>
          </View>

          <View style={styles.metricCard}>
            <Icon name="clock" size={28} color="#8b5cf6" />
            <Text style={styles.metricValue}>
              {analytics?.average_processing_time
                ? Math.round(analytics.average_processing_time)
                : 0}
            </Text>
            <Text style={styles.metricLabel}>Avg Time (ms)</Text>
          </View>
        </View>

        {/* File Type Distribution */}
        {analytics?.files_by_type && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Files by Type</Text>
            {Object.entries(analytics.files_by_type).map(([type, count]) => (
              <View key={type} style={styles.distributionItem}>
                <View style={styles.distributionContent}>
                  <Text style={styles.distributionLabel}>{type}</Text>
                  <View style={styles.distributionBar}>
                    <View
                      style={[
                        styles.distributionBarFill,
                        {
                          width: `${
                            ((count as number) /
                              Math.max(
                                ...Object.values(analytics.files_by_type).map(
                                  (v) => v as number,
                                ),
                              )) *
                            100
                          }%`,
                        },
                      ]}
                    />
                  </View>
                </View>
                <Text style={styles.distributionValue}>{count}</Text>
              </View>
            ))}
          </View>
        )}

        {/* Operation Type Distribution */}
        {analytics?.operations_by_type && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Operations by Type</Text>
            {Object.entries(analytics.operations_by_type).map(([type, count]) => (
              <View key={type} style={styles.operationItem}>
                <Text style={styles.operationLabel}>{type}</Text>
                <Text style={styles.operationCount}>{count}</Text>
              </View>
            ))}
          </View>
        )}

        {/* Storage Information */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Storage Information</Text>
          <View style={styles.storageCard}>
            <View style={styles.storageRow}>
              <Text style={styles.storageLabel}>Total Storage Used</Text>
              <Text style={styles.storageValue}>
                {analytics?.total_storage_used
                  ? (analytics.total_storage_used / 1024 / 1024).toFixed(2)
                  : 0}{' '}
                MB
              </Text>
            </View>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9ff',
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 30,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 24,
    marginTop: 16,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  metricCard: {
    width: '48%',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  metricValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginVertical: 8,
  },
  metricLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  distributionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 12,
    marginBottom: 10,
  },
  distributionContent: {
    flex: 1,
    marginRight: 12,
  },
  distributionLabel: {
    fontSize: 13,
    fontWeight: '500',
    color: '#333',
    marginBottom: 6,
  },
  distributionBar: {
    height: 8,
    backgroundColor: '#e2e8f0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  distributionBarFill: {
    height: '100%',
    backgroundColor: '#667eea',
  },
  distributionValue: {
    fontSize: 13,
    fontWeight: '600',
    color: '#667eea',
  },
  operationItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 12,
    marginBottom: 8,
  },
  operationLabel: {
    fontSize: 13,
    color: '#333',
  },
  operationCount: {
    fontSize: 13,
    fontWeight: '600',
    color: '#667eea',
  },
  storageCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
  },
  storageRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  storageLabel: {
    fontSize: 14,
    color: '#666',
  },
  storageValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#667eea',
  },
});

export default AnalyticsScreen;
