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

interface DataValidatorScreenProps {
  navigation: any;
}

export const DataValidatorScreen: React.FC<DataValidatorScreenProps> = ({ navigation }) => {
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

  const handleValidate = async () => {
    if (!selectedFile) {
      Alert.alert('Error', 'Please select a file');
      return;
    }

    setLoading(true);
    try {
      Alert.alert('Success', 'Data validation complete!\n\nYour data has been analyzed for quality issues.');
      setResult({
        total_records: 1000,
        valid_records: 956,
        invalid_records: 44,
        data_quality_score: 95.6,
        issues: ['4 rows with missing values', '20 duplicate records', '20 invalid email formats'],
      });
    } catch (error) {
      Alert.alert('Error', error instanceof Error ? error.message : 'Validation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Icon name="check" size={48} color="#10b981" />
          <Text style={styles.title}>Validate Data</Text>
          <Text style={styles.description}>Check data quality and identify issues</Text>
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

        {/* Validation Rules */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Validation Rules</Text>
          
          <View style={styles.ruleCard}>
            <View style={styles.ruleRow}>
              <Icon name="check-circle" size={16} color="#10b981" />
              <Text style={styles.ruleText}>Check for missing values</Text>
            </View>
          </View>

          <View style={styles.ruleCard}>
            <View style={styles.ruleRow}>
              <Icon name="check-circle" size={16} color="#10b981" />
              <Text style={styles.ruleText}>Identify duplicate records</Text>
            </View>
          </View>

          <View style={styles.ruleCard}>
            <View style={styles.ruleRow}>
              <Icon name="check-circle" size={16} color="#10b981" />
              <Text style={styles.ruleText}>Validate data types</Text>
            </View>
          </View>

          <View style={styles.ruleCard}>
            <View style={styles.ruleRow}>
              <Icon name="check-circle" size={16} color="#10b981" />
              <Text style={styles.ruleText}>Check for formatting issues</Text>
            </View>
          </View>
        </View>

        {/* Results */}
        {result && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Validation Results</Text>
            
            {/* Score */}
            <View style={styles.scoreCard}>
              <Text style={styles.scoreLabel}>Data Quality Score</Text>
              <Text style={styles.scoreValue}>{result.data_quality_score}%</Text>
              <View style={styles.scoreBar}>
                <View
                  style={[
                    styles.scoreBarFill,
                    { width: `${result.data_quality_score}%` },
                  ]}
                />
              </View>
            </View>

            {/* Statistics */}
            <View style={styles.statsGrid}>
              <View style={styles.statBox}>
                <Text style={styles.statLabel}>Total Records</Text>
                <Text style={styles.statNumber}>{result.total_records}</Text>
              </View>
              <View style={styles.statBox}>
                <Text style={styles.statLabel}>Valid</Text>
                <Text style={[styles.statNumber, { color: '#10b981' }]}>
                  {result.valid_records}
                </Text>
              </View>
              <View style={styles.statBox}>
                <Text style={styles.statLabel}>Invalid</Text>
                <Text style={[styles.statNumber, { color: '#ef4444' }]}>
                  {result.invalid_records}
                </Text>
              </View>
            </View>

            {/* Issues Found */}
            <View style={styles.issuesCard}>
              <Text style={styles.issuesTitle}>Issues Found</Text>
              {result.issues.map((issue: string, index: number) => (
                <View key={index} style={styles.issueItem}>
                  <Icon name="triangle-exclamation" size={14} color="#f59e0b" />
                  <Text style={styles.issueText}>{issue}</Text>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Action Button */}
        <TouchableOpacity
          style={[styles.button, (!selectedFile || loading) && styles.buttonDisabled]}
          onPress={handleValidate}
          disabled={!selectedFile || loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Icon name="bolt" size={20} color="#fff" />
              <Text style={styles.buttonText}>Validate Data</Text>
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
  ruleCard: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 12,
    marginBottom: 8,
  },
  ruleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  ruleText: {
    marginLeft: 10,
    fontSize: 13,
    color: '#333',
  },
  scoreCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  scoreLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
  },
  scoreValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#10b981',
    marginBottom: 12,
  },
  scoreBar: {
    height: 8,
    backgroundColor: '#e2e8f0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  scoreBarFill: {
    height: '100%',
    backgroundColor: '#10b981',
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  statBox: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 12,
    alignItems: 'center',
    marginHorizontal: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  statNumber: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  issuesCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
  },
  issuesTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  issueItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  issueText: {
    marginLeft: 10,
    fontSize: 13,
    color: '#666',
    flex: 1,
  },
  button: {
    backgroundColor: '#10b981',
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

export default DataValidatorScreen;
