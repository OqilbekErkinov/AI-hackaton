// /composables/useAuth.ts
import { readonly } from "vue";

/**
 * useAuth: Nuxt 3 compliant authentication composable.
 * Uses useState to share state across components and ensure SSR hydration.
 * Uses useCookie for persistent token management across server and client.
 */
export const useAuth = () => {
  const token = useCookie<string | null>("access", { 
    maxAge: 60 * 60 * 24 * 7, // 7 days
    path: '/',
    sameSite: 'lax'
  });
  
  // Shared state using useState (safe for SSR)
  const user = useState<any | null>("auth_user", () => null);
  const loading = useState<boolean>("auth_loading", () => false);
  const error = useState<any | null>("auth_error", () => null);
  const ready = useState<boolean>("auth_ready", () => false);
  
  // Get nuxt instance to store transient initialization promise
  const nuxtApp = useNuxtApp();

  /** init: verify token and fetch user data */
  const init = async () => {
    // If already initialized, stop
    if (ready.value && user.value) return;
    
    // Capture dependencies synchronously before entering async closure
    const api = useApi();
    const tokenValue = token.value;

    // Prevent double-initialization (race conditions)
    if ((nuxtApp as any)._authInitPromise) return (nuxtApp as any)._authInitPromise;

    (nuxtApp as any)._authInitPromise = (async () => {
      if (!tokenValue) {
        ready.value = true;
        return;
      }

      loading.value = true;
      error.value = null;
      try {
        const resp = await api.get("/auth/me/");
        
        if (resp.status === 200) {
          user.value = resp.data.user ?? resp.data;
        }
      } catch (e: any) {
        // Faqat token haqiqatdan ham xato bo'lgandagina (401/403) authni tozalaymiz
        // Boshqa xatolar (500, network error) bo'lsa, sessiya saqlanib qoladi
        if (e.response?.status === 401 || e.response?.status === 403) {
          clearAuth();
        }
        console.warn("useAuth.init error:", e.message);
      } finally {
        loading.value = false;
        ready.value = true;
        delete (nuxtApp as any)._authInitPromise;
      }
    })();

    return (nuxtApp as any)._authInitPromise;
  };

  /** login */
  const login = async ({ email, password }: any) => {
    loading.value = true;
    error.value = null;
    try {
      const api = useApi();
      const body = { email, password, username: email.split("@")[0] };
      const resp = await api.post("/auth/login/", body);

      if (resp.status === 200) {
        const data = resp.data;
        token.value = data.access || data.token || data.access_token;
        user.value = data.user ?? data;
        ready.value = true;
        return { data };
      }
      return { error: resp.data };
    } catch (e: any) {
      error.value = e.response?.data ?? e.message;
      throw e;
    } finally {
      loading.value = false;
    }
  };

  /** register */
  const register = async (payload: any) => {
    loading.value = true;
    error.value = null;
    try {
      const api = useApi();
      let resp;
      
      // Handle FormData if avatar is present, otherwise JSON
      if (payload instanceof FormData) {
        resp = await api.post("/auth/register/", payload);
      } else {
        resp = await api.post("/auth/register/", payload);
      }

      if (resp.status === 201 || resp.status === 200) {
        const data = resp.data;
        token.value = data.access || data.token || data.access_token;
        user.value = data.user ?? data;
        ready.value = true;
        return { data };
      }
      return { error: resp.data };
    } catch (e: any) {
      error.value = e.response?.data ?? e.message;
      throw e;
    } finally {
      loading.value = false;
    }
  };

  /** logout */
  const logout = () => {
    clearAuth();
  };

  /** internal helper to wipe auth state */
  const clearAuth = () => {
    token.value = null;
    user.value = null;
    ready.value = false;
  };

  return {
    user,
    token, // Reactive cookie-based token
    loading: readonly(loading),
    error: readonly(error),
    ready: readonly(ready),
    init,
    register,
    login,
    logout,
    clearAuth
  };
};

export default useAuth;
