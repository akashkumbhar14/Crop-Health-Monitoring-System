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
  SafeAreaView,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authAPI } from '../../services/api';

const LoginScreen = () => {
  const navigation = useNavigation();
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSendOTP = async () => {
    if (!phone.trim()) {
      Alert.alert('Error', 'Enter phone number');
      return;
    }

    try {
      setLoading(true);

      const formattedPhone = phone.startsWith('+')
        ? phone.trim()
        : `+91${phone.trim()}`;

      const data = await authAPI.sendOTP({ phone: formattedPhone });

      setOtpSent(true);

      if (data.dev_otp) {
        Alert.alert('DEV OTP', data.dev_otp);
      }

    } catch (error) {
      console.log("SEND OTP ERROR:", error?.response?.data || error);

      Alert.alert(
        'Error',
        error.response?.data?.detail || 'Failed to send OTP'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async () => {
    if (!otp || otp.length !== 6) {
      Alert.alert('Error', 'Enter valid OTP');
      return;
    }

    try {
      setLoading(true);

      const formattedPhone = phone.startsWith('+')
        ? phone.trim()
        : `+91${phone.trim()}`;

      const res = await authAPI.verifyOTP({
        phone: formattedPhone,
        otp,
      });

      console.log("VERIFY RESPONSE:", res);

      if (res.is_new_farmer) {
        navigation.navigate('Signup', { phone: formattedPhone });
      } else {
        navigation.navigate('Home');
      }

    } catch (error) {
      console.log("VERIFY ERROR:", error?.response?.data || error);

      Alert.alert(
        'Error',
        error.response?.data?.detail || 'OTP failed'
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

        <View style={styles.content}>
          
          {/* Main Login Card */}
          <View style={styles.card}>
            <View style={styles.brandIconContainer}>
              <Text style={styles.brandIcon}>🌿</Text>
            </View>
            <Text style={styles.title}>AgriAI</Text>
            <Text style={styles.subtitle}>Intelligent Crop Health Monitoring</Text>

            {!otpSent ? (
              <View style={styles.formContainer}>
                <Text style={styles.label}>Phone Number</Text>
                <TextInput
                  style={styles.input}
                  placeholder="9876543210"
                  keyboardType="phone-pad"
                  value={phone}
                  onChangeText={setPhone}
                  editable={!loading}
                  placeholderTextColor="#8EA696"
                />

                <TouchableOpacity
                  style={[styles.button, loading && styles.buttonDisabled]}
                  onPress={handleSendOTP}
                  disabled={loading}
                >
                  {loading ? (
                    <ActivityIndicator color="#FFFFFF" />
                  ) : (
                    <Text style={styles.buttonText}>Send OTP</Text>
                  )}
                </TouchableOpacity>
              </View>
            ) : (
              <View style={styles.formContainer}>
                <Text style={styles.label}>Enter Verification Code</Text>
                <Text style={styles.otpHint}>Secure code sent to {phone}</Text>

                <TextInput
                  style={[styles.input, styles.otpInput]}
                  placeholder="000000"
                  keyboardType="number-pad"
                  maxLength={6}
                  value={otp}
                  onChangeText={setOtp}
                  editable={!loading}
                  placeholderTextColor="#8EA696"
                />

                <TouchableOpacity
                  style={[styles.button, loading && styles.buttonDisabled]}
                  onPress={handleVerifyOTP}
                  disabled={loading}
                >
                  {loading ? (
                    <ActivityIndicator color="#FFFFFF" />
                  ) : (
                    <Text style={styles.buttonText}>Verify & Login</Text>
                  )}
                </TouchableOpacity>

                <TouchableOpacity onPress={() => { setOtpSent(false); setOtp(''); }} style={styles.linkButton}>
                  <Text style={styles.linkText}>Change Phone Number</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>

        </View>
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
  topRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: Platform.OS === 'android' ? 20 : 10,
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
  content: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: 20,
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
    alignItems: 'center',
  },
  brandIconContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#F4F7F3',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  brandIcon: {
    fontSize: 32,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F4A32', // Deep forest green
    marginBottom: 6,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 15,
    color: '#4F6B5C', // Muted grey-green
    textAlign: 'center',
    marginBottom: 32,
  },
  formContainer: {
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
    marginBottom: 24,
    fontSize: 16,
    color: '#1F4A32',
  },
  otpInput: {
    textAlign: 'center',
    fontSize: 24,
    fontWeight: 'bold',
    letterSpacing: 4,
  },
  button: {
    backgroundColor: '#1F4A32',
    paddingVertical: 16,
    borderRadius: 999, // Pill shape
    alignItems: 'center',
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
  otpHint: {
    fontSize: 13,
    color: '#4F6B5C',
    marginBottom: 16,
    marginLeft: 4,
  },
  linkButton: {
    marginTop: 20,
    paddingVertical: 8,
    alignItems: 'center',
  },
  linkText: {
    color: '#86B342', // Accent green
    fontSize: 14,
    fontWeight: 'bold',
  },
});

export default LoginScreen;