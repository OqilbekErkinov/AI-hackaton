import { ref, onMounted, onBeforeUnmount, watch } from "vue";
import useAuth from "@/composables/useAuth";
import useApi from "@/composables/useApi";

const unreadCount = ref(0);
let pollTimer: any = null;

export default function useMessages() {
  const auth = useAuth();
  const api = useApi();

  async function loadUnreadCount() {
    if (!auth.token.value) return;
    try {
      const resp = await api.get("/messages/?unread=1");
      const data = resp.data.results ?? resp.data ?? [];
      unreadCount.value = data.length;
    } catch (e) {
      console.error("loadUnreadCount error", e);
    }
  }

  function startPolling() {
    if (pollTimer) return;
    loadUnreadCount();
    pollTimer = setInterval(loadUnreadCount, 15000); // Poll every 15s
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
  }

  return {
    unreadCount,
    loadUnreadCount,
    startPolling,
    stopPolling,
  };
}
