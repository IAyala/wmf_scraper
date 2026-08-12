import axios from "axios";

/**
 * The API is served from the same origin as this app, under /api. In
 * development Vite proxies /api to the backend, so this holds there too and
 * the session cookie is always a first-party cookie.
 */
export const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

export interface User {
  username: string;
  role: "admin" | "superadmin";
}

/** Called when the server rejects the session, so the UI can return to login. */
let onUnauthenticated: (() => void) | null = null;

export const setUnauthenticatedHandler = (handler: (() => void) | null) => {
  onUnauthenticated = handler;
};

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // A 401 from /auth/* is the caller's business (a failed login, or the
    // session check on startup). Anywhere else it means the session expired.
    const url = error.config?.url ?? "";
    if (error.response?.status === 401 && !url.startsWith("/auth/")) {
      onUnauthenticated?.();
    }
    return Promise.reject(error);
  }
);

export const login = async (username: string, password: string): Promise<User> => {
  const { data } = await api.post<User>("/auth/login", { username, password });
  return data;
};

export const logout = async (): Promise<void> => {
  await api.post("/auth/logout");
};

/** The version the server is running. Public, so it works on the login screen. */
export const fetchVersion = async (): Promise<string> => {
  const { data } = await api.get<{ code_version: string }>("/version");
  return data.code_version;
};

/** Resolves to the logged-in user, or null when there is no valid session. */
export const fetchCurrentUser = async (): Promise<User | null> => {
  try {
    const { data } = await api.get<User>("/auth/me");
    return data;
  } catch {
    return null;
  }
};
