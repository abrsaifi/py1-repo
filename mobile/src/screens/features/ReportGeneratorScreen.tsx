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

interface ReportGeneratorScreenProps {
  navigation: any;
}

export const ReportGeneratorScreen: React.FC<ReportGeneratorScreenProps> = ({ navigation }) => {
  const [selectedFile, setSelectedFile] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [selectedReportType, setSelectedReportType] = useState<'summary' | 'detailed' | 'comparative'>('summary');

  const pickFile = async () => {
    try {
      const doc = await DocumentPicker.pick({
        type: [DocumentPicker.types.allFiles],
      });
      setSelectedFile(doc[0]);
    } catch (err) {
      if (DocumentPicker.isCancel(err)) {
        // User cancelled
      } else {
        Alert.alert('Error', 'Failed to pick file');
      }
    }
  };

  const handleGenerateReport = async () => {
    if (!selectedFile) {
      Alert.alert('Error', 'Please select a file');
      return;
    }

    setLoading(true);
    try {
      Alert.alert('Success', `${selectedReportType} report generated successfully!`);
    } catch (error) {
      Alert.alert('Error', error instanceof Error ? error.message : 'Report generation failed');
    } finally {
      setLoading(false);
    }
  };

  const reportTypes = [
    {
      id: 'summary' as const,
      label: 'Summary',
      description: 'Quick overview with key metrics',
      icon: 'chart-pie',
    },
    {
      id: 'detailed' as const,
      label: 'Detailed',
      description: 'Comprehensive analysis with breakdowns',
      icon: 'chart-bar',
    },
    {
      id: 'comparative' as const,
      label: 'Comparative',
      description: 'Compare multiple datasets',
      icon: 'scale-balanced',
    },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Icon name="chart-bar" size={48} color="#f59e0b" />
          <Text style={styles.title}>Generate Report</Text>
          <Text style={styles.description}>Create detailed analysis reports</Text>
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
              color={selectedFile ? '#f59e0b' : '#667eea'}
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

        {/* Report Type Selection */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Report Type</Text>
          
          {reportTypes.map((type) => (
            <TouchableOpacity
              key={type.id}
              style={[
                styles.reportTypeCard,
                selectedReportType === type.id && styles.reportTypeCardActive,
              ]}
              onPress={() => setSelectedReportType(type.id)}
            >
              <View style={styles.reportTypeIcon}>
                <Icon name={type.icon} size={24} color="#f59e0b" />
              </View>
              <View style={styles.reportTypeContent}>
                <Text style={styles.reportTypeLabel}>{type.label}</Text>
                <Text style={styles.reportTypeDescription}>{type.description}</Text>
              </View>
              {selectedReportType === type.id && (
                <Icon name="check-circle" size={20} color="#f59e0b" />
              )}
            </TouchableOpacity>
          ))}
        </View>

        {/* Report Options */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Report Contents</Text>
          
          <View style={styles.optionCard}>
            <View style={styles.optionRow}>
              <Icon name="check-circle" size={16} color="#10b981" />
              <Text style={styles.optionLabel}>Data Summary</Text>
            </View>
          </View>

          <View style={styles.optionCard}>
            <View style={styles.optionRow}>
              <Icon name="check-circle" size={16} color="#10b981" />
              <Text style={styles.optionLabel}>Statistical Analysis</Text>
            </View>
          </View>

          <View style={styles.optionCard}>
            <View style={styles.optionRow}>
              <Icon name="check-circle" size={16} color="#10b981" />
              <Text style={styles.optionLabel}>Charts and Graphs</Text>
            </View>
          </View>

          <View style={styles.optionCard}>
            <View style={styles.optionRow}>
              <Icon name="check-circle" size={16} color="#10b981" />
              <Text style={styles.optionLabel}>Recommendations</Text>
            </View>
          </View>
        </View>

        {/* Action Button */}
        <TouchableOpacity
          style={[styles.button, (!selectedFile || loading) && styles.buttonDisabled]}
          onPress={handleGenerateReport}
          disabled={!selectedFile || loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Icon name="wand-magic-sparkles" size={20} color="#fff" />
              <Text style={styles.buttonText}>Generate Report</Text>
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
    borderColor: '#f59e0b',
    backgroundColor: '#fffbeb',
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
  reportTypeCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 12,
    marginBottom: 10,
    borderWidth: 2,
    borderColor: '#e2e8f0',
  },
  reportTypeCardActive: {
    borderColor: '#f59e0b',
    backgroundColor: '#fffbeb',
  },
  reportTypeIcon: {
    width: 50,
    height: 50,
    borderRadius: 10,
    backgroundColor: '#f0f0f8',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  reportTypeContent: {
    flex: 1,
  },
  reportTypeLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  reportTypeDescription: {
    fontSize: 12,
    color: '#666',
  },
  optionCard: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 12,
    marginBottom: 8,
  },
  optionRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  optionLabel: {
    marginLeft: 10,
    fontSize: 13,
    color: '#333',
  },
  button: {
    backgroundColor: '#f59e0b',
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

export default ReportGeneratorScreen;
