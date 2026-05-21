import { reactive, readonly } from "vue";
import useAuth from "@/composables/useAuth";
import useApi from "@/composables/useApi";

const state = reactive({
  loaded: false,
  loading: false,
  profile: {
    user_id: null as string | null,
    fullname: "",
    phone: "",
    email: "",
    avatar: "",
    university_short: "",
    university_full: "",
    faculty_id: null as number | null,
    faculty_name: "",
    major_id: null as number | null,
    major_name: "",
    course: null as number | null,
    group: "",
    xp: 0,
  },
});

export default function useUserProfile() {
  const auth = useAuth();
  const api = useApi();
  const config = useRuntimeConfig();
  const API_BASE_URL = config.public.apiUrl.replace(/\/api$/, "");

  async function loadProfile(force = false) {
    const uid = auth.user?.value?.id;
    if (!uid) return;

    if (state.loaded && !force) return;

    state.loading = true;
    try {
      const res = await api.get("/profiles/me/");
      const p = res.data;

      state.profile.user_id = uid;
      state.profile.fullname = p.full_name || "";
      state.profile.phone = p.phone || "";
      state.profile.email = p.email || "";
      state.profile.university_short = p.university_short || "";
      state.profile.university_full = p.university_full || "";
      state.profile.faculty_id = p.faculty || null;
      state.profile.faculty_name = p.faculty_name || "";
      state.profile.major_id = p.major || null;
      state.profile.major_name = p.major_name || "";
      state.profile.course = p.course || null;
      state.profile.group = p.group || "";
      state.profile.xp = p.xp || 0;
      
      let av = p.avatar_url || p.avatar || "";
      if (av && !av.startsWith("http")) {
        av = API_BASE_URL + av;
      }
      state.profile.avatar = av;

      state.loaded = true;
    } catch (e) {
      console.error("loadProfile error", e);
    } finally {
      state.loading = false;
    }
  }

  async function updateProfile(payload: {
    fullname?: string;
    phone?: string;
    email?: string;
    avatarFile?: File | null;
    removeAvatar?: boolean;
    university_short?: string;
    university_full?: string;
    faculty?: number | null;
    major?: number | null;
    course?: number | null;
    group?: string;
  }) {
    const uid = auth.user?.value?.id;
    if (!uid) return;

    let res;

    // Use FormData for all updates to handle potential file
    const fd = new FormData();
    if (payload.fullname !== undefined) fd.append("full_name", payload.fullname);
    if (payload.phone !== undefined) fd.append("phone", payload.phone);
    if (payload.email !== undefined) fd.append("email", payload.email);
    if (payload.university_short !== undefined) fd.append("university_short", payload.university_short);
    if (payload.university_full !== undefined) fd.append("university_full", payload.university_full);
    if (payload.faculty !== undefined) fd.append("faculty", payload.faculty ? String(payload.faculty) : "");
    if (payload.major !== undefined) fd.append("major", payload.major ? String(payload.major) : "");
    if (payload.course !== undefined) fd.append("course", payload.course ? String(payload.course) : "");
    if (payload.group !== undefined) fd.append("group", payload.group || "");
    
    if (payload.avatarFile) {
      fd.append("avatar", payload.avatarFile);
    } else if (payload.removeAvatar) {
      fd.append("remove_avatar", "true");
    }

    res = await api.patch("/profiles/update_me/", fd);

    const p = res.data;

    // Manual refresh of the state based on response
    state.profile.fullname = p.full_name || state.profile.fullname;
    state.profile.phone = p.phone || state.profile.phone;
    state.profile.email = p.email || state.profile.email;
    state.profile.university_short = p.university_short || state.profile.university_short;
    state.profile.university_full = p.university_full || state.profile.university_full;
    state.profile.faculty_id = p.faculty || state.profile.faculty_id;
    state.profile.faculty_name = p.faculty_name || state.profile.faculty_name;
    state.profile.major_id = p.major || state.profile.major_id;
    state.profile.major_name = p.major_name || state.profile.major_name;
    state.profile.course = p.course || state.profile.course;
    state.profile.group = p.group || state.profile.group;
    
    let av = p.avatar_url || p.avatar || "";
    if (av && !av.startsWith("http")) {
      av = API_BASE_URL + av;
    }
    state.profile.avatar = av;

    return p;
  }

  function clearProfile() {
    state.loaded = false;
    state.profile.user_id = null;
    state.profile.fullname = "";
    state.profile.phone = "";
    state.profile.email = "";
    state.profile.avatar = "";
  }

  return {
    profile: readonly(state.profile),
    loading: readonly(state.loading),
    loadProfile,
    updateProfile,
    clearProfile,
  };
}
