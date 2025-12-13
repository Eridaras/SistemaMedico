'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { auth } from '@/lib/auth';
import { Loader2, Lock, Mail, ShieldCheck } from 'lucide-react';

export default function LoginPage() {
    const router = useRouter();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const result = await auth.login(email, password);
            if (result.success) {
                // Use hard redirect to ensure middleware picks up the new cookie
                window.location.href = '/dashboard';
            } else {
                setError(result.message || 'Credenciales inválidas');
                setLoading(false);
            }
        } catch (err) {
            console.error('Login error:', err);
            setError('Ocurrió un error inesperado');
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex">
            {/* Left Panel - Branding */}
            <div className="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-primary via-blue-600 to-indigo-700 overflow-hidden">
                {/* Decorative Elements */}
                <div className="absolute inset-0 opacity-20">
                    <div className="absolute top-0 left-0 w-72 h-72 bg-white/30 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2" />
                    <div className="absolute bottom-0 right-0 w-96 h-96 bg-white/20 rounded-full blur-3xl translate-x-1/3 translate-y-1/3" />
                    <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-white/10 rounded-full blur-2xl" />
                </div>

                {/* Content */}
                <div className="relative z-10 flex flex-col justify-center items-center w-full p-12 text-white">
                    <div className="flex items-center gap-3 mb-8">
                        <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
                            <ShieldCheck className="w-10 h-10" />
                        </div>
                    </div>
                    <h1 className="text-4xl font-black tracking-tight mb-4 text-center">
                        Clínica Bienestar
                    </h1>
                    <p className="text-lg text-white/80 text-center max-w-md leading-relaxed">
                        Sistema integral de gestión clínica. Administra pacientes, citas, inventario y facturación en un solo lugar.
                    </p>

                    {/* Features List */}
                    <div className="mt-12 space-y-4">
                        {[
                            'Gestión de Historia Clínica',
                            'Agendamiento de Citas',
                            'Control de Inventario',
                            'Facturación Electrónica'
                        ].map((feature, i) => (
                            <div key={i} className="flex items-center gap-3 text-white/90">
                                <div className="w-2 h-2 rounded-full bg-white/60" />
                                <span className="text-sm font-medium">{feature}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Right Panel - Login Form */}
            <div className="flex-1 flex flex-col justify-center items-center p-8 bg-background">
                <div className="w-full max-w-md space-y-8">
                    {/* Mobile Logo */}
                    <div className="flex lg:hidden items-center justify-center gap-3 mb-8">
                        <div className="p-3 bg-primary/10 rounded-xl">
                            <ShieldCheck className="w-8 h-8 text-primary" />
                        </div>
                        <h1 className="text-2xl font-bold text-foreground">Clínica Bienestar</h1>
                    </div>

                    {/* Form Header */}
                    <div className="text-center lg:text-left">
                        <h2 className="text-3xl font-bold tracking-tight text-foreground">
                            Bienvenido
                        </h2>
                        <p className="mt-2 text-muted-foreground">
                            Ingresa tus credenciales para acceder al sistema
                        </p>
                    </div>

                    {/* Login Form */}
                    <form onSubmit={handleLogin} className="space-y-6">
                        <div className="space-y-2">
                            <Label htmlFor="email" className="text-sm font-medium">
                                Correo Electrónico
                            </Label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="admin@clinica.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    className="pl-10 h-12 bg-muted/30 border-muted-foreground/20 focus:border-primary"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <div className="flex items-center justify-between">
                                <Label htmlFor="password" className="text-sm font-medium">
                                    Contraseña
                                </Label>
                                <a href="#" className="text-xs text-primary hover:underline">
                                    ¿Olvidaste tu contraseña?
                                </a>
                            </div>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    id="password"
                                    type="password"
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                    className="pl-10 h-12 bg-muted/30 border-muted-foreground/20 focus:border-primary"
                                />
                            </div>
                        </div>

                        {error && (
                            <div className="flex items-center gap-2 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                                <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                                <p className="text-sm text-red-600 dark:text-red-400 font-medium">
                                    {error}
                                </p>
                            </div>
                        )}

                        <Button
                            className="w-full h-12 text-base font-semibold shadow-lg shadow-primary/30 hover:shadow-primary/40 transition-all duration-300"
                            type="submit"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                                    Iniciando sesión...
                                </>
                            ) : (
                                'Iniciar Sesión'
                            )}
                        </Button>
                    </form>

                    {/* Footer */}
                    <div className="pt-6 text-center">
                        <p className="text-xs text-muted-foreground">
                            Al iniciar sesión, aceptas nuestros{' '}
                            <a href="#" className="text-primary hover:underline">Términos de Servicio</a>
                            {' '}y{' '}
                            <a href="#" className="text-primary hover:underline">Política de Privacidad</a>
                        </p>
                    </div>

                    <div className="pt-4 border-t border-border">
                        <p className="text-xs text-muted-foreground text-center">
                            Sistema de Gestión Clínica v1.0 • © 2024 Clínica Bienestar
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
