import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// These are placeholder values. Please replace them with your actual Firebase project configuration.
const firebaseConfig = {
    apiKey: "PLACEHOLDER",
    authDomain: "PLACEHOLDER.firebaseapp.com",
    projectId: "PLACEHOLDER",
    storageBucket: "PLACEHOLDER.appspot.com",
    messagingSenderId: "PLACEHOLDER",
    appId: "PLACEHOLDER"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
