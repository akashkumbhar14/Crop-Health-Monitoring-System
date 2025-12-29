import React from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';

const Loader = ({ visible = false }) => {
  if (!visible) return null;

  return (
    <View style={styles.overlay}>
      <ActivityIndicator size="large" color="#2E7D32" />
    </View>
  );
};

export default Loader;

const styles = StyleSheet.create({
  overlay: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    right: 0,
    left: 0,
    backgroundColor: 'rgba(255, 255, 255, 0.7)',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 999,
  },
});
