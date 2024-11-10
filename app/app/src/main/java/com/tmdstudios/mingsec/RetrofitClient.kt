package com.tmdstudios.mingsec

import io.github.cdimascio.dotenv.dotenv
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object RetrofitClient {
    private  val dotenv = dotenv {
        directory = "/assets"
        filename = "env" // instead of '.env', use 'env'
    }
    private val BASE_URL = dotenv["BASE_URL"] ?: "http://localhost:8000/"
    private val API_KEY = dotenv["API_KEY"] ?: throw IllegalArgumentException("API_KEY not found in .env")

    // Set up an OkHttpClient with the interceptor
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(ApiKeyInterceptor(API_KEY)) // Add the ApiKeyInterceptor to automatically inject the API key
        .connectTimeout(30, TimeUnit.SECONDS) // Optional: Set timeout for network requests
        .readTimeout(30, TimeUnit.SECONDS) // Optional: Set timeout for reading responses
        .build()

    // Retrofit instance with the OkHttpClient and API base URL
    val apiService: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient) // Pass the OkHttpClient with the interceptor
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}