import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  demoLogin as apiDemoLogin,
  getCurrentUser,
  getStoredUser,
  guestLogin as apiGuestLogin,
  isAuthenticated,
  login as apiLogin,
  logout as apiLogout,
  refreshToken,
  signup as apiSignup,
} from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(getStoredUser);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function restoreSession() {
      if (!isAuthenticated()) {
        setLoading(false);
        return;
      }

      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch {
        apiLogout();
        setUser(null);
      } finally {
        setLoading(false);
      }
    }

    restoreSession();
  }, []);

  // Listen for auth-expired event dispatched by api interceptor
  useEffect(() => {
    function handleAuthExpired() {
      setUser(null);
    }

    window.addEventListener("datanova:auth-expired", handleAuthExpired);
    return () => {
      window.removeEventListener("datanova:auth-expired", handleAuthExpired);
    };
  }, []);

  // Periodically refresh token every 30 minutes while authenticated to maintain active sessions
  useEffect(() => {
    if (!user) return;

    const interval = setInterval(async () => {
      try {
        await refreshToken();
      } catch {
        // Handled by authFetch / logout
      }
    }, 30 * 60 * 1000);

    return () => clearInterval(interval);
  }, [user]);

  async function login(email, password) {
    const data = await apiLogin(email, password);
    setUser(data.user);
    return data;
  }

  async function signup(
    email,
    password,
    fullName
  ) {
    const data = await apiSignup(
      email,
      password,
      fullName
    );

    setUser(data.user);

    return data;
  }

  async function demoLogin() {
    const data = await apiDemoLogin();
    setUser(data.user);
    return data;
  }

  async function guestLogin() {
    const data = await apiGuestLogin();
    setUser(data.user);
    return data;
  }

  function logout() {
    apiLogout();
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: Boolean(user),
        isGuest: Boolean(user?.is_guest),
        login,
        signup,
        demoLogin,
        guestLogin,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return context;
}
