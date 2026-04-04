import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  SafeAreaView,
} from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authAPI } from '../../services/api';

const SignupScreen = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const phone = route.params?.phone || '+919876543210'; // Fallback for UI testing

  const [name, setName] = useState('');
  const [language, setLanguage] = useState('english');
  const [loading, setLoading] = useState(false);

  const languages = [
    { label: 'English', value: 'english' },
    { label: 'Marathi', value: 'marathi' },
    { label: 'Hindi', value: 'hindi' },
    { label: 'Kannada', value: 'kannada' },
    { label: 'Telugu', value: 'telugu' },
  ];

  const handleCompleteProfile = async () => {
    if (!name.trim()) {
      Alert.alert('Error', 'Enter your name');
      return;
    }

    try {
      setLoading(true);

      const res = await authAPI.completeProfile({
        phone,
        name: name.trim(),
        language,
      });

      console.log("PROFILE RESPONSE:", res);

      // Store farmer profile
      await AsyncStorage.setItem('farmer_profile', JSON.stringify(res));

      // Navigate to Home Screen
      navigation.navigate('Home');

    } catch (error) {
      console.log('PROFILE ERROR:', error?.response?.data || error);

      Alert.alert(
        'Error',
        error.response?.data?.detail || 'Failed to complete profile'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.container}
      >
        <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
          
          {/* Top Navigation Row */}
          <View style={styles.topRow}>
            <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
              <Text style={styles.backText}>‹ Back</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.logoutButton} onPress={async () => {
              await AsyncStorage.removeItem('access_token');
              await AsyncStorage.removeItem('refresh_token');
              await AsyncStorage.removeItem('farmer_profile');
              navigation.reset({ index: 0, routes: [{ name: 'Login' }] });
            }}>
              <Text style={styles.logoutText}>Reset</Text>
            </TouchableOpacity>
          </View>

          {/* Main Form Card */}
          <View style={styles.card}>
            <View style={styles.brandIconContainer}>
              <Text style={styles.brandIcon}>🧑‍🌾</Text>
            </View>

            <Text style={styles.title}>Complete Profile</Text>
            <Text style={styles.subtitle}>Let's get your account set up</Text>

            {/* Phone Display (Read Only) */}
            <View style={styles.infoBox}>
              <Text style={styles.infoLabel}>Verified Phone Number</Text>
              <Text style={styles.infoValue}>{phone}</Text>
            </View>

            {/* Name Input */}
            <View style={styles.inputContainer}>
              <Text style={styles.label}>Full Name</Text>
              <TextInput
                style={styles.input}
                placeholder="e.g., Ramesh Patil"
                value={name}
                onChangeText={setName}
                editable={!loading}
                placeholderTextColor="#8EA696"
              />
            </View>

            {/* Language Selection */}
            <View style={styles.inputContainer}>
              <Text style={styles.label}>Preferred Language</Text>
              <View style={styles.languageOptions}>
                {languages.map((lang) => (
                  <TouchableOpacity
                    key={lang.value}
                    style={[
                      styles.languageChip,
                      language === lang.value && styles.languageChipSelected,
                    ]}
                    onPress={() => setLanguage(lang.value)}
                    disabled={loading}
                  >
                    <Text
                      style={[
                        styles.languageText,
                        language === lang.value && styles.languageTextSelected,
                      ]}
                    >
                      {lang.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {/* Submit Button */}
            <TouchableOpacity
              style={[styles.button, loading && styles.buttonDisabled]}
              onPress={handleCompleteProfile}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#FFFFFF" />
              ) : (
                <Text style={styles.buttonText}>Complete Setup</Text>
              )}
            </TouchableOpacity>

            <Text style={styles.note}>
              You can add farm details and other information later from your profile dashboard.
            </Text>
          </View>

        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#E6F5EA', // Light organic green
  },
  container: {
    flex: 1,
  },
  content: {
    paddingHorizontal: 20,
    paddingVertical: Platform.OS === 'android' ? 20 : 10,
    minHeight: '100%',
    justifyContent: 'center',
  },
  topRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  backButton: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  backText: {
    color: '#1F4A32',
    fontWeight: '600',
    fontSize: 14,
  },
  logoutButton: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#F8D7DA',
  },
  logoutText: {
    color: '#D32F2F',
    fontWeight: '600',
    fontSize: 14,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 28,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.05,
    shadowRadius: 20,
    elevation: 4,
  },
  brandIconContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#F4F7F3',
    justifyContent: 'center',
    alignItems: 'center',
    alignSelf: 'center',
    marginBottom: 16,
  },
  brandIcon: {
    fontSize: 32,
  },
  title: {
    fontSize: 26,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 6,
    color: '#1F4A32',
  },
  subtitle: {
    fontSize: 15,
    textAlign: 'center',
    color: '#4F6B5C',
    marginBottom: 28,
  },
  infoBox: {
    backgroundColor: '#F4F7F3',
    borderWidth: 1,
    borderColor: '#D1E8DA',
    padding: 16,
    borderRadius: 16,
    marginBottom: 24,
    alignItems: 'center',
  },
  infoLabel: {
    fontSize: 12,
    color: '#4F6B5C',
    fontWeight: '600',
    marginBottom: 4,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  infoValue: {
    fontSize: 18,
    color: '#1F4A32',
    fontWeight: 'bold',
  },
  inputContainer: {
    marginBottom: 24,
    width: '100%',
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F4A32',
    marginBottom: 8,
    marginLeft: 4,
  },
  input: {
    backgroundColor: '#F4F7F3',
    borderWidth: 1,
    borderColor: '#D1E8DA',
    borderRadius: 16,
    paddingHorizontal: 16,
    paddingVertical: 16,
    fontSize: 16,
    color: '#1F4A32',
  },
  languageOptions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 4,
  },
  languageChip: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#D1E8DA',
    borderRadius: 999, // Pill shape
    marginRight: 10,
    marginBottom: 10,
    paddingVertical: 10,
    paddingHorizontal: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 4,
    elevation: 1,
  },
  languageChipSelected: {
    backgroundColor: '#86B342', // Accent green
    borderColor: '#86B342',
    shadowColor: '#86B342',
    shadowOpacity: 0.3,
    elevation: 3,
  },
  languageText: {
    color: '#4F6B5C',
    fontSize: 14,
    fontWeight: '600',
  },
  languageTextSelected: {
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  button: {
    backgroundColor: '#1F4A32',
    paddingVertical: 16,
    borderRadius: 999, // Pill shape
    alignItems: 'center',
    marginTop: 8,
    shadowColor: '#1F4A32',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 4,
  },
  buttonDisabled: {
    backgroundColor: '#8EA696',
    shadowOpacity: 0,
    elevation: 0,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  note: {
    fontSize: 13,
    color: '#4F6B5C',
    textAlign: 'center',
    marginTop: 20,
    lineHeight: 20,
  },
});

export default SignupScreen;