import { TextInput, View, Text, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Header from '../src/components/Header';
import CustomButton from '../src/components/CustomButton';
import { useRouter } from 'expo-router';

export default function Login() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.safe}>
      <Header title="Login" subtitle="Access your account" />

      <View style={styles.form}>
        <TextInput
          placeholder="Phone Number"
          keyboardType="phone-pad"
          style={styles.input}
        />

        <CustomButton
          title="Login"
          onPress={() => router.replace('/home')}
        />

        <Text
          style={styles.link}
          onPress={() => router.push('/register')}
        >
          New user? Register
        </Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: '#fff',
  },
  form: {
    padding: 20,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  },
  link: {
    marginTop: 16,
    color: '#2E7D32',
    textAlign: 'center',
  },
});
