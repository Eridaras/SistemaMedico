"use client"

import React, { createContext, useContext, useEffect, useState } from 'react'
import { auth as authLib } from '@/lib/auth'

interface User {
  user_id: number
  email: string
  firstName: string
  lastName: string
  role: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<{ success: boolean; message?: string }>
  logout: () => void
  getToken: () => string | null
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const storedUser = authLib.getUser()
    const token = authLib.getToken()

    if (storedUser && token) {
      setUser(storedUser)
    }

    setIsLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    const result = await authLib.login(email, password)
    if (result.success && result.user) {
      setUser(result.user)
    }
    return result
  }

  const logout = () => {
    setUser(null)
    authLib.logout()
  }

  const getToken = () => {
    return authLib.getToken()
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        getToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
