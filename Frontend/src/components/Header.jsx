import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function Header({ title, subtitle }) {
  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      <View style={styles.container}>
        <Text style={styles.title}>{title}</Text>
        {subtitle && <Text style={styles.subtitle}>{subtitle}</Text>}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    backgroundColor: '#2E7D32',
  },
  container: {
    paddingHorizontal: 20,
    paddingBottom: 16,
  },
  title: {
    color: '#fff',
    fontSize: 22,
    fontWeight: '700',
  },
  subtitle: {
    color: '#E8F5E9',
    fontSize: 14,
    marginTop: 4,
  },
});
