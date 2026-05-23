package com.adex.app.util

import android.content.Context
import android.content.Intent
import androidx.core.content.ContextCompat
import androidx.work.CoroutineWorker
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.WorkerParameters
import com.adex.app.service.ADexForegroundService
import com.adex.app.service.ServiceActions
import java.util.concurrent.TimeUnit

class PersistenceWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {
    override suspend fun doWork(): Result {
        if (!ADexForegroundService.isServiceRunning) {
            val intent = Intent(applicationContext, ADexForegroundService::class.java).apply {
                action = ServiceActions.ACTION_START
            }
            runCatching {
                ContextCompat.startForegroundService(applicationContext, intent)
            }
            // If still not running, schedule immediate retry
            if (!ADexForegroundService.isServiceRunning) {
                scheduleRecovery(applicationContext)
            }
        }
        return Result.success()
    }

    companion object {
        private const val WORK_NAME = "adex_persistence_work"
        private const val RECOVERY_WORK_NAME = "adex_recovery_work"

        fun schedule(context: Context) {
            val request = PeriodicWorkRequestBuilder<PersistenceWorker>(15, TimeUnit.MINUTES)
                .setInitialDelay(5, TimeUnit.MINUTES)
                .build()

            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                WORK_NAME,
                ExistingPeriodicWorkPolicy.KEEP,
                request
            )
        }

        private fun scheduleRecovery(context: Context) {
            val recoveryRequest = androidx.work.OneTimeWorkRequestBuilder<PersistenceWorker>()
                .setInitialDelay(30, TimeUnit.SECONDS)
                .build()

            WorkManager.getInstance(context).enqueueUniqueWork(
                RECOVERY_WORK_NAME,
                androidx.work.ExistingWorkPolicy.REPLACE,
                recoveryRequest
            )
        }
    }
}
