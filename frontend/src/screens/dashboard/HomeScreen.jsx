import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, ActivityIndicator, Alert, StyleSheet, RefreshControl, TouchableOpacity, Image } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authAPI } from '../../services/api';

const HomeScreen = () => {
  const navigation = useNavigation();
  const [profile, setProfile] = useState(null);
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  const fetchWeather = async (lat, lon) => {
    try {
      const res = await fetch(
        `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true&hourly=temperature_2m,relativehumidity_2m`,
      );
      const data = await res.json();

      if (data?.current_weather) {
        setWeather({
          temp: data.current_weather.temperature,
          wind: data.current_weather.windspeed,
          weatherCode: data.current_weather.weathercode,
          humidity: data.hourly?.relativehumidity_2m?.[0] ?? null,
          desc: data.current_weather.temperature > 25 ? 'Sunny & Clear' : 'Fair Weather',
        });
      }
    } catch (wErr) {
      console.log('Weather fetch failed:', wErr);
      setWeather(null);
    }
  };

  const fetchProfile = async () => {
    try {
      setError(null);
      const data = await authAPI.getProfile();
      setProfile(data);

      const lat = data?.farm?.location?.coordinates?.[1] || 20.5937;
      const lon = data?.farm?.location?.coordinates?.[0] || 78.9629;
      await fetchWeather(lat, lon);
      
      await AsyncStorage.setItem('farmer_profile', JSON.stringify(data));
    } catch (err) {
      console.log('Fetch profile error:', err?.response?.data || err);
      try {
        const cached = await AsyncStorage.getItem('farmer_profile');
        if (cached) {
          setProfile(JSON.parse(cached));
        } else {
          setError('Failed to load profile');
        }
      } catch (cacheErr) {
        setError('Failed to load profile');
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
        <Text style={styles.errorText}>{error || 'No profile data'}</Text>
      </View>
    );
  }

  // Helper to get initials if no avatar image is present
  const getInitial = (name) => (name && name.length > 0 ? name.charAt(0).toUpperCase() : 'A');

  return (
    <View style={styles.mainWrapper}>
      <ScrollView 
        style={styles.container}
        showsVerticalScrollIndicator={false}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#1F4A32" />}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.appTitle}>AgriAI</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Profile')} style={styles.avatarCircle}>
             {/* Using initial as fallback, replace with Image if you have user photos */}
            <Text style={styles.avatarText}>{getInitial(profile.name)}</Text>
          </TouchableOpacity>
        </View>

        {/* Primary Action Card (Upload Zone) */}
        <View style={styles.uploadCard}>
          <View style={styles.uploadIconPlaceholder}>
            <Text style={{fontSize: 24}}>🌿</Text>
          </View>
          <Text style={styles.cardTitle}>Take or Upload Photo</Text>
          <Text style={styles.cardDesc}>For instant crop health assessment</Text>
          <TouchableOpacity style={styles.actionButton}>
            <Text style={styles.actionButtonText}>Analyze Crop Leaf</Text>
          </TouchableOpacity>
        </View>

        {/* Recent Analyses */}
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Recent Analyses</Text>
          <TouchableOpacity>
            <Text style={styles.sectionAction}>See all</Text>
          </TouchableOpacity>
        </View>

        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.chipScroll}>
          <View style={styles.chip}><Text style={styles.chipText}>🌾 Rice</Text></View>
          <View style={styles.chip}><Text style={styles.chipText}>🌽 Wheat</Text></View>
          <View style={styles.chipActive}><Text style={styles.chipTextActive}>✓ Healthy</Text></View>
        </ScrollView>

        {/* Farm Overview Strip */}
        <Text style={styles.sectionTitle}>Farm Overview</Text>
        <View style={styles.overviewStrip}>
          <View style={styles.overviewCard}>
            <Text style={styles.overviewLabel}>Soil Moisture</Text>
            <Text style={[styles.overviewValue, { color: '#86B342' }]}>Good</Text>
          </View>
          <View style={styles.overviewCard}>
            <Text style={styles.overviewLabel}>Predicted Rain</Text>
            <Text style={styles.overviewValue}>None</Text>
          </View>
        </View>

        {/* Bottom Split Section: Weather & Metrics */}
        <View style={styles.splitRow}> 
          {/* Weather Card (Dark Mode Accent) */}
          <View style={styles.weatherCard}>
            <Text style={styles.weatherTitle}>Current Weather</Text>
            {weather ? (
              <View style={styles.weatherContent}>
                <Text style={styles.weatherTemp}>{Math.round(weather.temp)}°</Text>
                <Text style={styles.weatherSub}>{weather.desc}</Text>
                <View style={styles.weatherDetailsRow}>
                  <Text style={styles.weatherSmall}>💨 {weather.wind} km/h</Text>
                  {weather.humidity != null && <Text style={styles.weatherSmall}>💧 {weather.humidity}%</Text>}
                </View>
              </View>
            ) : (
              <Text style={styles.weatherSub}>Data unavailable</Text>
            )}
          </View>

          {/* Field Metrics Card */}
          <View style={styles.statusCard}>
            <Text style={styles.statusTitle}>Field Metrics</Text>
            <View style={styles.statusRow}>
              <View style={styles.metricBox}>
                <Text style={styles.metricValue}>92%</Text>
                <Text style={styles.metricLabel}>NPK</Text>
              </View>
              <View style={styles.metricBox}>
                <Text style={styles.metricValue}>88%</Text>
                <Text style={styles.metricLabel}>Fertilizer</Text>
              </View>
            </View>
            <View style={styles.statusRow}>
              <View style={styles.metricBox}>
                <Text style={styles.metricValue}>95%</Text>
                <Text style={styles.metricLabel}>Soil</Text>
              </View>
              <View style={styles.metricBox}>
                <Text style={[styles.metricValue, {color: '#E7B526'}]}>90%</Text>
                <Text style={styles.metricLabel}>Yield</Text>
              </View>
            </View>
          </View>
        </View>
        
        <View style={{ height: 40 }} />
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  mainWrapper: {
    flex: 1,
    backgroundColor: '#E6F5EA', // Light organic green
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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 10,
    marginBottom: 24,
  },
  appTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F4A32',
    letterSpacing: -0.5,
  },
  avatarCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 4,
  },
  avatarText: {
    color: '#1F4A32',
    fontSize: 18,
    fontWeight: 'bold',
  },
  uploadCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 24,
    marginBottom: 24,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#D1E8DA',
    borderStyle: 'dashed',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.04,
    shadowRadius: 16,
    elevation: 2,
  },
  uploadIconPlaceholder: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#F4F7F3',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  cardTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1F4A32',
    marginBottom: 6,
  },
  cardDesc: {
    color: '#4F6B5C',
    fontSize: 14,
    marginBottom: 20,
    textAlign: 'center',
  },
  actionButton: {
    backgroundColor: '#1F4A32',
    borderRadius: 999, // Pill shape
    paddingVertical: 14,
    paddingHorizontal: 32,
    width: '100%',
    alignItems: 'center',
    shadowColor: '#1F4A32',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 4,
  },
  actionButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F4A32',
    marginBottom: 12,
  },
  sectionAction: {
    color: '#86B342',
    fontWeight: 'bold',
    fontSize: 14,
  },
  chipScroll: {
    marginBottom: 24,
  },
  chip: {
    backgroundColor: '#FFFFFF',
    borderRadius: 999,
    paddingHorizontal: 16,
    paddingVertical: 10,
    marginRight: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 4,
    elevation: 1,
  },
  chipActive: {
    backgroundColor: '#86B342', // Accent green
    borderRadius: 999,
    paddingHorizontal: 16,
    paddingVertical: 10,
    marginRight: 10,
    shadowColor: '#86B342',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 6,
    elevation: 3,
  },
  chipText: {
    color: '#4F6B5C',
    fontSize: 14,
    fontWeight: '600',
  },
  chipTextActive: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: 'bold',
  },
  overviewStrip: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  overviewCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    marginHorizontal: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.04,
    shadowRadius: 8,
    elevation: 2,
  },
  overviewLabel: {
    fontSize: 12,
    color: '#4F6B5C',
    fontWeight: '600',
  },
  overviewValue: {
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 6,
    color: '#1F4A32',
  },
  splitRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  weatherCard: {
    flex: 1,
    backgroundColor: '#1F4A32', // Dark forest green mode
    borderRadius: 20,
    padding: 20,
    marginRight: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.15,
    shadowRadius: 10,
    elevation: 4,
    justifyContent: 'space-between',
  },
  weatherTitle: {
    fontSize: 12,
    color: '#D1E8DA',
    fontWeight: 'bold',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  weatherContent: {
    marginTop: 10,
  },
  weatherTemp: {
    fontSize: 42,
    color: '#FFFFFF',
    fontWeight: 'bold',
    marginBottom: 4,
  },
  weatherSub: {
    color: '#E7B526', // Gold accent
    fontWeight: '600',
    fontSize: 14,
    marginBottom: 12,
  },
  weatherDetailsRow: {
    flexDirection: 'column',
    gap: 4,
  },
  weatherSmall: {
    color: '#D1E8DA',
    fontSize: 12,
    fontWeight: '500',
  },
  statusCard: {
    flex: 1.2,
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 16,
    marginLeft: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 3,
  },
  statusTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1F4A32',
    marginBottom: 12,
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  metricBox: {
    flex: 1,
    backgroundColor: '#F4F7F3', // Very light gray-green
    borderRadius: 12,
    padding: 10,
    marginHorizontal: 4,
    alignItems: 'center',
  },
  metricValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F4A32',
  },
  metricLabel: {
    fontSize: 11,
    color: '#4F6B5C',
    marginTop: 4,
    fontWeight: '600',
  },
  errorText: {
    fontSize: 16,
    color: '#D32F2F',
    fontWeight: 'bold',
  },
});

export default HomeScreen;