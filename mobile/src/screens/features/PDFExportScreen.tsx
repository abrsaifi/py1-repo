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

interface PDFExportScreenProps {
  navigation: any;
}

export const PDFExportScreen: React.FC<PDFExportScreenProps> = ({ navigation }) => {
  const [selectedFile, setSelectedFile] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState<'pdf' | 'excel' | 'json'>('pdf');

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

  const handleExport = async () => {
    if (!selectedFile) {
      Alert.alert('Error', 'Please select a file');
      return;
    }

    setLoading(true);
    try {
      Alert.alert('Success', `File exported to ${selectedFormat.toUpperCase()} successfully!`);
    } catch (error) {
      Alert.alert('Error', error instanceof Error ? error.message : 'Export failed');
    } finally {
      setLoading(false);
    }
  };

  const formats = [
    { id: 'pdf' as const, label: 'PDF', icon: 'file-pdf', color: '#ef4444' },
    { id: 'excel' as const, label: 'Excel', icon: 'file-excel', color: '#10b981' },
    { id: 'json' as const, label: 'JSON', icon: 'file-code', color: '#f59e0b' },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Icon name="file-pdf" size={48} color="#ef4444" />
          <Text style={styles.title}>Export to PDF</Text>
          <Text style={styles.description}>Convert your files to different formats</Text>
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
              color={selectedFile ? '#ef4444' : '#667eea'}
            />
            <View style={styles.filePickerContent}>
              <Text style={styles.filePickerTitle}>
                {selectedFile ? 'File Selected' : 'Choose File'}
              </Text>
              <Text style={styles.filePickerSubtitle}>
                {selectedFile ? selectedFile.name : 'Any file type'}
              </Text>
            </View>
          </TouchableOpacity>
        </View>

        {/* Format Selection */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Export Format</Text>
          
          <View style={styles.formatGrid}>
            {formats.map((format) => (
              <TouchableOpacity
                key={format.id}
                style={[
                  styles.formatCard,
                  selectedFormat === format.id && styles.formatCardActive,
                ]}
                onPress={() => setSelectedFormat(format.id)}
              >
                <Icon name={format.icon} size={32} color={format.color} />
                <Text style={styles.formatLabel}>{format.label}</Text>
                {selectedFormat === format.id && (
                  <Icon
                    name="check-circle"
                    size={20}
                    color={format.color}
                    style={styles.checkmark}
                  />
                )}
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Options */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Options</Text>
          
          <View style={styles.optionCard}>
            <View style={styles.optionRow}>
              <Text style={styles.optionLabel}>Include headers</Text>
              <View style={styles.toggle}>
                <View style={styles.toggleActive} />
              </View>
            </View>
          </View>

          <View style={styles.optionCard}>
            <View style={styles.optionRow}>
              <Text style={styles.optionLabel}>Compress file</Text>
              <View style={styles.toggle}>
                <View style={styles.toggleActive} />
              </View>
            </View>
          </View>
        </View>

        {/* Action Button */}
        <TouchableOpacity
          style={[styles.button, (!selectedFile || loading) && styles.buttonDisabled]}
          onPress={handleExport}
          disabled={!selectedFile || loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Icon name="file-arrow-down" size={20} color="#fff" />
              <Text style={styles.buttonText}>Export File</Text>
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
    borderColor: '#ef4444',
    backgroundColor: '#fef2f2',
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
  formatGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  formatCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 12,
    alignItems: 'center',
    marginHorizontal: 4,
    borderWidth: 2,
    borderColor: '#e2e8f0',
  },
  formatCardActive: {
    borderColor: '#ef4444',
    backgroundColor: '#fef2f2',
  },
  formatLabel: {
    fontSize: 12,
    color: '#333',
    fontWeight: '600',
    marginTop: 8,
  },
  checkmark: {
    position: 'absolute',
    top: 8,
    right: 8,
  },
  optionCard: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 12,
    marginBottom: 8,
  },
  optionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
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
    backgroundColor: '#ef4444',
  },
  button: {
    backgroundColor: '#ef4444',
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

export default PDFExportScreen;
