import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, ActivityIndicator, StyleSheet, RefreshControl, Alert, TouchableOpacity } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authAPI } from '../../services/api';

const ProfileScreen = () => {
  const navigation = useNavigation();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  const handleLogout = async () => {
    try {
      await AsyncStorage.removeItem('access_token');
      await AsyncStorage.removeItem('refresh_token');
      await AsyncStorage.removeItem('farmer_profile');
      navigation.reset({ index: 0, routes: [{ name: 'Login' }] });
    } catch (err) {
      Alert.alert('Logout failed', 'Please try again.');
    }
  };

  const fetchProfile = async () => {
    try {
      setError(null);
      const data = await authAPI.getProfile();
      setProfile(data);
      await AsyncStorage.setItem('farmer_profile', JSON.stringify(data));
    } catch (err) {
      console.log('Profile fetch error:', err?.response?.data || err);
      try {
        const saved = await AsyncStorage.getItem('farmer_profile');
        if (saved) setProfile(JSON.parse(saved));
        else setError('Unable to load profile');
      } catch (cacheErr) {
        setError('Unable to load profile');
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchProfile();
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN');
  };

  // Helper to get initials for the avatar
  const getInitial = (name) => {
    return name && name.length > 0 ? name.charAt(0).toUpperCase() : 'A';
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#1F4A32" />
      </View>
    );
  }

  if (error || !profile) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>{error || 'Profile not found'}</Text>
      </View>
    );
  }

  return (
    <View style={styles.mainWrapper}>
      <ScrollView
        style={styles.container}
        showsVerticalScrollIndicator={false}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#1F4A32" />}
      >
        {/* Header Section */}
        <View style={styles.headerContainer}>
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Text style={styles.backText}>‹ Back</Text>
          </TouchableOpacity>
          <View style={styles.avatarCircle}>
            <Text style={styles.avatarText}>{getInitial(profile.name)}</Text>
          </View>
        </View>

        <Text style={styles.pageTitle}>Account Overview</Text>

        {/* Personal Details Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Personal Details</Text>
          
          <View style={styles.row}>
            <Text style={styles.label}>Name</Text>
            <Text style={styles.value}>{profile.name || 'Not set'}</Text>
          </View>
          <View style={styles.divider} />
          
          <View style={styles.row}>
            <Text style={styles.label}>Phone</Text>
            <Text style={styles.value}>{profile.phone}</Text>
          </View>
          <View style={styles.divider} />

          <View style={styles.row}>
            <Text style={styles.label}>Language</Text>
            <Text style={styles.value}>{profile.language}</Text>
          </View>
          <View style={styles.divider} />

          <View style={styles.row}>
            <Text style={styles.label}>Profile Status</Text>
            <View style={[styles.badge, { backgroundColor: profile.is_profile_complete ? '#EAF5EC' : '#FFF5D1' }]}>
              <Text style={[styles.badgeText, { color: profile.is_profile_complete ? '#197A30' : '#B28600' }]}>
                {profile.is_profile_complete ? 'Complete' : 'Incomplete'}
              </Text>
            </View>
          </View>
          <View style={styles.divider} />

          <View style={styles.row}>
            <Text style={styles.label}>Member Since</Text>
            <Text style={styles.value}>{formatDate(profile.created_at)}</Text>
          </View>
        </View>

        {/* Farm Details Card */}
        <Text style={styles.sectionTitle}>Farm Details</Text>
        <View style={styles.card}>
          {profile.farm ? (
            <>
              <View style={styles.row}>
                <Text style={styles.label}>Crop Type</Text>
                <Text style={styles.value}>{profile.farm.crop_type || 'N/A'}</Text>
              </View>
              <View style={styles.divider} />
              
              <View style={styles.row}>
                <Text style={styles.label}>Area</Text>
                <Text style={styles.value}>{profile.farm.area_acres ? `${profile.farm.area_acres} acres` : 'N/A'}</Text>
              </View>
              <View style={styles.divider} />
              
              <View style={styles.row}>
                <Text style={styles.label}>Soil Type</Text>
                <Text style={styles.value}>{profile.farm.soil_type || 'N/A'}</Text>
              </View>
              <View style={styles.divider} />
              
              <View style={styles.row}>
                <Text style={styles.label}>Location</Text>
                <Text style={styles.value}>
                  {profile.farm.location ? `${profile.farm.location.coordinates?.[1]?.toFixed(4)}, ${profile.farm.location.coordinates?.[0]?.toFixed(4)}` : 'N/A'}
                </Text>
              </View>
            </>
          ) : (
            <Text style={styles.noFarm}>No farm data available. Tap edit to update your farm information.</Text>
          )}
        </View>

        {/* Logout Button */}
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutText}>Log Out</Text>
        </TouchableOpacity>
        
        <View style={{ height: 40 }} />
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  mainWrapper: {
    flex: 1,
    backgroundColor: '#E6F5EA', // Light organic green background
  },
  container: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 10,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#E6F5EA',
  },
  headerContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 10,
    marginBottom: 20,
  },
  backButton: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 20, // Pill shape
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  backText: {
    color: '#1F4A32',
    fontWeight: '600',
    fontSize: 14,
  },
  avatarCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#1F4A32',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 4,
  },
  avatarText: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: 'bold',
  },
  pageTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F4A32', // Deep forest green
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F4A32',
    marginTop: 24,
    marginBottom: 12,
    marginLeft: 4,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.04,
    shadowRadius: 16,
    elevation: 3, // For Android shadow
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F4A32',
    marginBottom: 16,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 4,
  },
  label: {
    color: '#4F6B5C', // Muted grey-green
    fontWeight: '500',
    fontSize: 14,
  },
  value: {
    color: '#1F4A32',
    fontWeight: '600',
    fontSize: 15,
  },
  divider: {
    height: 1,
    backgroundColor: '#F0F4F1',
    marginVertical: 12,
  },
  badge: {
    paddingVertical: 4,
    paddingHorizontal: 12,
    borderRadius: 12,
  },
  badgeText: {
    fontWeight: '700',
    fontSize: 12,
  },
  noFarm: {
    color: '#4F6B5C',
    fontStyle: 'italic',
    lineHeight: 20,
  },
  logoutButton: {
    marginTop: 40,
    paddingVertical: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 999, // Pill shape
    borderWidth: 1,
    borderColor: '#F8D7DA',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  logoutText: {
    color: '#D32F2F', // Clean red for logout
    fontWeight: '700',
    fontSize: 16,
  },
  errorText: {
    color: '#D32F2F',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default ProfileScreen;