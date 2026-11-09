"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { AuthResponse, demoLogin as apiDemoLogin, getMe, loginUser, logoutUser, registerUser, User } from "./api";

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  register: (name: string, email: string, pass: string) => Promise<void>;
  demoLogin: (personaId: string) => Promise<void>;
  logout: () => Promise<void>;
  switchUser: (user: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    try {
      const savedToken = localStorage.getItem("arthapilot_token");
      const savedUser = localStorage.getItem("arthapilot_user");
      if (savedToken && savedUser) {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
        // Verify token in background
        getMe(savedToken)
          .then((verified) => {
            setUser(verified);
            localStorage.setItem("arthapilot_user", JSON.stringify(verified));
          })
          .catch(() => {
            // Expired token
            localStorage.removeItem("arthapilot_token");
            localStorage.removeItem("arthapilot_user");
            setToken(null);
            setUser(null);
          });
      }
    } catch {
      // LocalStorage unavailable
    } finally {
      setLoading(false);
    }
  }, []);

  const handleAuthSuccess = (res: AuthResponse) => {
    setToken(res.token);
    setUser(res.user);
    try {
      localStorage.setItem("arthapilot_token", res.token);
      localStorage.setItem("arthapilot_user", JSON.stringify(res.user));
    } catch {
      // Ignore storage error
    }
  };

  const login = async (email: string, pass: string) => {
    const res = await loginUser(email, pass);
    handleAuthSuccess(res);
  };

  const register = async (name: string, email: string, pass: string) => {
    const res = await registerUser(name, email, pass);
    handleAuthSuccess(res);
  };

  const demoLogin = async (personaId: string) => {
    const res = await apiDemoLogin(personaId);
    handleAuthSuccess(res);
  };

  const logout = async () => {
    if (token) {
      await logoutUser(token);
    }
    setToken(null);
    setUser(null);
    try {
      localStorage.removeItem("arthapilot_token");
      localStorage.removeItem("arthapilot_user");
    } catch {
      // Ignore
    }
  };

  const switchUser = (newUser: User) => {
    setUser(newUser);
    try {
      localStorage.setItem("arthapilot_user", JSON.stringify(newUser));
    } catch {
      // Ignore
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        demoLogin,
        logout,
        switchUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
