import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  Text,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/FontAwesome6';
import ApiClient from '../../services/ApiClient';
import { AnalyticsData } from '../../types';

interface DashboardScreenProps {
  navigation: any;
}

export const DashboardScreen: React.FC<DashboardScreenProps> = ({ navigation }) => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [username, setUsername] = useState('');

  useEffect(() => {
    loadDashboardData();
    loadUsername();
  }, []);

  const loadUsername = async () => {
    try {
      const user = await ApiClient.getCurrentUser();
      setUsername(user.username);
    } catch (error) {
      console.error('Failed to load user:', error);
    }
  };

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const data = await ApiClient.getAnalytics();
      setAnalytics(data);
    } catch (error) {
      Alert.alert('Error', 'Failed to load analytics data');
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#667eea" />
          <Text style={styles.loadingText}>Loading dashboard...</Text>
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
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Welcome back!</Text>
            <Text style={styles.username}>{username}</Text>
          </View>
          <View style={styles.avatar}>
            <Icon name="user-circle" size={40} color="#667eea" />
          </View>
        </View>

        {/* Quick Stats */}
        <View style={styles.statsGrid}>
          <TouchableOpacity style={styles.statCard}>
            <Icon name="file" size={24} color="#667eea" />
            <Text style={styles.statValue}>{analytics?.total_files || 0}</Text>
            <Text style={styles.statLabel}>Files Processed</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.statCard}>
            <Icon name="check-circle" size={24} color="#10b981" />
            <Text style={styles.statValue}>
              {analytics?.success_rate ? Math.round(analytics.success_rate) : 0}%
            </Text>
            <Text style={styles.statLabel}>Success Rate</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.statCard}>
            <Icon name="clock" size={24} color="#f59e0b" />
            <Text style={styles.statValue}>
              {analytics?.average_processing_time
                ? Math.round(analytics.average_processing_time)
                : 0}
            </Text>
            <Text style={styles.statLabel}>Avg Time (ms)</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.statCard}>
            <Icon name="database" size={24} color="#6366f1" />
            <Text style={styles.statValue}>
              {analytics?.total_storage_used
                ? (analytics.total_storage_used / 1024 / 1024).toFixed(1)
                : 0}
            </Text>
            <Text style={styles.statLabel}>Storage (MB)</Text>
          </TouchableOpacity>
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('Tools', { screen: 'DuplicateRemover' })}
          >
            <View style={styles.actionIcon}>
              <Icon name="clone" size={24} color="#667eea" />
            </View>
            <View style={styles.actionContent}>
              <Text style={styles.actionTitle}>Remove Duplicates</Text>
              <Text style={styles.actionDescription}>Remove duplicate records from your data</Text>
            </View>
            <Icon name="chevron-right" size={20} color="#ccc" />
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('Tools', { screen: 'DataValidator' })}
          >
            <View style={styles.actionIcon}>
              <Icon name="check" size={24} color="#10b981" />
            </View>
            <View style={styles.actionContent}>
              <Text style={styles.actionTitle}>Validate Data</Text>
              <Text style={styles.actionDescription}>Check data quality and integrity</Text>
            </View>
            <Icon name="chevron-right" size={20} color="#ccc" />
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('Tools', { screen: 'PDFExport' })}
          >
            <View style={styles.actionIcon}>
              <Icon name="file-pdf" size={24} color="#ef4444" />
            </View>
            <View style={styles.actionContent}>
              <Text style={styles.actionTitle}>Export to PDF</Text>
              <Text style={styles.actionDescription}>Convert and export your files</Text>
            </View>
            <Icon name="chevron-right" size={20} color="#ccc" />
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('Tools', { screen: 'ReportGenerator' })}
          >
            <View style={styles.actionIcon}>
              <Icon name="chart-bar" size={24} color="#f59e0b" />
            </View>
            <View style={styles.actionContent}>
              <Text style={styles.actionTitle}>Generate Report</Text>
              <Text style={styles.actionDescription}>Create detailed analysis reports</Text>
            </View>
            <Icon name="chevron-right" size={20} color="#ccc" />
          </TouchableOpacity>
        </View>

        {/* Recent Activity */}
        {analytics?.total_operations && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Overview</Text>
            <View style={styles.infoCard}>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Total Operations</Text>
                <Text style={styles.infoValue}>{analytics.total_operations}</Text>
              </View>
              <View style={styles.divider} />
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Most Used</Text>
                <Text style={styles.infoValue}>
                  {analytics.operations_by_type
                    ? Object.entries(analytics.operations_by_type)
                        .sort(([, a], [, b]) => (b as number) - (a as number))
                        .slice(0, 1)
                        .map(([key]) => key)
                        .join(', ') || 'N/A'
                    : 'N/A'}
                </Text>
              </View>
            </View>
          </View>
        )}
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
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    color: '#666',
    fontSize: 14,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  greeting: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  username: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  avatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  statCard: {
    width: '48%',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginVertical: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 12,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  actionIcon: {
    width: 50,
    height: 50,
    borderRadius: 10,
    backgroundColor: '#f0f0f8',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  actionContent: {
    flex: 1,
  },
  actionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  actionDescription: {
    fontSize: 12,
    color: '#999',
  },
  infoCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  infoLabel: {
    fontSize: 14,
    color: '#666',
  },
  infoValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#667eea',
  },
  divider: {
    height: 1,
    backgroundColor: '#f0f0f0',
    marginVertical: 8,
  },
});

export default DashboardScreen;
