package com.tmdstudios.mingsec

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.tmdstudios.mingsec.ui.theme.MingSecTheme
import kotlinx.coroutines.launch
import retrofit2.Response

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            MingSecTheme(darkTheme = true) {
                MainScreen()
            }
        }
    }
}

@Composable
fun MainScreen() {
    val alarmReports = remember { mutableStateOf<List<AlarmReport>>(emptyList()) }
    val isLoading = remember { mutableStateOf(true) }
    val errorMessage = remember { mutableStateOf<String?>(null) }
    val showPopup = remember { mutableStateOf(false) }
    val fcmToken = remember { mutableStateOf<String?>(null) }

    // Coroutine scope to manage background tasks like network requests
    val scope = rememberCoroutineScope()

    // LaunchedEffect to run network request when the composable is first launched
    LaunchedEffect(Unit) {
        scope.launch {
            try {
                Log.d("MainScreen", "Making network request to fetch alarms")

                // Fetch alarm reports from the API
                val response: Response<List<AlarmReport>> = RetrofitClient.apiService.getAlarms()

                if (response.isSuccessful) {
                    val body = response.body()
                    if (body != null) {
                        alarmReports.value = body.reversed() // Set the data to alarmReports
                        Log.d("MainScreen", "Alarms fetched successfully: ${body.size} reports")
                    } else {
                        errorMessage.value = "No data available"
                        Log.e("MainScreen", "Response body was null")
                    }
                } else {
                    errorMessage.value = "Error: ${response.message()}"
                    Log.e("MainScreen", "Error fetching alarms: ${response.message()}")
                }
            } catch (e: Exception) {
                // Handle network or other exceptions
                errorMessage.value = "Exception: ${e.localizedMessage}"
                Log.e("MainScreen", "Exception occurred: ${e.localizedMessage}", e)
            } finally {
                // Set loading state to false after the network call completes
                isLoading.value = false
                Log.d("MainScreen", "Network call completed, isLoading = false")
            }
        }
    }

    // Main UI container
    Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
        Column(modifier = Modifier.padding(16.dp)) {
            Box(
                modifier = Modifier.fillMaxWidth()
            ) {
                Button(
                    onClick = {
                                FCMTokenManager.getFCMToken { token ->
                                    fcmToken.value = token
                                }
                                showPopup.value = true
                              },
                    modifier = Modifier
                        .align(Alignment.Center)
                        .padding(top = 16.dp, bottom = 16.dp)
                        .border(
                            BorderStroke(1.dp, MaterialTheme.colorScheme.onSurface),
                            shape = MaterialTheme.shapes.medium
                        ),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.background,
                        contentColor = MaterialTheme.colorScheme.onBackground
                    )
                ) {
                    Text(text = "Notification Device Token")
                }
            }
            Header()

            // Conditional UI rendering based on loading, error, or data state
            if (isLoading.value) {
                Text(text = "Loading alarm reports...", modifier = Modifier.padding(16.dp))
            } else if (errorMessage.value != null) {
                Text(text = "Error: ${errorMessage.value}", modifier = Modifier.padding(16.dp))
            } else {
                if (alarmReports.value.isEmpty()) {
                    Text(text = "No alarm reports available.", modifier = Modifier.padding(16.dp))
                } else {
                    LazyColumn(modifier = Modifier.fillMaxSize()) {
                        items(alarmReports.value) { report ->
                            AlarmCard(alarmReport = report) // Display each alarm report
                        }
                    }
                }
            }

            if (showPopup.value) {
                AlertDialog(
                    onDismissRequest = { showPopup.value = false }, // Close the dialog when clicked outside
                    title = { Text(text = "Notification Device Token") },
                    text = { Text(text = "${fcmToken.value}") },
                    confirmButton = {
                        Button(
                            onClick = { showPopup.value = false },
                            modifier = Modifier
                                .border(
                                    BorderStroke(1.dp, MaterialTheme.colorScheme.onSurface),
                                    shape = MaterialTheme.shapes.medium
                                ),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = MaterialTheme.colorScheme.background,
                                contentColor = MaterialTheme.colorScheme.onBackground
                            )) {
                            Text("OK")
                        }
                    }
                )
            }
        }
    }
}

@Composable
fun Header() {
    Box(
        modifier = Modifier.fillMaxWidth()
    ) {
        Text(
            text = "Reported Alarms",
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier
                .align(Alignment.Center)
                .padding(top = 16.dp, bottom = 16.dp)
        )
    }
}

@Composable
fun AlarmCard(alarmReport: AlarmReport) {
    // Display individual alarm details in a card-like format
    Column(modifier = Modifier.padding(8.dp)) {
        Text(text = "Camera: ${alarmReport.camera}", style = MaterialTheme.typography.bodyMedium)
        Text(text = "Time: ${alarmReport.time}", style = MaterialTheme.typography.bodyLarge)
    }
}
