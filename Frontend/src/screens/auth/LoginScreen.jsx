import React, { useState } from 'react'
import {
	View,
	Text,
	StyleSheet,
	TextInput,
	TouchableOpacity,
	KeyboardAvoidingView,
	Platform,
	Alert,
} from 'react-native'
import { CREDENTIALS } from '../../utils'

export default function LoginScreen({ navigation }) {
	const [email, setEmail] = useState('')
	const [password, setPassword] = useState('')

	const handleLogin = () => {
		if (email === CREDENTIALS.email && password === CREDENTIALS.password) {
			navigation.replace('Dashboard', { email })
		} else {
			Alert.alert('Login failed', 'Invalid email or password')
		}
	}

	return (
		<KeyboardAvoidingView
			style={styles.container}
			behavior={Platform.OS === 'ios' ? 'padding' : undefined}
		>
			<View style={styles.header}>
				<View style={styles.headerContent}>
					<Text style={styles.appTitle}>Crop Health Monitor</Text>
					<Text style={styles.appSubtitle}>Login to your farm dashboard</Text>
				</View>
			</View>

			<View style={styles.card}>
				<Text style={styles.label}>Email</Text>
				<TextInput
					value={email}
					onChangeText={setEmail}
					placeholder="you@example.com"
					style={styles.input}
					keyboardType="email-address"
					autoCapitalize="none"
				/>

				<Text style={[styles.label, { marginTop: 12 }]}>Password</Text>
				<TextInput
					value={password}
					onChangeText={setPassword}
					placeholder="••••••••"
					style={styles.input}
					secureTextEntry
				/>

				<TouchableOpacity style={styles.button} onPress={handleLogin}>
					<Text style={styles.buttonText}>Log In</Text>
				</TouchableOpacity>

				<View style={styles.rowRight}>
					<Text style={styles.smallText}>Don't have an account?</Text>
					<TouchableOpacity onPress={() => navigation.navigate('Signup')}>
						<Text style={styles.link}> Sign up</Text>
					</TouchableOpacity>
				</View>
			</View>

			<View style={styles.footer}>
				<Text style={styles.footerText}>Helping farmers detect crop issues early.</Text>
			</View>
		</KeyboardAvoidingView>
	)
}

const styles = StyleSheet.create({
	container: { flex: 1, backgroundColor: '#f3f7f2' },
	header: {
		backgroundColor: '#2e7d32',
		paddingVertical: 28,
		paddingHorizontal: 20,
		borderBottomLeftRadius: 24,
		borderBottomRightRadius: 24,
	},
	headerContent: { alignItems: 'flex-start' },
	appTitle: { color: '#fff', fontSize: 22, fontWeight: '700' },
	appSubtitle: { color: '#e8f5e9', marginTop: 6 },
	card: {
		margin: 20,
		marginTop: 24,
		backgroundColor: '#fff',
		borderRadius: 12,
		padding: 16,
		shadowColor: '#000',
		shadowOpacity: 0.06,
		shadowRadius: 10,
		elevation: 4,
	},
	label: { color: '#2f3a2f', fontWeight: '600', marginBottom: 6 },
	input: {
		height: 46,
		borderColor: '#e6efe6',
		borderWidth: 1,
		borderRadius: 8,
		paddingHorizontal: 12,
		backgroundColor: '#fff',
	},
	button: {
		marginTop: 18,
		backgroundColor: '#388e3c',
		paddingVertical: 12,
		borderRadius: 8,
		alignItems: 'center',
	},
	buttonText: { color: '#fff', fontWeight: '700' },
	footer: { alignItems: 'center', padding: 12 },
	footerText: { color: '#6b6f62' },
})
