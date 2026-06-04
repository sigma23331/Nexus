import { useUserStore } from '@/stores/user'
import { updateUserLocation } from '@/api/user'

const LOCATION_AUTO_REQUEST_KEY = 'privacy_location_auto_request_at'
const LOCATION_AUTO_INTERVAL_MS = 3 * 24 * 60 * 60 * 1000

function isLocationAutoEnabled(): boolean {
  return localStorage.getItem('privacy_location') === 'true'
}

function shouldRequestLocation(): boolean {
  const stored = localStorage.getItem(LOCATION_AUTO_REQUEST_KEY)
  if (!stored) return true
  const last = Number(stored)
  if (Number.isNaN(last)) return true
  return Date.now() - last >= LOCATION_AUTO_INTERVAL_MS
}

function markLocationRequested(): void {
  localStorage.setItem(LOCATION_AUTO_REQUEST_KEY, Date.now().toString())
}

function isSecureContext(): boolean {
  return window.isSecureContext || location.hostname === 'localhost'
}

function getCurrentPosition(): Promise<GeolocationPosition | null> {
  if (!('geolocation' in navigator)) return Promise.resolve(null)
  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      (position) => resolve(position),
      () => resolve(null),
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      },
    )
  })
}

export async function autoRequestUserLocation(): Promise<void> {
  if (!isLocationAutoEnabled()) return
  if (!isSecureContext()) return
  if (!shouldRequestLocation()) return

  const userStore = useUserStore()
  if (!userStore.isLoggedIn) return

  markLocationRequested()

  const position = await getCurrentPosition()
  if (!position) return

  try {
    await updateUserLocation({
      latitude: position.coords.latitude,
      longitude: position.coords.longitude,
      locationAccuracy: position.coords.accuracy,
    })
    await userStore.fetchUserInfo()
  } catch {
    // 自动更新失败时不阻断应用，下一次仍可重新触发
  }
}
