import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { authAPI } from '../../services/api';

const LoginScreen = ({ navigation }) => {
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [loading, setLoading] = useState(false);

  // 📌 SEND OTP
  const handleSendOTP = async () => {
    if (!phone.trim()) {
      Alert.alert('Error', 'Please enter phone number');
      return;
    }

    setLoading(true);
    try {
      const data = await authAPI.sendOTP({ phone: phone.trim() });

      setOtpSent(true);
      Alert.alert('Success', data.message || 'OTP sent');

      // DEV MODE OTP
      if (data.dev_otp) {
        Alert.alert('DEV OTP', data.dev_otp);
      }
    } catch (error) {
      console.log(error);
      Alert.alert('Error', error.response?.data?.detail || 'Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  // 📌 VERIFY OTP
  const handleVerifyOTP = async () => {
    if (!phone.trim()) {
      Alert.alert('Error', 'Please enter phone number');
      return;
    }

    if (!otp.trim()) {
      Alert.alert('Error', 'Please enter OTP');
      return;
    }

    setLoading(true);
    try {
      const data = await authAPI.verifyOTP({
        phone: phone.trim(),
        otp: otp.trim(),
      });

      if (data.is_new_farmer) {
        navigation.navigate('Signup', { phone: phone.trim() });
      } else {
        navigation.replace('Home');
      }
    } catch (error) {
      console.log(error);
      Alert.alert('Error', error.response?.data?.detail || 'Invalid OTP');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Welcome Back 🌱</Text>
      <Text style={styles.subtitle}>Crop Health Monitoring</Text>

      {!otpSent ? (
        <>
          <Text style={styles.label}>Phone Number</Text>
          <TextInput
            style={styles.input}
            placeholder="+919876543210"
            value={phone}
            onChangeText={setPhone}
            keyboardType="phone-pad"
            editable={!loading}
          />

          <TouchableOpacity
            style={[styles.button, loading && styles.buttonDisabled]}
            onPress={handleSendOTP}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Send OTP</Text>
            )}
          </TouchableOpacity>
        </>
      ) : (
        <>
          <Text style={styles.label}>Enter OTP</Text>
          <Text style={styles.info}>OTP sent to {phone}</Text>

          <TextInput
            style={styles.input}
            placeholder="000000"
            value={otp}
            onChangeText={setOtp}
            keyboardType="numeric"
            maxLength={6}
            editable={!loading}
          />

          <TouchableOpacity
            style={[styles.button, loading && styles.buttonDisabled]}
            onPress={handleVerifyOTP}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Verify OTP</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity onPress={() => setOtpSent(false)}>
            <Text style={styles.changePhoneText}>Change phone number?</Text>
          </TouchableOpacity>
        </>
      )}
    </View>
  );
};

export default LoginScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F4F7F3',
    justifyContent: 'center',
    paddingHorizontal: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    color: '#666',
    marginBottom: 30,
  },
  label: {
    fontSize: 14,
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  button: {
    backgroundColor: '#327941',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
  },
  info: {
    fontSize: 12,
    color: '#666',
    marginBottom: 10,
  },
  changePhoneText: {
    textAlign: 'center',
    marginTop: 16,
    color: '#327941',
  },
});