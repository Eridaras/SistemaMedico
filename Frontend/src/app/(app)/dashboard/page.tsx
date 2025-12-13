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
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  BarChart,
  Bar,
  XAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import {
  ArrowUp,
  ArrowDown,
  MoreVertical
} from "lucide-react";
import { PageTransition } from "@/components/page-transition";

// Mock Data matching the design
const financialData = [
  { name: 'Sem 1', ingresos: 4500, egresos: 2100 },
  { name: 'Sem 2', ingresos: 5800, egresos: 3200 },
  { name: 'Sem 3', ingresos: 7200, egresos: 2400 },
  { name: 'Sem 4', ingresos: 6100, egresos: 2800 },
];

const todaysAppointments = [
  {
    id: 1,
    name: "Carlos Mendoza",
    time: "10:30 AM",
    type: "Consulta General",
    avatar: "https://lh3.googleusercontent.com/aida-public/AB6AXuAKQ6Ee45IRLU3KVP9d9PAkLBJpWomajVTF5_K6_R-Xms7poJknDT7bfUY6_hFJfa8oA_I4sju6HgXUZ4k1khOvsmiQwxGRjkvv1X0Yp50BsY9Esm02pEmf7vTgVxxadg85Vh_itLjtxF5GEPsHR2AhTZnQ8eT5fV3ZZXCX8RfSq4ZOFyjbZmExyijcRvRtIaVgKcUS5RoWf2pl0V1NWtTrgdsYHkWAU4lg-lVRtZCGfBBbyJMejC8v_uhDDmDTdrC4z2_nwNn4OlFy"
  },
  {
    id: 2,
    name: "Ana Jiménez",
    time: "11:00 AM",
    type: "Control",
    avatar: "https://lh3.googleusercontent.com/aida-public/AB6AXuAnwoBytQ8L__yDWODA5JrGsJLyAKZASOICoyynYpd60dYCz17wfgVp_8elclDltGub8pxVFtOk9YV-GiEd3SAp4tT1XjyKTfU6sUlULfxzcGd7fCw4zGtKnIV2-rG7KYsZV9zFHL0Y5t885ciJs9eLtHwgRsPfjinVGAu1E28rBM_xp_Hjr1U-CzWS8lO8AumWYvxracc1BE6Fbyanll6u87MHVuZgAy5HYR2c_7x6pIP7WYCIPiKk6U8Wbh5NgsBJlL6AoN9xM-Tm"
  },
  {
    id: 3,
    name: "Sofia Rodriguez",
    time: "12:15 PM",
    type: "Limpieza Dental",
    avatar: "https://lh3.googleusercontent.com/aida-public/AB6AXuDfkyH3M1CuSH1Yj6pqDmU-Sj9lCSwqy62dRc3w0NmEoyvL4kgAbFoMWOEzcGUIvioFFsebKNodZxOZnvDBAXOL_fD7HZvCm26WIJRQmzFLuEwNwC9V00kb_HreT-EKf2_0etIw7uj5hkrzwDmfhup-1jl1ZLSTyswIGugqtOH8qhZ7sJlT_8mNNB4XDQ1fJiTdbX0HFHXLeCLu1KHJIuX0N1XJCy56PmRYB18b74RXkywRtRke1v68IArDM1IdNQXDjzC7LXe2kGhR"
  },
  {
    id: 4,
    name: "Javier Torres",
    time: "01:00 PM",
    type: "Consulta General",
    avatar: "https://lh3.googleusercontent.com/aida-public/AB6AXuBGi3e_Wzo9LwdCvYKZatIe9oWXbSLEZrkkyQ2uJjcw2zpBxJ8JC0T0X59t5jCPK5yuEtKb8DZm5R0uZPPd4sk8wg-LpWJx3JHVgOsgtZ4EWlEoPxv1dfqt2ug5Gd_q2QhO0GmDD_l6NZdSjjxQ7VvEukzFbsO4N9qCW-hR_WoNmV57who9kNaDPcOgZ13-1RoLb5Re5Xue1ShsIp9zJ4m6Syuo5slDSSujPjrgTx85Kts48nkrLtGnNEwEYo8PWQ5JeAGaYlIVwVCU"
  }
];

export default function DashboardPage() {
  const [period, setPeriod] = React.useState('mes');

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
          { label: 'Ventas Totales', value: '$12,450.00', change: '+8.2%', trend: 'up' },
          { label: 'Pacientes Nuevos', value: '32', change: '+5.4%', trend: 'up' },
          { label: 'Tratamientos Vendidos', value: '56', change: '+1.8%', trend: 'up' },
          { label: 'Gastos Totales', value: '$3,120.00', change: '-2.1%', trend: 'down' },
        ].map((item, i) => (
          <Card key={i} className="border-border/50 shadow-sm transition-all hover:shadow-md">
            <CardContent className="p-6 flex flex-col gap-2">
              <p className="text-base font-medium text-muted-foreground">{item.label}</p>
              <p className="text-3xl font-bold tracking-tight text-foreground">{item.value}</p>
              <div className={`flex items-center text-sm font-medium ${item.trend === 'up' && item.label !== 'Gastos Totales' ? 'text-green-600 dark:text-green-500' : 'text-red-600 dark:text-red-500'}`}>
                {item.change}
                {item.trend === 'up' ? <ArrowUp className="w-4 h-4 ml-1" /> : <ArrowDown className="w-4 h-4 ml-1" />}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Income vs Expenses Chart */}
        <Card className="lg:col-span-2 border-border/50 shadow-sm">
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

        {/* Today's Appointments List */}
        <Card className="border-border/50 shadow-sm">
          <CardHeader>
            <CardTitle className="text-lg font-bold">Citas de Hoy</CardTitle>
            <CardDescription>Próximos pacientes para el día.</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-6 mt-2">
              {todaysAppointments.map((apt) => (
                <li key={apt.id} className="flex items-center gap-4">
                  <Avatar className="h-10 w-10 border-2 border-white dark:border-gray-800 shadow-sm">
                    <AvatarImage src={apt.avatar} alt={apt.name} />
                    <AvatarFallback>{apt.name[0]}</AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">{apt.name}</p>
                    <p className="text-xs text-muted-foreground truncate">
                      {apt.time} - {apt.type}
                    </p>
                  </div>
                  <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>
    </PageTransition>
  );
}
