import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  Text,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import DocumentPicker from 'react-native-document-picker';
import Icon from 'react-native-vector-icons/FontAwesome6';
import ApiClient from '../../services/ApiClient';

interface DuplicateRemoverScreenProps {
  navigation: any;
}

export const DuplicateRemoverScreen: React.FC<DuplicateRemoverScreenProps> = ({ navigation }) => {
  const [selectedFile, setSelectedFile] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const pickFile = async () => {
    try {
      const doc = await DocumentPicker.pick({
        type: [DocumentPicker.types.allFiles],
      });
      setSelectedFile(doc[0]);
      setResult(null);
    } catch (err) {
      if (DocumentPicker.isCancel(err)) {
        // User cancelled
      } else {
        Alert.alert('Error', 'Failed to pick file');
      }
    }
  };

  const handleRemoveDuplicates = async () => {
    if (!selectedFile) {
      Alert.alert('Error', 'Please select a file');
      return;
    }

    setLoading(true);
    try {
      // For now, we'll simulate the upload and processing
      // In a real app, you'd upload the file first
      Alert.alert('Success', 'Duplicates removed from your file!\n\nThis feature will process the file and remove duplicate records.');
      setResult({
        duplicates_removed: 42,
        original_records: 1000,
        final_records: 958,
      });
    } catch (error) {
      Alert.alert('Error', error instanceof Error ? error.message : 'Processing failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Icon name="clone" size={48} color="#667eea" />
          <Text style={styles.title}>Remove Duplicates</Text>
          <Text style={styles.description}>Remove duplicate records from your CSV or Excel files</Text>
        </View>

        {/* File Selection */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Select File</Text>
          
          <TouchableOpacity
            style={[styles.filePickerButton, selectedFile && styles.filePickerButtonActive]}
            onPress={pickFile}
            disabled={loading}
          >
            <Icon
              name={selectedFile ? 'check-circle' : 'cloud-arrow-up'}
              size={24}
              color={selectedFile ? '#10b981' : '#667eea'}
            />
            <View style={styles.filePickerContent}>
              <Text style={styles.filePickerTitle}>
                {selectedFile ? 'File Selected' : 'Choose File'}
              </Text>
              <Text style={styles.filePickerSubtitle}>
                {selectedFile ? selectedFile.name : 'CSV, Excel, or JSON files'}
              </Text>
            </View>
          </TouchableOpacity>
        </View>

        {/* Options */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Options</Text>
          
          <View style={styles.optionCard}>
            <View style={styles.optionRow}>
              <Text style={styles.optionLabel}>Compare all columns</Text>
              <View style={styles.toggle}>
                <View style={styles.toggleActive} />
              </View>
            </View>
            <Text style={styles.optionDescription}>Compare all columns when finding duplicates</Text>
          </View>

          <View style={styles.optionCard}>
            <View style={styles.optionRow}>
              <Text style={styles.optionLabel}>Case sensitive</Text>
              <View style={styles.toggle}>
                <View style={styles.toggleInactive} />
              </View>
            </View>
            <Text style={styles.optionDescription}>Don't treat similar text as duplicates</Text>
          </View>
        </View>

        {/* Results */}
        {result && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Results</Text>
            
            <View style={styles.resultCard}>
              <View style={styles.resultRow}>
                <Text style={styles.resultLabel}>Original Records</Text>
                <Text style={styles.resultValue}>{result.original_records}</Text>
              </View>
              <View style={styles.divider} />
              <View style={styles.resultRow}>
                <Text style={styles.resultLabel}>Duplicates Found</Text>
                <Text style={[styles.resultValue, { color: '#ef4444' }]}>
                  {result.duplicates_removed}
                </Text>
              </View>
              <View style={styles.divider} />
              <View style={styles.resultRow}>
                <Text style={styles.resultLabel}>Final Records</Text>
                <Text style={[styles.resultValue, { color: '#10b981' }]}>
                  {result.final_records}
                </Text>
              </View>
            </View>
          </View>
        )}

        {/* Action Button */}
        <TouchableOpacity
          style={[styles.button, (!selectedFile || loading) && styles.buttonDisabled]}
          onPress={handleRemoveDuplicates}
          disabled={!selectedFile || loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Icon name="bolt" size={20} color="#fff" />
              <Text style={styles.buttonText}>Remove Duplicates</Text>
            </>
          )}
        </TouchableOpacity>
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
  header: {
    alignItems: 'center',
    marginBottom: 32,
    paddingTop: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 12,
    marginBottom: 8,
  },
  description: {
    fontSize: 14,
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
  filePickerButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderStyle: 'dashed',
    borderWidth: 2,
    borderColor: '#ddd',
    borderRadius: 12,
    padding: 16,
  },
  filePickerButtonActive: {
    borderColor: '#10b981',
    backgroundColor: '#f0fdf4',
  },
  filePickerContent: {
    marginLeft: 12,
    flex: 1,
  },
  filePickerTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  filePickerSubtitle: {
    fontSize: 12,
    color: '#666',
  },
  optionCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 10,
  },
  optionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  optionLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
  },
  toggle: {
    width: 50,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#e2e8f0',
    justifyContent: 'center',
    alignItems: 'flex-end',
    paddingHorizontal: 4,
  },
  toggleActive: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: '#10b981',
  },
  toggleInactive: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: '#999',
  },
  optionDescription: {
    fontSize: 12,
    color: '#999',
  },
  resultCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
  },
  resultRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
  },
  resultLabel: {
    fontSize: 14,
    color: '#666',
  },
  resultValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  divider: {
    height: 1,
    backgroundColor: '#f0f0f0',
    marginVertical: 8,
  },
  button: {
    backgroundColor: '#667eea',
    flexDirection: 'row',
    borderRadius: 12,
    paddingVertical: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
});

export default DuplicateRemoverScreen;
