import { Text, View, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Header from '../src/components/Header';
import CustomButton from '../src/components/CustomButton';
import { useRouter } from 'expo-router';

export default function Home() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.safe}>
      <Header
        title="Crop Health"
        subtitle="Smart Crop Monitoring System"
      />

      <View style={styles.content}>
        <Text style={styles.text}>
          Welcome to Crop Health Monitoring System
        </Text>

        <CustomButton
          title="Profile"
          onPress={() => router.push('/profile')}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  },
  text: {
    fontSize: 16,
    marginBottom: 20,
    textAlign: 'center',
  },
});
