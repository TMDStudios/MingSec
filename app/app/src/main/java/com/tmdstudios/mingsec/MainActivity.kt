package com.tmdstudios.mingsec

import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.tmdstudios.mingsec.ui.theme.MingSecTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        createNotificationChannel() // Create the notification channel

        setContent {
            MingSecTheme {
                // Surface container using the 'background' color from the theme
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    Greeting("Android")
                }
            }
        }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                "default_channel",
                "Default Channel",
                NotificationManager.IMPORTANCE_DEFAULT
            )
            val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }
    }
}

@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
    // State variable to hold the FCM token
    var token by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(Unit) {
        // Retrieve the FCM token
        FCMTokenManager.getFCMToken { retrievedToken ->
            token = retrievedToken // Update the state with the retrieved token
        }
    }

    // Display the UI based on whether the token has been retrieved
    if (token != null) {
        GreetingWithToken(name, token!!, modifier) // Use !! to assert that token is not null
    } else {
        // Display a loading message or similar while the token is being fetched
        Text(
            text = "Hello $name!\nFetching FCM Token...",
            modifier = modifier.padding(16.dp) // Add some padding for better readability
        )
    }
}

@Composable
fun GreetingWithToken(name: String, token: String, modifier: Modifier = Modifier) {
    Text(
        text = "Hello $name!\nFCM Token: $token",
        modifier = modifier.padding(16.dp) // Add some padding for better readability
    )
}
