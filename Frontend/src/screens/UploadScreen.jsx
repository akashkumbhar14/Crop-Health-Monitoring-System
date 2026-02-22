import React, { useState } from 'react'
import { View, Text, StyleSheet, Image, Alert } from 'react-native'
import PrimaryButton from './components/PrimaryButton'
import { launchImageLibrary } from 'react-native-image-picker'
import { fakePredict } from '../utils'

export default function UploadScreen({ navigation }) {
  const [photo, setPhoto] = useState(null)

  const pickImage = () => {
    launchImageLibrary({ mediaType: 'photo' }, (res) => {
      if (res.didCancel) return
      if (res.errorCode) {
        Alert.alert('Error', res.errorMessage || 'Unknown error')
        return
      }
      const asset = res.assets && res.assets[0]
      if (asset) setPhoto(asset.uri)
    })
  }

  const handleAnalyze = () => {
    const result = fakePredict()
    navigation.navigate('Result', { ...result, image: photo })
  }

  return (
    <View style={styles.container}>
      {!photo ? (
        <View style={{ gap: 12 }}>
          <Text style={styles.instructions}>Select an image from your gallery</Text>
          <PrimaryButton title="Pick Image" onPress={pickImage} />
        </View>
      ) : (
        <View style={{ alignItems: 'center' }}>
          <Image source={{ uri: photo }} style={styles.preview} />
          <PrimaryButton title="Analyze" onPress={handleAnalyze} style={{ marginTop: 12 }} />
          <PrimaryButton title="Choose Another" onPress={() => setPhoto(null)} style={{ marginTop: 8, backgroundColor: '#666' }} />
        </View>
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: '#f6fdf7', justifyContent: 'center' },
  instructions: { fontSize: 16, color: '#2e7d32', marginBottom: 8 },
  preview: { width: 300, height: 300, borderRadius: 8, resizeMode: 'cover' },
})
