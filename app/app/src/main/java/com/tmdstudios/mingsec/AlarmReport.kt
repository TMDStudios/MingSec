package com.tmdstudios.mingsec

import com.google.gson.annotations.SerializedName

data class AlarmReport(
    @SerializedName("camera") val camera: String,
    @SerializedName("time") val time: String?
)
