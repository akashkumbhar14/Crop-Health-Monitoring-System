export const CREDENTIALS = { email: 'admin@gmail.com', password: 'admin@123' }

export function fakePredict() {
  const diseases = [
    { name: 'Powdery Mildew', treatment: 'Apply sulfur-based fungicide and remove infected leaves.' },
    { name: 'Late Blight', treatment: 'Remove infected plants and use copper fungicide.' },
    { name: 'Leaf Spot', treatment: 'Use appropriate bactericide and improve air circulation.' },
    { name: 'Healthy', treatment: 'No action needed. Monitor the crop.' },
  ]
  const pick = diseases[Math.floor(Math.random() * diseases.length)]
  const confidence = (60 + Math.random() * 40).toFixed(1) // 60-100%
  return { disease: pick.name, confidence, treatment: pick.treatment }
}
