"use client";

import * as React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  BarChart,
  Bar,
  XAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import {
  ArrowUp,
  ArrowDown
} from "lucide-react";
import { PageTransition } from "@/components/page-transition";
import { auth } from "@/lib/auth";
import { TodayAppointmentsWidget } from "@/components/today-appointments-widget";
import { LowStockWidget } from "@/components/low-stock-widget";

// TypeScript Interfaces
interface DashboardStats {
  ventas_totales: number;
  pacientes_nuevos: number;
  citas_hoy: number;
  ingresos_mes: number;
}

interface FinancialData {
  name: string;
  ingresos: number;
  egresos: number;
}

export default function DashboardPage() {
  const [stats, setStats] = React.useState<DashboardStats | null>(null);
  const [financialData, setFinancialData] = React.useState<FinancialData[]>([]);

  // Fetch all dashboard data from backend
  React.useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [statsRes, financialRes] = await Promise.all([
          fetch('/api/facturacion/dashboard/stats', {
            headers: { 'Authorization': `Bearer ${auth.getToken()}` }
          }),
          fetch('/api/facturacion/dashboard/monthly', {
            headers: { 'Authorization': `Bearer ${auth.getToken()}` }
          })
        ]);

        if (statsRes.ok) {
          const data = await statsRes.json();
          if (data.success) setStats(data.data);
        }

        if (financialRes.ok) {
          const data = await financialRes.json();
          if (data.success) setFinancialData(data.data.monthly || []);
        }
      } catch (err) {
        console.error("Error loading dashboard:", err);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <PageTransition className="flex flex-col gap-6 w-full max-w-7xl mx-auto">
      {/* Header Section */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-black leading-tight tracking-tight text-foreground">
            Dashboard Principal
          </h1>
          <p className="text-muted-foreground">
            Resumen de la actividad de la clínica para este mes.
          </p>
        </div>

        {/* Time Period Selector */}
        <div className="flex gap-2 p-1 bg-background/50 rounded-lg">
          {['Hoy', 'Esta Semana', 'Este Mes', 'Este Año'].map((label) => {
            const isActive = label === 'Este Mes';
            return (
              <Button
                key={label}
                variant={isActive ? 'default' : 'outline'}
                className={`h-8 px-4 text-sm font-medium ${!isActive ? 'bg-white dark:bg-card border-none shadow-sm' : ''}`}
                size="sm"
              >
                {label}
              </Button>
            );
          })}
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Ingresos Totales', value: `$${stats?.total_income?.toFixed(2) || '0.00'}`, change: '+8.2%', trend: 'up' },
          { label: 'Facturas', value: stats?.invoice_count?.toString() || '0', change: '+5.4%', trend: 'up' },
          { label: 'Gastos Totales', value: `$${stats?.total_expenses?.toFixed(2) || '0.00'}`, change: '+12%', trend: 'down' },
          { label: 'Ganancia', value: `$${stats?.profit?.toFixed(2) || '0.00'}`, change: `${stats?.profit_margin?.toFixed(1) || '0'}%`, trend: (stats?.profit || 0) >= 0 ? 'up' : 'down' },
        ].map((item, i) => (
          <Card key={i} className="border-border/50 shadow-sm transition-all hover:shadow-md">
            <CardContent className="p-6 flex flex-col gap-2">
              <p className="text-base font-medium text-muted-foreground">{item.label}</p>
              <p className="text-3xl font-bold tracking-tight text-foreground">{item.value}</p>
              <div className={`flex items-center text-sm font-medium ${item.trend === 'up' ? 'text-green-600 dark:text-green-500' : 'text-red-600 dark:text-red-500'}`}>
                {item.change}
                {item.trend === 'up' ? <ArrowUp className="w-4 h-4 ml-1" /> : <ArrowDown className="w-4 h-4 ml-1" />}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
        {/* Income vs Expenses Chart */}
        <Card className="lg:col-span-3 border-border/50 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div>
              <CardTitle className="text-lg font-bold">Ingresos vs. Egresos</CardTitle>
              <CardDescription>Rendimiento financiero del mes actual.</CardDescription>
            </div>
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-primary" />
                <span className="text-muted-foreground">Ingresos</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-muted-foreground/30" />
                <span className="text-muted-foreground">Egresos</span>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full mt-4 bg-gray-50/50 dark:bg-gray-800/20 rounded-lg p-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={financialData} barGap={8}>
                  <XAxis
                    dataKey="name"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#888888', fontSize: 12 }}
                    dy={10}
                  />
                  <Tooltip
                    cursor={{ fill: 'transparent' }}
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                  />
                  <Bar dataKey="ingresos" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} barSize={32} />
                  <Bar dataKey="egresos" fill="hsl(var(--muted-foreground))" opacity={0.3} radius={[4, 4, 0, 0]} barSize={32} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Today's Appointments Widget */}
        <div className="lg:col-span-2">
          <TodayAppointmentsWidget />
        </div>
      </div>

      {/* Low Stock Widget */}
      <LowStockWidget />
    </PageTransition>
  );
}
