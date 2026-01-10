'use client';
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Calendar,
  Receipt,
  LayoutDashboard,
  FileText,
  Menu,
  Package,
  Search,
  Settings,
  HelpCircle,
  LogOut,
  ClipboardList,
  Sparkles
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Sheet,
  SheetContent,
  SheetTrigger,
} from '@/components/ui/sheet';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { auth } from '@/lib/auth';
import { NotificationsPanel } from '@/components/notifications-panel';
import { AuthProvider } from '@/components/auth-provider';

const navItems = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/patients', icon: ClipboardList, label: 'Historia Clínica' },
  { href: '/appointments', icon: Calendar, label: 'Agendamiento' },
  { href: '/treatments', icon: Sparkles, label: 'Tratamientos' },
  { href: '/inventory', icon: Package, label: 'Inventario' },
  { href: '/billing', icon: Receipt, label: 'Facturación' },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [user, setUser] = React.useState<any>(null);

  React.useEffect(() => {
    setUser(auth.getUser());
  }, []);

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Brand Header */}
      <div className="flex h-16 shrink-0 items-center gap-2 border-b px-6">
        <div className="h-6 w-6 text-primary">
          <svg fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 12h3v8h6v-6h2v6h6v-8h3L12 2z" />
          </svg>
        </div>
        <span className="text-lg font-bold tracking-tight">Clínica Bienestar</span>
      </div>

      <div className="flex flex-col flex-1 justify-between p-4">
        <div className="flex flex-col gap-6">
          {/* User Profile in Sidebar (Desktop) */}
          <div className="flex items-center gap-3 px-2">
            <Avatar className="h-10 w-10 border border-border">
              <AvatarImage src="https://lh3.googleusercontent.com/aida-public/AB6AXuDXQC5a7tykWxIi6RHgQaM0SCVTR1MQLJoRC-AsVYhDaz4YZUfhLJsDTvUzW-M3kDUpJKqKP5TOfMqcYiBURVagtvkMMkfJlHs0JWNZ1exAyiCyZBALOWEs9DqvksJI-3GlVcmVls5INbDSiNzAFwEvuqixVIuq2jYGb48inwNOvlfgcmszcdBDb7ab__TQbGd52UvqmFJG3CgsCBvr1R7hU6GZyYAFBgJ0tIFQCEYN8ZNfIhilVG3ta5hPfiffOthJtLl7YYv8TPtg" alt="Dr. Elena" />
              <AvatarFallback>EV</AvatarFallback>
            </Avatar>
            <div className="flex flex-col overflow-hidden">
              <span className="text-sm font-medium truncate">{user?.full_name || 'Cargando...'}</span>
              <span className="text-xs text-muted-foreground truncate">{user?.role_name || '...'}</span>
            </div>
          </div>

          {/* Navigation */}
          <nav className="grid gap-1">
            {navItems.map(({ href, icon: Icon, label }) => {
              const isActive = pathname.startsWith(href);
              return (
                <Link
                  key={href}
                  href={href}
                  className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${isActive
                    ? 'bg-primary/10 text-primary'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                    }`}
                >
                  <Icon className={`h-4 w-4 ${isActive ? 'text-primary' : ''}`} />
                  {label}
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="flex flex-col gap-4">
          <Button className="w-full bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm" size="sm">
            Nueva Cita
          </Button>
          <nav className="grid gap-1">
            <Link href="/settings" className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground">
              <Settings className="h-4 w-4" />
              Configuración
            </Link>
            <Link href="/help" className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground">
              <HelpCircle className="h-4 w-4" />
              Ayuda
            </Link>
            <button
              onClick={() => auth.logout()}
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-destructive hover:bg-destructive/10 hover:text-destructive w-full"
            >
              <LogOut className="h-4 w-4" />
              Cerrar Sesión
            </button>
          </nav>
        </div>
      </div>
    </div>
  );

  return (
    <AuthProvider>
      <div className="grid min-h-screen w-full md:grid-cols-[240px_1fr] lg:grid-cols-[280px_1fr]">
        <div className="hidden border-r bg-card md:block">
          <SidebarContent />
        </div>
        <div className="flex flex-col h-screen overflow-hidden">
          <header className="flex h-16 shrink-0 items-center justify-between gap-4 border-b bg-background px-4 lg:px-6">
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="md:hidden shrink-0">
                  <Menu className="h-5 w-5" />
                  <span className="sr-only">Toggle navigation menu</span>
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="p-0 w-[280px]">
                <SidebarContent />
              </SheetContent>
            </Sheet>

            {/* Search Bar */}
            <div className="w-full flex-1 md:w-auto md:flex-none">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder="Buscar pacientes, citas..."
                  className="w-full rounded-lg bg-background pl-9 md:w-[320px] lg:w-[440px]"
                />
              </div>
            </div>

            <div className="flex items-center gap-4">
              <NotificationsPanel />
              <Avatar className="h-9 w-9 border border-border md:hidden">
                <AvatarImage src="https://lh3.googleusercontent.com/aida-public/AB6AXuDXQC5a7tykWxIi6RHgQaM0SCVTR1MQLJoRC-AsVYhDaz4YZUfhLJsDTvUzW-M3kDUpJKqKP5TOfMqcYiBURVagtvkMMkfJlHs0JWNZ1exAyiCyZBALOWEs9DqvksJI-3GlVcmVls5INbDSiNzAFwEvuqixVIuq2jYGb48inwNOvlfgcmszcdBDb7ab__TQbGd52UvqmFJG3CgsCBvr1R7hU6GZyYAFBgJ0tIFQCEYN8ZNfIhilVG3ta5hPfiffOthJtLl7YYv8TPtg" alt="Dr. Elena" />
                <AvatarFallback>EV</AvatarFallback>
              </Avatar>
            </div>
          </header>
          <main className="flex-1 overflow-y-auto bg-background p-4 lg:p-8">
            {children}
          </main>
        </div>
      </div>
    </AuthProvider>
  );
}
