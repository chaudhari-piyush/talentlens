import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
};

// Check if Firebase is configured
if (!firebaseConfig.apiKey || firebaseConfig.apiKey === 'your_firebase_api_key') {
  console.warn('Firebase is not configured. Please update the .env file with your Firebase configuration.');
  console.warn('The app will not work properly without Firebase configuration.');
}

let app;
let auth;

try {
  app = initializeApp(firebaseConfig);
  auth = getAuth(app);
} catch (error) {
  console.error('Firebase initialization error:', error);
  // Create mock auth object to prevent app from crashing
  auth = {
    currentUser: null,
    signOut: () => Promise.resolve(),
    onAuthStateChanged: () => () => {}
  };
}

export { auth };
export default app;