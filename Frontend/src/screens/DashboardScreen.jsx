import React from 'react'
import { View, Text, StyleSheet } from 'react-native'
import PrimaryButton from './components/PrimaryButton'

export default function DashboardScreen({ navigation, route }) {
  const email = route?.params?.email || 'admin@gmail.com'

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Welcome</Text>
      <Text style={styles.subtitle}>{email}</Text>

      <View style={styles.actions}>
        <PrimaryButton title="Scan Crop" onPress={() => navigation.navigate('Camera', { email })} style={styles.btn} />
        <PrimaryButton title="Upload Image" onPress={() => navigation.navigate('Upload', { email })} style={styles.btn} />
        <PrimaryButton title="Reports" onPress={() => navigation.navigate('Result', { email })} style={styles.btn} />
        <PrimaryButton title="Profile" onPress={() => navigation.navigate('Profile', { email })} style={styles.btn} />
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: '#f5fbf6' },
  title: { fontSize: 24, fontWeight: '700', color: '#184d2b' },
  subtitle: { color: '#2e7d32', marginTop: 6 },
  actions: { marginTop: 28, gap: 12 },
  btn: { marginBottom: 12 },
})
