import React, {useState} from 'react'
import { SafeAreaView } from 'react-native'
import LoginScreen from './src/screens/auth/LoginScreen'
import SignupScreen from './src/screens/auth/SignupScreen'

const App = () => {
  const [route, setRoute] = useState('login')

  return (
    <SafeAreaView style={{flex:1}}>
      {route === 'login' && (
        <LoginScreen
          onSignupPress={() => setRoute('signup')}
          onLoginPress={(creds) => console.log('Login:', creds)}
        />
      )}
      {route === 'signup' && (
        <SignupScreen
          onCancel={() => setRoute('login')}
          onSignup={(data) => { console.log('Signup:', data); setRoute('login') }}
        />
      )}
    </SafeAreaView>
  )
}

export default App