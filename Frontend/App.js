import 'react-native-gesture-handler'
import React from 'react'
import { SafeAreaProvider } from 'react-native-safe-area-context'
import { NavigationContainer } from '@react-navigation/native'
import { enableScreens } from 'react-native-screens'
import AppNavigator from './src/navigation'
// Using the JS stack navigator avoids relying on native view managers
// so we don't require react-native-screens to register native view managers.

export default function App() {
  enableScreens()
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <AppNavigator />
      </NavigationContainer>
    </SafeAreaProvider>
  )
}
