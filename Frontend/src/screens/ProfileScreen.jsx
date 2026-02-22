import React from 'react'
import { View, Text, StyleSheet, Alert } from 'react-native'
import PrimaryButton from './components/PrimaryButton'

export default function ProfileScreen({ navigation, route }) {
  const email = route?.params?.email || 'admin@gmail.com'

  const handleLogout = () => {
    navigation.replace('Login')
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Profile</Text>
      <View style={styles.card}>
        <Text style={styles.label}>Email</Text>
        <Text style={styles.value}>{email}</Text>
      </View>

      <PrimaryButton title="Logout" onPress={handleLogout} style={{ marginTop: 20, backgroundColor: '#c0392b' }} />
    </View>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: '#f5fbf6' },
  title: { fontSize: 22, fontWeight: '700', color: '#184d2b' },
  card: { marginTop: 14, backgroundColor: '#fff', padding: 14, borderRadius: 8 },
  label: { color: '#2e7d32', fontWeight: '700' },
  value: { marginTop: 6, color: '#333' },
})
