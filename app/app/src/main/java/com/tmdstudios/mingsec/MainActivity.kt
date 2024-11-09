package com.tmdstudios.mingsec

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.tmdstudios.mingsec.ui.theme.MingSecTheme
import kotlinx.coroutines.launch
import retrofit2.Response

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MingSecTheme {
                // Main Screen UI
                MainScreen()
            }
        }
    }
}

@Composable
fun MainScreen() {
    // State to hold the list of alarm reports
    var alarmReports by remember { mutableStateOf<List<AlarmReport>>(emptyList()) }
    var isLoading by remember { mutableStateOf(true) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    // The API key to be used for authorization
    val apiKey = "API_KEY"  // Replace with your actual API key

    // Launch a coroutine for network request
    val scope = rememberCoroutineScope()

    // Fetch data from API using LaunchedEffect
    LaunchedEffect(Unit) {
        scope.launch {
            try {
                // Call the suspend function to fetch alarm reports from the API
                val response: Response<List<AlarmReport>> = RetrofitClient.apiService.getAlarms("Bearer $apiKey")

                // Check if the response is successful
                if (response.isSuccessful) {
                    alarmReports = response.body() ?: emptyList()
                    isLoading = false
                } else {
                    errorMessage = "Error: ${response.message()}"
                    isLoading = false
                }
            } catch (e: Exception) {
                // Log the exception to identify the issue
                errorMessage = "Exception: ${e.localizedMessage}"
                isLoading = false
            }
        }
    }

    // Surface to display the UI
    Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
        Column(modifier = Modifier.padding(16.dp)) {
            Header()

            // Display loading or error message
            if (isLoading) {
                Text(text = "Loading alarm reports...", modifier = Modifier.padding(16.dp))
            } else if (errorMessage != null) {
                // Show the error message
                Text(text = "Error: $errorMessage", modifier = Modifier.padding(16.dp))
            } else {
                // Display the alarm reports list
                LazyColumn(modifier = Modifier.fillMaxSize()) {
                    items(alarmReports) { report ->
                        AlarmCard(alarmReport = report)
                    }
                }
            }
        }
    }
}

@Composable
fun Header() {
    var token by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(Unit) {
        // Retrieve the FCM token
        FCMTokenManager.getFCMToken { retrievedToken ->
            token = retrievedToken // Update the state with the retrieved token
        }
    }

    token?.let { Log.d("FCM_TOKEN", it) }

    Text(
        text = "Reported Alarms",
        style = MaterialTheme.typography.headlineMedium,
        modifier = Modifier.padding(16.dp)
    )
}

@Composable
fun AlarmCard(alarmReport: AlarmReport) {
    Column(modifier = Modifier.padding(8.dp)) {
        Text(text = "Camera: ${alarmReport.camera}", style = MaterialTheme.typography.bodyMedium)
        Text(text = "Time: ${alarmReport.time}", style = MaterialTheme.typography.bodyLarge)
    }
}
