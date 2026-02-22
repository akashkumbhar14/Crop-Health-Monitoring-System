import React from 'react'
import { View, Text, StyleSheet, Image, ScrollView } from 'react-native'
import PrimaryButton from './components/PrimaryButton'

export default function ResultScreen({ route, navigation }) {
  const { disease = 'Unknown', confidence = '0', treatment = '', image } = route.params || {}

  return (
    <ScrollView contentContainerStyle={styles.container}>
      {image ? <Image source={{ uri: image }} style={styles.image} /> : null}
      <View style={styles.card}>
        <Text style={styles.label}>Disease</Text>
        <Text style={styles.value}>{disease}</Text>

        <Text style={[styles.label, { marginTop: 12 }]}>Confidence</Text>
        <Text style={styles.value}>{confidence}%</Text>

        <Text style={[styles.label, { marginTop: 12 }]}>Treatment Suggestion</Text>
        <Text style={styles.treatment}>{treatment}</Text>
      </View>

      <PrimaryButton title="Back to Dashboard" onPress={() => navigation.popToTop()} style={{ marginTop: 20 }} />
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container: { padding: 20, alignItems: 'center', backgroundColor: '#f7fff8', minHeight: '100%' },
  image: { width: 320, height: 320, borderRadius: 8, marginBottom: 12 },
  card: { width: '100%', backgroundColor: '#fff', padding: 16, borderRadius: 10, elevation: 2 },
  label: { color: '#2e7d32', fontWeight: '700' },
  value: { fontSize: 18, marginTop: 6, color: '#1a3d1a' },
  treatment: { marginTop: 6, color: '#333' },
})
