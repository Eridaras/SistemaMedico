"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import {
    ChevronLeft,
    ChevronRight,
    Plus,
    Search,
    Bell,
    MessageSquare,
    Filter,
    Building,
    Clock,
    BriefcaseMedical,
    MapPin,
    Settings,
    CheckCircle2
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { PageTransition } from "@/components/page-transition";

// Calendar Grid Generator
const days = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
const calendarDays = Array.from({ length: 35 }, (_, i) => {
    const day = i - 4; // Offset to start previous month
    const isCurrentMonth = day > 0 && day <= 30;
    return {
        day: day > 0 && day <= 30 ? day : day <= 0 ? 30 + day : day - 30,
        isCurrentMonth,
        appointments: day === 7 ? [
            { id: 1, time: '9:00', patient: 'Juan Pérez', type: 'General', color: 'green' },
            { id: 2, time: '10:30', patient: 'María López', type: 'Control', color: 'teal' },
            { id: 3, time: '11:15', patient: 'Carlos Gil', type: 'Dental', color: 'orange' },
        ] : []
    };
});

export default function AppointmentsPage() {
    const [view, setView] = React.useState('Mes');
    const [selectedDate, setSelectedDate] = React.useState<number | null>(7);

    return (
        <PageTransition className="flex flex-col h-[calc(100vh-8rem)] gap-6 w-full mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold tracking-tight text-foreground">Agendamiento de Citas</h1>
                <div className="flex items-center gap-2">
                    <div className="relative hidden md:block w-64">
                        <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input placeholder="Buscar paciente..." className="pl-9 bg-background" />
                    </div>
                    <Button variant="outline" size="icon" className="rounded-full">
                        <Bell className="h-4 w-4" />
                    </Button>
                    <Button variant="outline" size="icon" className="rounded-full">
                        <MessageSquare className="h-4 w-4" />
                    </Button>
                </div>
            </div>

            <div className="flex flex-1 gap-6 overflow-hidden">
                {/* Calendar Section */}
                <div className="flex flex-1 flex-col bg-card rounded-xl border border-border shadow-sm overflow-hidden">
                    {/* Calendar Toolbar */}
                    <div className="flex flex-wrap justify-between items-center gap-4 p-4 border-b border-border">
                        <div className="flex items-center gap-4">
                            <div className="flex gap-1">
                                <Button variant="ghost" size="icon"><ChevronLeft className="h-4 w-4" /></Button>
                                <Button variant="ghost" size="icon"><ChevronRight className="h-4 w-4" /></Button>
                            </div>
                            <h3 className="text-lg font-semibold">Diciembre 2023</h3>
                        </div>

                        <div className="flex bg-muted/50 p-1 rounded-lg">
                            {['Mes', 'Semana', 'Día'].map((v) => (
                                <Button
                                    key={v}
                                    variant={view === v ? 'default' : 'ghost'}
                                    size="sm"
                                    onClick={() => setView(v)}
                                    className="rounded-md"
                                >
                                    {v}
                                </Button>
                            ))}
                        </div>

                        <Button className="gap-2">
                            <Plus className="h-4 w-4" />
                            Nueva Cita
                        </Button>
                    </div>

                    {/* Filters */}
                    <div className="flex gap-3 p-4 border-b border-border overflow-x-auto bg-muted/10">
                        <Button variant="outline" size="sm" className="gap-2 text-muted-foreground">
                            Doctor <Filter className="h-3 w-3" />
                        </Button>
                        <Button variant="outline" size="sm" className="gap-2 text-muted-foreground">
                            Especialidad <BriefcaseMedical className="h-3 w-3" />
                        </Button>
                        <Button variant="outline" size="sm" className="gap-2 text-muted-foreground">
                            Consultorio <Building className="h-3 w-3" />
                        </Button>
                    </div>

                    {/* Calendar Grid */}
                    <div className="flex-1 overflow-auto p-4">
                        <div className="grid grid-cols-7 h-full min-h-[600px] border-l border-t border-border">
                            {days.map(day => (
                                <div key={day} className="text-center text-sm font-semibold text-muted-foreground py-3 border-b border-r border-border bg-muted/5">
                                    {day}
                                </div>
                            ))}
                            {calendarDays.map((date, i) => (
                                <div
                                    key={i}
                                    onClick={() => date.isCurrentMonth && setSelectedDate(date.day)}
                                    className={`
                    relative min-h-[100px] p-2 border-b border-r border-border transition-colors cursor-pointer
                    ${!date.isCurrentMonth ? 'bg-muted/10 text-muted-foreground/50' : 'hover:bg-muted/20'}
                    ${selectedDate === date.day && date.isCurrentMonth ? 'bg-primary/5 ring-1 ring-inset ring-primary' : ''}
                  `}
                                >
                                    <span className={`
                    text-sm font-medium
                    ${selectedDate === date.day && date.isCurrentMonth ? 'text-primary font-bold' : ''}
                  `}>
                                        {date.day}
                                    </span>

                                    <div className="mt-2 space-y-1">
                                        {date.appointments.map(apt => (
                                            <div
                                                key={apt.id}
                                                className={`
                          text-xs p-1.5 rounded-md truncate font-medium
                          ${apt.color === 'green' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : ''}
                          ${apt.color === 'teal' ? 'bg-teal-100 text-teal-800 dark:bg-teal-900/30 dark:text-teal-300' : ''}
                          ${apt.color === 'orange' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300' : ''}
                        `}
                                            >
                                                <b>{apt.time}</b> {apt.patient}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Sidebar Details Panel */}
                <div className="w-96 flex-shrink-0 bg-card rounded-xl border border-border shadow-sm flex flex-col overflow-hidden">
                    <div className="p-4 border-b border-border bg-muted/10">
                        <h3 className="text-lg font-semibold">Detalles de la Cita</h3>
                        <p className="text-sm text-muted-foreground">Jueves, 7 de Diciembre, 2023 - 9:00 AM</p>
                    </div>

                    <div className="flex-1 p-6 space-y-8 overflow-y-auto">
                        {/* Patient Info */}
                        <div>
                            <h4 className="text-sm font-medium text-muted-foreground mb-3">Paciente</h4>
                            <div className="flex items-center gap-3">
                                <Avatar className="h-12 w-12 border border-border">
                                    <AvatarImage src="https://lh3.googleusercontent.com/aida-public/AB6AXuD_kfhe9-hnfTorRBu0Tp_uJUM1R9WujxtIch8mXhFaAAy5QclSACoyBNDx-LHM3GXEAfvRT04enx20bGKcYf8XidX4p6AYlVcjv3cBv4W2NTjZtiL8i21g1pK5A0KIjva54AdFMXNhP-G19vfMUazntoUlZ-tlV9DB9RNI75hDUDJoRR82eZgGkqmJKowAEb7Zt7T_eo8hMvaRyDiC7y7uya_pjpcy3ji6d0KJQwahGAJea7nyICA6XaPKUdXX0AfMEL-A39jSuGqN" />
                                    <AvatarFallback>JP</AvatarFallback>
                                </Avatar>
                                <div>
                                    <p className="font-semibold text-foreground">Juan Pérez</p>
                                    <p className="text-sm text-muted-foreground">+57 300 123 4567</p>
                                </div>
                            </div>
                        </div>

                        {/* Appointment Info */}
                        <div>
                            <h4 className="text-sm font-medium text-muted-foreground mb-3">Información</h4>
                            <div className="space-y-4 rounded-lg bg-muted/20 p-4 border border-border">
                                <div className="flex items-center gap-3 text-sm">
                                    <Clock className="w-4 h-4 text-primary" />
                                    <span>9:00 AM - 9:30 AM (30 min)</span>
                                </div>
                                <div className="flex items-center gap-3 text-sm">
                                    <BriefcaseMedical className="w-4 h-4 text-primary" />
                                    <span>Consulta General</span>
                                </div>
                                <div className="flex items-center gap-3 text-sm">
                                    <MapPin className="w-4 h-4 text-primary" />
                                    <span>Consultorio 3</span>
                                </div>
                            </div>
                        </div>

                        {/* Status */}
                        <div>
                            <h4 className="text-sm font-medium text-muted-foreground mb-3">Estado</h4>
                            <Badge variant="outline" className="bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 border-transparent px-3 py-1">
                                <span className="w-2 h-2 rounded-full bg-green-500 mr-2" />
                                Confirmada
                            </Badge>
                        </div>

                        {/* Notifications */}
                        <div className="space-y-4">
                            <div className="flex justify-between items-center">
                                <h4 className="text-sm font-medium text-muted-foreground">Notificaciones</h4>
                                <Button variant="ghost" size="sm" className="h-6 text-xs gap-1 text-primary">
                                    <Settings className="w-3 h-3" /> Configurar
                                </Button>
                            </div>

                            <div className="bg-muted/10 rounded-lg border border-border p-4 space-y-4">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2 text-sm font-medium">
                                        <MessageSquare className="w-4 h-4 text-green-500" />
                                        WhatsApp
                                    </div>
                                    <Switch checked />
                                </div>
                                <div className="flex items-center gap-2 text-xs text-green-600 dark:text-green-400">
                                    <CheckCircle2 className="w-3 h-3" /> Enviado hace 2 horas
                                </div>

                                <div className="border-t border-border" />

                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2 text-sm font-medium">
                                        <Bell className="w-4 h-4 text-blue-500" />
                                        Email
                                    </div>
                                    <Switch checked />
                                </div>
                                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                    <Clock className="w-3 h-3" /> Programado en 1 día
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="p-4 border-t border-border flex gap-3 bg-muted/10">
                        <Button variant="outline" className="flex-1">Reprogramar</Button>
                        <Button className="flex-1">Guardar</Button>
                    </div>
                </div>
            </div>
        </PageTransition>
    );
}
