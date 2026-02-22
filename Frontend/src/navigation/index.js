import React from 'react'
import { createNativeStackNavigator } from '@react-navigation/native-stack'
import LoginScreen from '../screens/auth/LoginScreen'
import SignupScreen from '../screens/auth/SignupScreen'
import DashboardScreen from '../screens/DashboardScreen'
import CameraScreen from '../screens/CameraScreen'
import UploadScreen from '../screens/UploadScreen'
import ResultScreen from '../screens/ResultScreen'
import ProfileScreen from '../screens/ProfileScreen'
import 'react-native-gesture-handler';
const Stack = createNativeStackNavigator()

export default function AppNavigator() {
  return (
    <Stack.Navigator initialRouteName="Login">
      <Stack.Screen name="Login" component={LoginScreen} options={{ headerShown: false }} />
      <Stack.Screen name="Signup" component={SignupScreen} options={{ title: 'Sign up' }} />
      <Stack.Screen name="Dashboard" component={DashboardScreen} options={{ title: 'Dashboard' }} />
      <Stack.Screen name="Camera" component={CameraScreen} options={{ title: 'Scan Crop' }} />
      <Stack.Screen name="Upload" component={UploadScreen} options={{ title: 'Upload Image' }} />
      <Stack.Screen name="Result" component={ResultScreen} options={{ title: 'Result' }} />
      <Stack.Screen name="Profile" component={ProfileScreen} options={{ title: 'Profile' }} />
    </Stack.Navigator>
  )
}
