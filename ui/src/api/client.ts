import axios, { type AxiosInstance } from "axios"

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"

export const http: AxiosInstance = axios.create({
  baseURL,
  timeout: 10_000,
  headers: { "Content-Type": "application/json" },
})
