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

  // Request interceptor: Inject token dynamically on each request
  api.interceptors.request.use((config) => {
    const currentToken = auth.token.value;
    if (currentToken) {
      config.headers.Authorization = `Bearer ${currentToken}`;
    }
    return config;
  }, (error) => {
    return Promise.reject(error);
  });

  return api;
}

export default useApi;
