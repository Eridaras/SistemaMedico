interface LoginResponse {
    success: boolean;
    access_token?: string;
    message?: string;
    user?: any;
}

export const auth = {
    async login(email: string, password: string): Promise<LoginResponse> {
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            // Backend returns { success, data: { token, user }, message }
            if (response.ok && data.data?.token) {
                if (typeof window !== 'undefined') {
                    localStorage.setItem('token', data.data.token);
                    localStorage.setItem('user', JSON.stringify(data.data.user)); // Store user
                    // Set cookie for middleware (1 day expiry)
                    document.cookie = `token=${data.data.token}; path=/; max-age=86400; SameSite=Strict`;
                }
                return { success: true, access_token: data.data.token, user: data.data.user };
            }

            return {
                success: false,
                message: data.message || 'Credenciales inválidas'
            };
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, message: 'Error de conexión con el servidor' };
        }
    },

    logout() {
        if (typeof window !== 'undefined') {
            localStorage.removeItem('token');
            localStorage.removeItem('user'); // Remove user
            document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT';
            window.location.href = '/login';
        }
    },

    getToken(): string | null {
        if (typeof window !== 'undefined') {
            return localStorage.getItem('token');
        }
        return null;
    },

    getUser(): any | null {
        if (typeof window !== 'undefined') {
            const userStr = localStorage.getItem('user');
            if (userStr) {
                try {
                    return JSON.parse(userStr);
                } catch (e) {
                    return null;
                }
            }
        }
        return null;
    },

    isAuthenticated(): boolean {
        return !!this.getToken();
    }
};
