import {
  createContext,
  useContext,
  useState,
  useEffect,
  useRef,
  useCallback,
  type ReactNode,
} from "react";
import API from "../services/api";

interface User {
  id: number;
  name?: string;
  email: string;
  phone_number?: string;
  role: string;
  organization: {
    id: number;
    name: string;
    plan: string;
  };
  subscription: {
    plan_name: string;
    is_active: boolean;
    end_date: string | null;
    reports_used: number;
  };
}

interface AuthContextType {
  user: User | null;
  login: (phoneNumber: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const initialized = useRef(false);
  const loadingUser = useRef(false);

  const clearSession = useCallback(() => {
    localStorage.removeItem("access_token");
    setUser(null);
  }, []);

  const loadUser = useCallback(async () => {
    if (loadingUser.current) return;
    loadingUser.current = true;

    try {
      const response = await API.get("/users/me");
      setUser(response.data);
    } catch {
      clearSession();
    } finally {
      loadingUser.current = false;
    }
  }, [clearSession]);

  const initializeAuth = useCallback(async () => {
    if (initialized.current) return;
    initialized.current = true;

    const token = localStorage.getItem("access_token");

    if (!token) {
      setLoading(false);
      return;
    }

    await loadUser();
    setLoading(false);
  }, [loadUser]);

  const refreshUser = async () => {
    await loadUser();
  };

  const login = async (phoneNumber: string, password: string) => {
    const response = await API.post("/users/login", {
      phone_number: phoneNumber,
      password,
    });

    localStorage.setItem("access_token", response.data.access_token);
    await loadUser();
  };

  const logout = async () => {
    try {
      await API.post("/logout", undefined, {
        withCredentials: true,
      });
    } catch {
      // Frontend stays resilient even if server-side logout is not implemented yet.
    } finally {
      clearSession();
      window.location.href = "/login";
    }
  };

  useEffect(() => {
    void initializeAuth();
  }, [initializeAuth]);

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        refreshUser,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }

  return context;
};
