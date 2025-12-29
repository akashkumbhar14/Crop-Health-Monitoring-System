import { StyleSheet, Text, View, TextInput } from 'react-native';
import CustomButton from '../src/components/CustomButton';
import Header from '../src/components/Header';
import { useRouter } from 'expo-router';

export default function Login() {
  const router = useRouter();

  return (
    <View style={styles.container}>
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
          New user? Register here
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
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
