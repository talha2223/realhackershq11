import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyDE2ZhXNdvidq3pwL6AfPF_I7o4dEset6E",
  authDomain: "realhackershq.firebaseapp.com",
  projectId: "realhackershq",
  storageBucket: "realhackershq.firebasestorage.app",
  messagingSenderId: "866560106940",
  appId: "1:866560106940:web:4f260fada54b6f3fa7cbb9",
  measurementId: "G-05F8VH1N5Q"
};

const app = initializeApp(firebaseConfig);
const analytics = typeof window !== 'undefined' ? getAnalytics(app) : null;
const auth = getAuth(app);

export { app, analytics, auth };
