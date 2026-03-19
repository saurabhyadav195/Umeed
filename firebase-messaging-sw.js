importScripts("https://www.gstatic.com/firebasejs/9.6.1/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/9.6.1/firebase-messaging-compat.js");

firebase.initializeApp({
  apiKey: "AIzaSyDCXxsEE72vdnhr1ek6MVFZwFXDi2CQiHY",
  authDomain: "umeed-f2657.firebaseapp.com",
  projectId: "umeed-f2657",
  storageBucket: "umeed-f2657.firebasestorage.app",
  messagingSenderId: "90024521377",
  appId: "1:90024521377:web:b80c6454516a038c2a4ae0",
  measurementId: "G-4TZ9R70JWK"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {

  self.registration.showNotification(
    payload.notification.title,
    {
      body: payload.notification.body
    }
  );

});