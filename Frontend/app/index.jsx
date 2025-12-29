import { Text, StyleSheet, Animated } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useEffect, useRef } from 'react';
import { useRouter } from 'expo-router';

export default function Index() {
  const router = useRouter();

  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.8)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 1000,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        friction: 6,
        useNativeDriver: true,
      }),
    ]).start();

    const timer = setTimeout(() => {
      router.replace('/home');
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <SafeAreaView style={styles.safe}>
      <Animated.View
        style={[
          styles.container,
          {
            opacity: fadeAnim,
            transform: [{ scale: scaleAnim }],
          },
        ]}
      >
        <Text style={styles.logo}>🌱</Text>
        <Text style={styles.title}>Crop Health</Text>
        <Text style={styles.subtitle}>
          Smart Crop Monitoring System
        </Text>
      </Animated.View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: '#2E7D32',
  },
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  logo: {
    fontSize: 60,
    marginBottom: 12,
  },
  title: {
    fontSize: 26,
    fontWeight: '700',
    color: '#fff',
  },
  subtitle: {
    fontSize: 14,
    color: '#E8F5E9',
    marginTop: 6,
  },
});
