import React, { useEffect } from 'react';
import {
  View,
  StyleSheet,
  Text,
  ActivityIndicator,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import ApiClient from '../../services/ApiClient';

interface SplashScreenProps {
  navigation: any;
}

export const SplashScreen: React.FC<SplashScreenProps> = ({ navigation }) => {
  useEffect(() => {
    const restoreSession = async () => {
      try {
        // Try to restore the session
        const restoreSuccess = await ApiClient.restoreSession();
        
        // Add a small delay to make the splash screen visible
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        if (restoreSuccess) {
          navigation.reset({
            index: 0,
            routes: [{ name: 'MainApp' }],
          });
        } else {
          navigation.reset({
            index: 0,
            routes: [{ name: 'Auth' }],
          });
        }
      } catch (error) {
        console.error('Session restoration failed:', error);
        // Navigate to login on error
        navigation.reset({
          index: 0,
          routes: [{ name: 'Auth' }],
        });
      }
    };

    restoreSession();
  }, [navigation]);

  return (
    <View style={styles.container}>
      <Text style={styles.logo}>📄</Text>
      <Text style={styles.title}>DocPro</Text>
      <Text style={styles.subtitle}>Professional Document Processing</Text>
      
      <ActivityIndicator
        size="large"
        color="#667eea"
        style={styles.loader}
      />
      
      <Text style={styles.loadingText}>Initializing...</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9ff',
    justifyContent: 'center',
    alignItems: 'center',
  },
  logo: {
    fontSize: 80,
    marginBottom: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#667eea',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 40,
  },
  loader: {
    marginVertical: 20,
  },
  loadingText: {
    color: '#999',
    fontSize: 12,
    marginTop: 20,
  },
});

export default SplashScreen;
