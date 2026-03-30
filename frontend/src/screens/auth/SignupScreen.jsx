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
import { Picker } from '@react-native-picker/picker';
import { authAPI } from '../../services/api';

const SignupScreen = ({ navigation, route }) => {
  const { phone } = route.params;

  const [name, setName] = useState('');
  const [language, setLanguage] = useState('english');
  const [loading, setLoading] = useState(false);

  const handleCompleteProfile = async () => {
    if (!name.trim()) {
      Alert.alert('Error', 'Enter your name');
      return;
    }

    setLoading(true);
    try {
      await authAPI.completeProfile({
        phone,
        name: name.trim(),
        language,
      });

      Alert.alert('Success', 'Profile completed');
      navigation.replace('Home');
    } catch (error) {
      console.log(error);
      Alert.alert('Error', error.response?.data?.detail || 'Failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Complete Profile 🌱</Text>
      <Text style={styles.subtitle}>{phone}</Text>

      <Text style={styles.label}>Full Name</Text>
      <TextInput
        style={styles.input}
        placeholder="Your name"
        value={name}
        onChangeText={setName}
      />

      <Text style={styles.label}>Language</Text>
      <View style={styles.pickerContainer}>
        <Picker
          selectedValue={language}
          onValueChange={(itemValue) => setLanguage(itemValue)}
        >
          <Picker.Item label="English" value="english" />
          <Picker.Item label="Hindi" value="hindi" />
          <Picker.Item label="Marathi" value="marathi" />
        </Picker>
      </View>

      <TouchableOpacity style={styles.button} onPress={handleCompleteProfile}>
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Complete Signup</Text>
        )}
      </TouchableOpacity>
    </View>
  );
};

export default SignupScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#F4F7F3',
  },
  title: {
    fontSize: 26,
    textAlign: 'center',
    marginBottom: 10,
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: 20,
    color: '#666',
  },
  label: {
    marginBottom: 6,
  },
  input: {
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  pickerContainer: {
    backgroundColor: '#fff',
    borderRadius: 8,
    marginBottom: 20,
  },
  button: {
    backgroundColor: '#327941',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
  },
});