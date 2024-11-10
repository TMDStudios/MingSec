package com.tmdstudios.mingsec

import retrofit2.Response
import retrofit2.http.GET

interface ApiService {
    @GET("api/alarms/get/")
    suspend fun getAlarms(): Response<List<AlarmReport>>
}