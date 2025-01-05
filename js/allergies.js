import { initializeApp } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-app.js";
import { getAuth, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-auth.js";
import { getDatabase, ref, update } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-database.js";

// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyANhyD1eztaP_jnKwryZMzQ078Yt1wdaa8",
    authDomain: "allergimate-11086.firebaseapp.com",
    projectId: "allergimate-11086",
    storageBucket: "allergimate-11086.firebasestorage.app",
    messagingSenderId: "106919192013",
    appId: "1:106919192013:web:a9a21590be3bab02fdd084",
    measurementId: "G-MB9R5RTV5X"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth();
const database = getDatabase(app);

// DOM Elements
const finishButton = document.getElementById("finish-button");
const allergiesDataInput = document.getElementById("allergies-data");

// Event Listener for Finish Button
finishButton.addEventListener("click", async () => {
    const allergies = allergiesDataInput.value; // Fetch allergies data from hidden input

    if (!allergies) {
        alert("Please enter your allergies data.");
        return;
    }

    onAuthStateChanged(auth, async (user) => {
        if (user) {
            try {
                // Update allergies in Realtime Database
                const userRef = ref(database, `users/${user.uid}`);
                await update(userRef, { allergies: JSON.parse(allergies) });

                alert("Your allergies data has been saved.");
                auth.signOut(); // Log out the user
                window.location.href = "login.html"; // Redirect to login.html
            } catch (error) {
                console.error("Error saving allergies data:", error);
                alert("Failed to save allergies data. Please try again.");
            }
        } else {
            alert("No user is logged in. Redirecting to login.");
            window.location.href = "login.html";
        }
    });
});
