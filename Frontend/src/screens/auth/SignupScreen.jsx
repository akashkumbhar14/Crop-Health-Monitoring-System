import React, {useState} from 'react'
import { View, Text, StyleSheet, TextInput, TouchableOpacity, KeyboardAvoidingView, Platform } from 'react-native'

export default function SignupScreen({ onCancel = () => {}, onSignup = () => {} }) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')

  const handleSignup = () => {
    onSignup({ name, email, phone, password })
  }

  return (
    <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <View style={styles.header}>
        <Text style={styles.appTitle}>Create account</Text>
        <Text style={styles.appSubtitle}>Join Crop Health Monitor</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.label}>Full name</Text>
        <TextInput value={name} onChangeText={setName} placeholder="Jane Farmer" style={styles.input} />

        <Text style={[styles.label, {marginTop:12}]}>Email</Text>
        <TextInput value={email} onChangeText={setEmail} placeholder="you@example.com" style={styles.input} keyboardType="email-address" autoCapitalize="none" />

        <Text style={[styles.label, {marginTop:12}]}>Phone</Text>
        <TextInput value={phone} onChangeText={setPhone} placeholder="+123456789" style={styles.input} keyboardType="phone-pad" />

        <Text style={[styles.label, {marginTop:12}]}>Password</Text>
        <TextInput value={password} onChangeText={setPassword} placeholder="Create a password" style={styles.input} secureTextEntry />

        <TouchableOpacity style={styles.button} onPress={handleSignup}>
          <Text style={styles.buttonText}>Create account</Text>
        </TouchableOpacity>

        <View style={styles.rowRight}>
          <Text style={styles.smallText}>Already have an account?</Text>
          <TouchableOpacity onPress={onCancel}>
            <Text style={styles.link}> Log in</Text>
          </TouchableOpacity>
        </View>
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
  smallText: { color: '#6b6f62' },
  link: { color: '#2e7d32', fontWeight: '700' },
  rowRight: { flexDirection: 'row', justifyContent: 'flex-end', marginTop: 12, alignItems: 'center' },
})
