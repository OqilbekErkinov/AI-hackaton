// /composables/useApi.ts
import axios from "axios";
import { useAuth } from "./useAuth";

export function useApi() {
  const config = useRuntimeConfig();
  const auth = useAuth();
  const token = auth.token.value;
  
  // Use NUXT_PUBLIC_API_URL if available, otherwise fallback to local dev URL
  const baseURL = config.public.apiUrl || "http://127.0.0.1:9000/api";
  
  const api = axios.create({
    baseURL,
    headers: {
      "Accept": "application/json",
    }
  });

  // Request interceptor: Inject captured token
  api.interceptors.request.use((config) => {
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  }, (error) => {
    return Promise.reject(error);
  });

  return api;
}

export default useApi;
