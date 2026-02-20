import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  Text,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/FontAwesome6';
import AsyncStorage from '@react-native-async-storage/async-storage';
import ApiClient from '../../services/ApiClient';

interface SettingsScreenProps {
  navigation: any;
}

export const SettingsScreen: React.FC<SettingsScreenProps> = ({ navigation }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUserInfo();
  }, []);

  const loadUserInfo = async () => {
    try {
      const user = await ApiClient.getCurrentUser();
      setUsername(user.username);
      setEmail(user.email);
    } catch (error) {
      console.error('Failed to load user info:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    Alert.alert('Logout', 'Are you sure you want to logout?', [
      {
        text: 'Cancel',
        style: 'cancel',
      },
      {
        text: 'Logout',
        style: 'destructive',
        onPress: async () => {
          try {
            await ApiClient.logout();
            // Navigation to auth screen happens automatically via App.tsx state management
          } catch (error) {
            Alert.alert('Error', 'Failed to logout');
          }
        },
      },
    ]);
  };

  const goToProfile = () => {
    navigation.navigate('Settings', { screen: 'Profile' });
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
        <Text style={styles.header}>Settings</Text>

        {/* User Profile Section */}
        <TouchableOpacity style={styles.profileCard} onPress={goToProfile}>
          <View style={styles.profileAvatar}>
            <Icon name="user-circle" size={56} color="#fff" />
          </View>
          <View style={styles.profileContent}>
            <Text style={styles.profileName}>{username}</Text>
            <Text style={styles.profileEmail}>{email}</Text>
          </View>
          <Icon name="chevron-right" size={20} color="#ccc" />
        </TouchableOpacity>

        {/* Account Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Account</Text>

          <TouchableOpacity style={styles.settingItem} onPress={goToProfile}>
            <View style={styles.settingIconContainer}>
              <Icon name="user" size={18} color="#667eea" />
            </View>
            <View style={styles.settingContent}>
              <Text style={styles.settingLabel}>Profile Information</Text>
              <Text style={styles.settingDescription}>View and edit your profile</Text>
            </View>
            <Icon name="chevron-right" size={16} color="#ccc" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.settingItem}>
            <View style={styles.settingIconContainer}>
              <Icon name="lock" size={18} color="#667eea" />
            </View>
            <View style={styles.settingContent}>
              <Text style={styles.settingLabel}>Change Password</Text>
              <Text style={styles.settingDescription}>Update your password</Text>
            </View>
            <Icon name="chevron-right" size={16} color="#ccc" />
          </TouchableOpacity>
        </View>

        {/* API Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>API & Integration</Text>

          <TouchableOpacity style={styles.settingItem}>
            <View style={styles.settingIconContainer}>
              <Icon name="key" size={18} color="#f59e0b" />
            </View>
            <View style={styles.settingContent}>
              <Text style={styles.settingLabel}>API Keys</Text>
              <Text style={styles.settingDescription}>Manage your API keys</Text>
            </View>
            <Icon name="chevron-right" size={16} color="#ccc" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.settingItem}>
            <View style={styles.settingIconContainer}>
              <Icon name="webhook" size={18} color="#f59e0b" />
            </View>
            <View style={styles.settingContent}>
              <Text style={styles.settingLabel}>Webhooks</Text>
              <Text style={styles.settingDescription}>Configure webhook notifications</Text>
            </View>
            <Icon name="chevron-right" size={16} color="#ccc" />
          </TouchableOpacity>
        </View>

        {/* App Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>App</Text>

          <TouchableOpacity style={styles.settingItem}>
            <View style={styles.settingIconContainer}>
              <Icon name="bell" size={18} color="#10b981" />
            </View>
            <View style={styles.settingContent}>
              <Text style={styles.settingLabel}>Notifications</Text>
              <Text style={styles.settingDescription}>Manage notification preferences</Text>
            </View>
            <Icon name="chevron-right" size={16} color="#ccc" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.settingItem}>
            <View style={styles.settingIconContainer}>
              <Icon name="palette" size={18} color="#10b981" />
            </View>
            <View style={styles.settingContent}>
              <Text style={styles.settingLabel}>Theme</Text>
              <Text style={styles.settingDescription}>Choose light or dark theme</Text>
            </View>
            <Icon name="chevron-right" size={16} color="#ccc" />
          </TouchableOpacity>
        </View>

        {/* Help & Support */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Help & Support</Text>

          <TouchableOpacity style={styles.settingItem}>
            <View style={styles.settingIconContainer}>
              <Icon name="circle-question" size={18} color="#8b5cf6" />
            </View>
            <View style={styles.settingContent}>
              <Text style={styles.settingLabel}>Help Center</Text>
              <Text style={styles.settingDescription}>Get help and support</Text>
            </View>
            <Icon name="chevron-right" size={16} color="#ccc" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.settingItem}>
            <View style={styles.settingIconContainer}>
              <Icon name="file-lines" size={18} color="#8b5cf6" />
            </View>
            <View style={styles.settingContent}>
              <Text style={styles.settingLabel}>Terms & Privacy</Text>
              <Text style={styles.settingDescription}>Read our terms and privacy policy</Text>
            </View>
            <Icon name="chevron-right" size={16} color="#ccc" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.settingItem}>
            <View style={styles.settingIconContainer}>
              <Icon name="circle-info" size={18} color="#8b5cf6" />
            </View>
            <View style={styles.settingContent}>
              <Text style={styles.settingLabel}>About</Text>
              <Text style={styles.settingDescription}>Version 1.0.0</Text>
            </View>
            <Icon name="chevron-right" size={16} color="#ccc" />
          </TouchableOpacity>
        </View>

        {/* Logout Section */}
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Icon name="sign-out" size={18} color="#ef4444" />
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>

        <View style={styles.footer}>
          <Text style={styles.footerText}>DocPro Mobile v1.0.0</Text>
          <Text style={styles.footerSubtext}>© 2024 DocPro. All rights reserved.</Text>
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
  profileCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  profileAvatar: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#667eea',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  profileContent: {
    flex: 1,
  },
  profileName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  profileEmail: {
    fontSize: 12,
    color: '#666',
  },
  section: {
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
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.02,
    shadowRadius: 2,
    elevation: 1,
  },
  settingIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 8,
    backgroundColor: '#f0f0f8',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  settingContent: {
    flex: 1,
  },
  settingLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
    marginBottom: 2,
  },
  settingDescription: {
    fontSize: 12,
    color: '#999',
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
    borderRadius: 10,
    paddingVertical: 14,
    marginTop: 24,
    marginBottom: 16,
  },
  logoutText: {
    marginLeft: 8,
    fontSize: 14,
    fontWeight: '600',
    color: '#ef4444',
  },
  footer: {
    alignItems: 'center',
    paddingVertical: 16,
  },
  footerText: {
    fontSize: 12,
    color: '#999',
    marginBottom: 2,
  },
  footerSubtext: {
    fontSize: 10,
    color: '#ccc',
  },
});

export default SettingsScreen;
