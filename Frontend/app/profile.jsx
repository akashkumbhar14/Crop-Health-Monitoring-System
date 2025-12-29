import { View, Text, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Header from '../src/components/Header';
import CustomButton from '../src/components/CustomButton';
import { useRouter } from 'expo-router';

export default function Profile() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.safe}>
      <Header title="Profile" subtitle="Farmer Details" />

      <View style={styles.content}>
        <Text style={styles.item}>Name: Akash Kumbhar</Text>
        <Text style={styles.item}>Role: Farmer</Text>
        <Text style={styles.item}>Location: Maharashtra</Text>

        <CustomButton
          title="Logout"
          onPress={() => router.replace('/login')}
          style={{ marginTop: 20 }}
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
    padding: 20,
  },
  item: {
    fontSize: 16,
    marginBottom: 12,
  },
});
