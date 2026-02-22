import React, { useState } from 'react'
import { View, Text, StyleSheet, TextInput, TouchableOpacity, Alert, KeyboardAvoidingView, Platform } from 'react-native'

export default function SignupScreen({ navigation }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleSignup = () => {
    // Demo signup: no persistence. Inform the user and go back to Login.
    Alert.alert('Signup complete', 'Account created (demo). You can now login.', [
      { text: 'Go to Login', onPress: () => navigation.replace('Login') },
    ])
  }

  return (
    <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <View style={styles.header}>
        <Text style={styles.appTitle}>Create account</Text>
        <Text style={styles.appSubtitle}>Join Crop Health Monitor</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.label}>Email</Text>
        <TextInput value={email} onChangeText={setEmail} placeholder="you@example.com" style={styles.input} keyboardType="email-address" autoCapitalize="none" />

        <Text style={[styles.label, { marginTop: 12 }]}>Password</Text>
        <TextInput value={password} onChangeText={setPassword} placeholder="Create a password" style={styles.input} secureTextEntry />

        <TouchableOpacity style={styles.button} onPress={handleSignup}>
          <Text style={styles.buttonText}>Create account</Text>
        </TouchableOpacity>

        <TouchableOpacity onPress={() => navigation.replace('Login')} style={{ marginTop: 12 }}>
          <Text style={styles.link}>Back to Login</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f3f7f2' },
  header: { backgroundColor: '#2e7d32', paddingVertical: 26, paddingHorizontal: 20, borderBottomLeftRadius: 24, borderBottomRightRadius: 24 },
  appTitle: { color: '#fff', fontSize: 20, fontWeight: '700' },
  appSubtitle: { color: '#e8f5e9', marginTop: 6 },
  card: { margin: 20, marginTop: 24, backgroundColor: '#fff', borderRadius: 12, padding: 16, shadowColor: '#000', shadowOpacity: 0.06, shadowRadius: 10, elevation: 4 },
  label: { color: '#2f3a2f', fontWeight: '600', marginBottom: 6 },
  input: { height: 46, borderColor: '#e6efe6', borderWidth: 1, borderRadius: 8, paddingHorizontal: 12, backgroundColor: '#fff' },
  button: { marginTop: 18, backgroundColor: '#388e3c', paddingVertical: 12, borderRadius: 8, alignItems: 'center' },
  buttonText: { color: '#fff', fontWeight: '700' },
  link: { color: '#2e7d32', fontWeight: '700', textAlign: 'center' },
})
