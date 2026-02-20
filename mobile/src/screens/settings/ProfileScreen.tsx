import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  Text,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  TextInput,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/FontAwesome6';
import ApiClient from '../../services/ApiClient';
import { User } from '../../types';

interface ProfileScreenProps {
  navigation: any;
}

export const ProfileScreen: React.FC<ProfileScreenProps> = ({ navigation }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [apiKey, setApiKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);

  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    try {
      const userData = await ApiClient.getCurrentUser();
      setUser(userData);
      setApiKey(userData.api_key);
    } catch (error) {
      Alert.alert('Error', 'Failed to load profile');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleResetApiKey = async () => {
    Alert.alert('Reset API Key', 'Are you sure you want to reset your API key? This will invalidate the current key.', [
      {
        text: 'Cancel',
        style: 'cancel',
      },
      {
        text: 'Reset',
        style: 'destructive',
        onPress: async () => {
          try {
            const newApiKey = await ApiClient.resetApiKey();
            setApiKey(newApiKey);
            Alert.alert('Success', 'API key has been reset');
          } catch (error) {
            Alert.alert('Error', 'Failed to reset API key');
          }
        },
      },
    ]);
  };

  const handleCopyApiKey = () => {
    // In a real app, use react-native-clipboard
    Alert.alert('Copied', 'API key copied to clipboard');
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
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
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Icon name="chevron-left" size={24} color="#667eea" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Profile Information</Text>
          <View style={{ width: 24 }} />
        </View>

        {/* Profile Avatar Section */}
        <View style={styles.avatarSection}>
          <View style={styles.avatar}>
            <Icon name="user-circle" size={80} color="#fff" />
          </View>
          <Text style={styles.username}>{user?.username}</Text>
          <Text style={styles.joinDate}>Joined {formatDate(user?.created_at || '')}</Text>
        </View>

        {/* Account Information */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Account Information</Text>

          <View style={styles.infoCard}>
            <View style={styles.infoField}>
              <Text style={styles.fieldLabel}>Username</Text>
              <View style={styles.fieldValue}>
                <Icon name="user" size={14} color="#667eea" />
                <Text style={styles.fieldText}>{user?.username}</Text>
              </View>
            </View>
          </View>

          <View style={styles.infoCard}>
            <View style={styles.infoField}>
              <Text style={styles.fieldLabel}>Email Address</Text>
              <View style={styles.fieldValue}>
                <Icon name="envelope" size={14} color="#667eea" />
                <Text style={styles.fieldText}>{user?.email}</Text>
              </View>
            </View>
          </View>

          <View style={styles.infoCard}>
            <View style={styles.infoField}>
              <Text style={styles.fieldLabel}>Account Created</Text>
              <View style={styles.fieldValue}>
                <Icon name="calendar" size={14} color="#667eea" />
                <Text style={styles.fieldText}>{formatDate(user?.created_at || '')}</Text>
              </View>
            </View>
          </View>
        </View>

        {/* API Key Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>API Key</Text>

          <View style={styles.apiKeyCard}>
            <View style={styles.apiKeyHeader}>
              <Text style={styles.apiKeyLabel}>Your API Key</Text>
              <TouchableOpacity onPress={() => setShowApiKey(!showApiKey)}>
                <Icon name={showApiKey ? 'eye' : 'eye-slash'} size={16} color="#667eea" />
              </TouchableOpacity>
            </View>

            <View style={styles.apiKeyInputContainer}>
              <TextInput
                style={styles.apiKeyInput}
                value={showApiKey ? apiKey : '••••••••••••••••••••'}
                editable={false}
                selectTextOnFocus={true}
              />
              <TouchableOpacity
                style={styles.copyButton}
                onPress={handleCopyApiKey}
              >
                <Icon name="copy" size={16} color="#667eea" />
              </TouchableOpacity>
            </View>

            <Text style={styles.apiKeyInfo}>
              Use this key to authenticate API requests. Keep it secure!
            </Text>

            <TouchableOpacity
              style={styles.resetButton}
              onPress={handleResetApiKey}
            >
              <Icon name="rotate-right" size={14} color="#fff" />
              <Text style={styles.resetButtonText}>Reset API Key</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Security Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Security</Text>

          <TouchableOpacity style={styles.securityItem}>
            <View style={styles.securityIconContainer}>
              <Icon name="lock" size={16} color="#f59e0b" />
            </View>
            <View style={styles.securityContent}>
              <Text style={styles.securityLabel}>Change Password</Text>
              <Text style={styles.securityDescription}>Update your password</Text>
            </View>
            <Icon name="chevron-right" size={16} color="#ccc" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.securityItem}>
            <View style={styles.securityIconContainer}>
              <Icon name="shield" size={16} color="#10b981" />
            </View>
            <View style={styles.securityContent}>
              <Text style={styles.securityLabel}>Two-Factor Authentication</Text>
              <Text style={styles.securityDescription}>Not enabled</Text>
            </View>
            <Icon name="chevron-right" size={16} color="#ccc" />
          </TouchableOpacity>
        </View>

        {/* Danger Zone */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Danger Zone</Text>

          <TouchableOpacity style={styles.dangerItem}>
            <Icon name="triangle-exclamation" size={16} color="#ef4444" />
            <Text style={styles.dangerText}>Delete Account</Text>
            <Icon name="chevron-right" size={16} color="#ccc" />
          </TouchableOpacity>
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
    paddingBottom: 30,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 16,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  avatarSection: {
    alignItems: 'center',
    paddingVertical: 24,
  },
  avatar: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#667eea',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  username: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  joinDate: {
    fontSize: 12,
    color: '#999',
  },
  section: {
    paddingHorizontal: 16,
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    textTransform: 'uppercase',
    marginBottom: 12,
    letterSpacing: 0.5,
  },
  infoCard: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 14,
    marginBottom: 8,
  },
  infoField: {
    flexDirection: 'column',
  },
  fieldLabel: {
    fontSize: 12,
    color: '#999',
    marginBottom: 6,
    textTransform: 'uppercase',
    fontWeight: '500',
  },
  fieldValue: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  fieldText: {
    fontSize: 14,
    color: '#333',
    marginLeft: 10,
  },
  apiKeyCard: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 14,
  },
  apiKeyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  apiKeyLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#333',
    textTransform: 'uppercase',
  },
  apiKeyInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8f9ff',
    borderRadius: 8,
    paddingHorizontal: 10,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  apiKeyInput: {
    flex: 1,
    paddingVertical: 10,
    fontSize: 12,
    fontFamily: 'monospace',
    color: '#333',
  },
  copyButton: {
    padding: 8,
  },
  apiKeyInfo: {
    fontSize: 11,
    color: '#999',
    marginBottom: 12,
    fontStyle: 'italic',
  },
  resetButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#667eea',
    borderRadius: 8,
    paddingVertical: 10,
  },
  resetButtonText: {
    color: '#fff',
    fontSize: 13,
    fontWeight: '600',
    marginLeft: 6,
  },
  securityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    marginBottom: 8,
  },
  securityIconContainer: {
    width: 36,
    height: 36,
    borderRadius: 8,
    backgroundColor: '#f0f0f8',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  securityContent: {
    flex: 1,
  },
  securityLabel: {
    fontSize: 13,
    fontWeight: '500',
    color: '#333',
  },
  securityDescription: {
    fontSize: 11,
    color: '#999',
    marginTop: 2,
  },
  dangerItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fef2f2',
    borderRadius: 10,
    borderWidth: 2,
    borderColor: '#fee2e2',
    paddingHorizontal: 14,
    paddingVertical: 12,
  },
  dangerText: {
    flex: 1,
    fontSize: 13,
    fontWeight: '500',
    color: '#ef4444',
    marginLeft: 12,
  },
});

export default ProfileScreen;
