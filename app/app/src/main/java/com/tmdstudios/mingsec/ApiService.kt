package com.tmdstudios.mingsec

import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Header

interface ApiService {

    // GET request to fetch a list of alarms (using AlarmReport class)
    @GET("ENDPOINT")
    suspend fun getAlarms(
        @Header("Authorization") apiKey: String // Authorization header
    ): Response<List<AlarmReport>> // A list of AlarmReport objects
}