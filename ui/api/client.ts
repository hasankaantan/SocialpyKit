import axios, { type AxiosInstance } from "axios"

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"

const TOKEN_KEY = "socialpykit_token"

export const http: AxiosInstance = axios.create({
  baseURL,
  timeout: 10_000,
  headers: { "Content-Type": "application/json" },
})

// Auto-attach the bearer token from localStorage to every request so
// service code does not have to thread the token through manually.
// Stores still own the lifecycle (login persists, logout clears).
http.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token !== null) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
