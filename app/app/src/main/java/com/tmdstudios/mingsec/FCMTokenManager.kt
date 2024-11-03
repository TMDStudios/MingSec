package com.tmdstudios.mingsec

import com.google.firebase.messaging.FirebaseMessaging

object FCMTokenManager {
    private var fcmToken: String? = null

    fun getFCMToken(onTokenReceived: (String?) -> Unit) {
        if (fcmToken != null) {
            // If the token is already retrieved, return it
            onTokenReceived(fcmToken)
        } else {
            // Fetch the token if not already available
            FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
                if (task.isSuccessful) {
                    fcmToken = task.result
                    onTokenReceived(fcmToken)
                } else {
                    onTokenReceived(null) // Handle the error
                }
            }
        }
    }
}
