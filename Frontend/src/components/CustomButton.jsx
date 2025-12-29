import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';

const CustomButton = ({
  title,
  onPress,
  loading = false,
  disabled = false,
  style,
  textStyle,
}) => {
  const isDisabled = disabled || loading;

  return (
    <TouchableOpacity
      style={[
        styles.button,
        isDisabled && styles.disabled,
        style,
      ]}
      onPress={onPress}
      activeOpacity={0.8}
      disabled={isDisabled}
    >
      {loading ? (
        <ActivityIndicator color="#ffffff" />
      ) : (
        <Text style={[styles.text, textStyle]}>
          {title}
        </Text>
      )}
    </TouchableOpacity>
  );
};

export default CustomButton;

const styles = StyleSheet.create({
  button: {
    height: 48,
    backgroundColor: '#2E7D32',
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 16,
  },
  disabled: {
    backgroundColor: '#9E9E9E',
  },
  text: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
});
