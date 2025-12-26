"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
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
    Loader2
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { PageTransition } from "@/components/page-transition";
import { auth } from "@/lib/auth";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";

// TypeScript Interfaces
interface Appointment {
  appointment_id: number;
  patient_id: number;
  patient_name: string;
  doctor_id: number;
  doctor_name: string;
  start_time: string; // ISO 8601
  end_time: string;
  status: 'PENDING' | 'CONFIRMED' | 'COMPLETED' | 'CANCELLED';
  reason: string;
  notes?: string;
}

interface CalendarDay {
  day: number;
  date: string; // YYYY-MM-DD
  isCurrentMonth: boolean;
  appointments: Appointment[];
}

// Calendar Grid Generator
const days = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];

export default function AppointmentsPage() {
    const { toast } = useToast();
    const [view, setView] = React.useState('Mes');
    const [selectedDate, setSelectedDate] = React.useState<number | null>(7);
    const [appointments, setAppointments] = React.useState<Appointment[]>([]);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState("");
    const [currentMonth, setCurrentMonth] = React.useState(new Date());
    const [selectedAppointment, setSelectedAppointment] = React.useState<any | null>(null);
    const [loadingDetails, setLoadingDetails] = React.useState(false);

    // New appointment modal state
    const [showNewAppointmentModal, setShowNewAppointmentModal] = React.useState(false);
    const [patients, setPatients] = React.useState<any[]>([]);
    const [doctors, setDoctors] = React.useState<any[]>([]);
    const [loadingPatients, setLoadingPatients] = React.useState(false);
    const [loadingDoctors, setLoadingDoctors] = React.useState(false);
    const [creatingAppointment, setCreatingAppointment] = React.useState(false);

    // New appointment form data
    const [newAppointment, setNewAppointment] = React.useState({
        patient_id: '',
        doctor_id: '',
        date: '',
        start_time: '',
        end_time: '',
        reason: '',
        status: 'PENDING'
    });

    // Fetch appointments from backend
    const fetchAppointments = React.useCallback(async (month: Date) => {
        try {
            setLoading(true);
            const year = month.getFullYear();
            const monthNum = month.getMonth() + 1;

            const response = await fetch(
                `/api/citas/appointments?year=${year}&month=${monthNum}`,
                {
                    headers: {
                        'Authorization': `Bearer ${auth.getToken()}`
                    }
                }
            );

            if (!response.ok) throw new Error("Error al cargar citas");

            const data = await response.json();
            if (data.success && data.data) {
                setAppointments(data.data.appointments || []);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : "Error desconocido");
        } finally {
            setLoading(false);
        }
    }, []);

    React.useEffect(() => {
        fetchAppointments(currentMonth);
    }, [currentMonth, fetchAppointments]);

    // Fetch appointment details
    const fetchAppointmentDetails = React.useCallback(async (appointmentId: number) => {
        try {
            setLoadingDetails(true);
            const response = await fetch(
                `/api/citas/appointments/${appointmentId}`,
                {
                    headers: {
                        'Authorization': `Bearer ${auth.getToken()}`
                    }
                }
            );

            if (!response.ok) throw new Error("Error al cargar detalles");

            const data = await response.json();
            if (data.success && data.data.appointment) {
                setSelectedAppointment(data.data.appointment);
            }
        } catch (err) {
            console.error("Error loading appointment details:", err);
            setSelectedAppointment(null);
        } finally {
            setLoadingDetails(false);
        }
    }, []);

    // Fetch patients for dropdown
    const fetchPatients = React.useCallback(async () => {
        try {
            setLoadingPatients(true);
            const response = await fetch('/api/historia-clinica/patients?per_page=100', {
                headers: {
                    'Authorization': `Bearer ${auth.getToken()}`
                }
            });

            if (!response.ok) throw new Error("Error al cargar pacientes");

            const data = await response.json();
            if (data.success && data.data.patients) {
                setPatients(data.data.patients);
            }
        } catch (err) {
            console.error("Error loading patients:", err);
            toast({
                title: "Error",
                description: "No se pudieron cargar los pacientes",
                variant: "destructive",
            });
        } finally {
            setLoadingPatients(false);
        }
    }, [toast]);

    // Fetch doctors (users with role doctor)
    const fetchDoctors = React.useCallback(async () => {
        try {
            setLoadingDoctors(true);
            const response = await fetch('/api/auth/users?role=doctor', {
                headers: {
                    'Authorization': `Bearer ${auth.getToken()}`
                }
            });

            if (!response.ok) throw new Error("Error al cargar doctores");

            const data = await response.json();
            if (data.success && data.data.users) {
                setDoctors(data.data.users);
            }
        } catch (err) {
            console.error("Error loading doctors:", err);
            toast({
                title: "Error",
                description: "No se pudieron cargar los doctores",
                variant: "destructive",
            });
        } finally {
            setLoadingDoctors(false);
        }
    }, [toast]);

    // Open new appointment modal
    const handleOpenNewAppointmentModal = () => {
        setShowNewAppointmentModal(true);
        fetchPatients();
        fetchDoctors();
    };

    // Create new appointment
    const handleCreateAppointment = async () => {
        if (!newAppointment.patient_id || !newAppointment.doctor_id || !newAppointment.date || !newAppointment.start_time || !newAppointment.end_time) {
            toast({
                title: "Error",
                description: "Complete todos los campos requeridos",
                variant: "destructive",
            });
            return;
        }

        try {
            setCreatingAppointment(true);

            const startDateTime = `${newAppointment.date}T${newAppointment.start_time}:00`;
            const endDateTime = `${newAppointment.date}T${newAppointment.end_time}:00`;

            const payload = {
                patient_id: parseInt(newAppointment.patient_id),
                doctor_id: parseInt(newAppointment.doctor_id),
                start_time: startDateTime,
                end_time: endDateTime,
                reason: newAppointment.reason || null,
                status: newAppointment.status
            };

            const response = await fetch('/api/citas/appointments', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${auth.getToken()}`
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (data.success) {
                toast({
                    title: "Cita creada",
                    description: "La cita se ha creado exitosamente",
                });
                setShowNewAppointmentModal(false);
                setNewAppointment({
                    patient_id: '',
                    doctor_id: '',
                    date: '',
                    start_time: '',
                    end_time: '',
                    reason: '',
                    status: 'PENDING'
                });
                fetchAppointments(currentMonth);
            } else {
                throw new Error(data.message || 'Error al crear cita');
            }
        } catch (error) {
            toast({
                title: "Error",
                description: error instanceof Error ? error.message : "No se pudo crear la cita",
                variant: "destructive",
            });
        } finally {
            setCreatingAppointment(false);
        }
    };

    // Generate calendar days dynamically
    const generateCalendarDays = React.useMemo(() => {
        const year = currentMonth.getFullYear();
        const month = currentMonth.getMonth();
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startOffset = firstDay.getDay();

        const calendarDays: CalendarDay[] = [];

        // Días del mes anterior
        const prevMonthLastDay = new Date(year, month, 0).getDate();
        for (let i = startOffset - 1; i >= 0; i--) {
            calendarDays.push({
                day: prevMonthLastDay - i,
                date: new Date(year, month - 1, prevMonthLastDay - i).toISOString().split('T')[0],
                isCurrentMonth: false,
                appointments: []
            });
        }

        // Días del mes actual
        for (let day = 1; day <= lastDay.getDate(); day++) {
            const dateStr = new Date(year, month, day).toISOString().split('T')[0];
            const dayAppointments = appointments.filter(apt =>
                apt.start_time.split('T')[0] === dateStr
            );

            calendarDays.push({
                day,
                date: dateStr,
                isCurrentMonth: true,
                appointments: dayAppointments
            });
        }

        // Días del mes siguiente
        const remaining = 35 - calendarDays.length;
        for (let day = 1; day <= remaining; day++) {
            calendarDays.push({
                day,
                date: new Date(year, month + 1, day).toISOString().split('T')[0],
                isCurrentMonth: false,
                appointments: []
            });
        }

        return calendarDays;
    }, [currentMonth, appointments]);

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
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))}
                                >
                                    <ChevronLeft className="h-4 w-4" />
                                </Button>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))}
                                >
                                    <ChevronRight className="h-4 w-4" />
                                </Button>
                            </div>
                            <h3 className="text-lg font-semibold">
                                {currentMonth.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })}
                            </h3>
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

                        <Button className="gap-2" onClick={handleOpenNewAppointmentModal}>
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
                        {loading && (
                            <div className="flex items-center justify-center h-[600px]">
                                <div className="text-center">
                                    <Loader2 className="h-12 w-12 border-b-2 border-primary mx-auto animate-spin" />
                                    <p className="mt-4 text-sm text-muted-foreground">Cargando citas...</p>
                                </div>
                            </div>
                        )}

                        {error && (
                            <div className="flex items-center justify-center h-[600px]">
                                <div className="text-center text-red-500">
                                    <p>Error: {error}</p>
                                    <Button onClick={() => fetchAppointments(currentMonth)} className="mt-4">
                                        Reintentar
                                    </Button>
                                </div>
                            </div>
                        )}

                        {!loading && !error && (
                            <div className="grid grid-cols-7 h-full min-h-[600px] border-l border-t border-border">
                                {days.map(day => (
                                    <div key={day} className="text-center text-sm font-semibold text-muted-foreground py-3 border-b border-r border-border bg-muted/5">
                                        {day}
                                    </div>
                                ))}
                                {generateCalendarDays.map((date, i) => (
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
                                                    key={apt.appointment_id}
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        fetchAppointmentDetails(apt.appointment_id);
                                                    }}
                                                    className={`
                              text-xs p-1.5 rounded-md truncate font-medium cursor-pointer hover:opacity-80 transition-opacity
                              ${apt.status === 'CONFIRMED' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : ''}
                              ${apt.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300' : ''}
                              ${apt.status === 'COMPLETED' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300' : ''}
                              ${apt.status === 'CANCELLED' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300' : ''}
                              ${selectedAppointment?.appointment_id === apt.appointment_id ? 'ring-2 ring-primary ring-offset-1' : ''}
                            `}
                                                >
                                                    <b>{new Date(apt.start_time).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}</b> {apt.patient_name}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Sidebar Details Panel */}
                <div className="w-96 flex-shrink-0 bg-card rounded-xl border border-border shadow-sm flex flex-col overflow-hidden">
                    {loadingDetails ? (
                        <div className="flex-1 flex items-center justify-center">
                            <div className="text-center">
                                <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
                                <p className="mt-2 text-sm text-muted-foreground">Cargando detalles...</p>
                            </div>
                        </div>
                    ) : !selectedAppointment ? (
                        <div className="flex-1 flex items-center justify-center p-6">
                            <div className="text-center">
                                <BriefcaseMedical className="h-16 w-16 mx-auto text-muted-foreground/30 mb-4" />
                                <p className="text-sm text-muted-foreground">Seleccione una cita del calendario para ver los detalles</p>
                            </div>
                        </div>
                    ) : (
                        <>
                            <div className="p-4 border-b border-border bg-muted/10">
                                <h3 className="text-lg font-semibold">Detalles de la Cita</h3>
                                <p className="text-sm text-muted-foreground">
                                    {new Date(selectedAppointment.start_time).toLocaleDateString('es-ES', {
                                        weekday: 'long',
                                        year: 'numeric',
                                        month: 'long',
                                        day: 'numeric'
                                    })} - {new Date(selectedAppointment.start_time).toLocaleTimeString('es-ES', {
                                        hour: '2-digit',
                                        minute: '2-digit'
                                    })}
                                </p>
                            </div>

                            <div className="flex-1 p-6 space-y-8 overflow-y-auto">
                                {/* Patient Info */}
                                <div>
                                    <h4 className="text-sm font-medium text-muted-foreground mb-3">Paciente</h4>
                                    <div className="flex items-center gap-3">
                                        <Avatar className="h-12 w-12 border border-border">
                                            <AvatarFallback>
                                                {selectedAppointment.patient_name?.split(' ').map((n: string) => n[0]).join('').substring(0, 2).toUpperCase() || 'PA'}
                                            </AvatarFallback>
                                        </Avatar>
                                        <div>
                                            <p className="font-semibold text-foreground">{selectedAppointment.patient_name || 'N/A'}</p>
                                            <p className="text-sm text-muted-foreground">{selectedAppointment.patient_phone || 'Sin teléfono'}</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Appointment Info */}
                                <div>
                                    <h4 className="text-sm font-medium text-muted-foreground mb-3">Información</h4>
                                    <div className="space-y-4 rounded-lg bg-muted/20 p-4 border border-border">
                                        <div className="flex items-center gap-3 text-sm">
                                            <Clock className="w-4 h-4 text-primary" />
                                            <span>
                                                {new Date(selectedAppointment.start_time).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })} - {new Date(selectedAppointment.end_time).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}
                                            </span>
                                        </div>
                                        <div className="flex items-center gap-3 text-sm">
                                            <BriefcaseMedical className="w-4 h-4 text-primary" />
                                            <span>{selectedAppointment.reason || 'Sin motivo especificado'}</span>
                                        </div>
                                        <div className="flex items-center gap-3 text-sm">
                                            <MapPin className="w-4 h-4 text-primary" />
                                            <span>Dr. {selectedAppointment.doctor_name || 'N/A'}</span>
                                        </div>
                                        {selectedAppointment.notes && (
                                            <div className="pt-2 border-t border-border">
                                                <p className="text-xs text-muted-foreground mb-1">Notas:</p>
                                                <p className="text-sm">{selectedAppointment.notes}</p>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Status */}
                                <div>
                                    <h4 className="text-sm font-medium text-muted-foreground mb-3">Estado</h4>
                                    <Badge
                                        variant="outline"
                                        className={`
                                            border-transparent px-3 py-1
                                            ${selectedAppointment.status === 'CONFIRMED' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : ''}
                                            ${selectedAppointment.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300' : ''}
                                            ${selectedAppointment.status === 'COMPLETED' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300' : ''}
                                            ${selectedAppointment.status === 'CANCELLED' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300' : ''}
                                        `}
                                    >
                                        <span className={`
                                            w-2 h-2 rounded-full mr-2
                                            ${selectedAppointment.status === 'CONFIRMED' ? 'bg-green-500' : ''}
                                            ${selectedAppointment.status === 'PENDING' ? 'bg-yellow-500' : ''}
                                            ${selectedAppointment.status === 'COMPLETED' ? 'bg-blue-500' : ''}
                                            ${selectedAppointment.status === 'CANCELLED' ? 'bg-red-500' : ''}
                                        `} />
                                        {selectedAppointment.status === 'CONFIRMED' && 'Confirmada'}
                                        {selectedAppointment.status === 'PENDING' && 'Pendiente'}
                                        {selectedAppointment.status === 'COMPLETED' && 'Completada'}
                                        {selectedAppointment.status === 'CANCELLED' && 'Cancelada'}
                                    </Badge>
                                </div>

                                {/* Treatments and Extras */}
                                {(selectedAppointment.treatments?.length > 0 || selectedAppointment.extras?.length > 0) && (
                                    <div>
                                        <h4 className="text-sm font-medium text-muted-foreground mb-3">Servicios</h4>
                                        <div className="space-y-2">
                                            {selectedAppointment.treatments?.map((treatment: any, idx: number) => (
                                                <div key={idx} className="flex justify-between text-sm p-2 bg-muted/20 rounded">
                                                    <span>{treatment.treatment_name}</span>
                                                    <span className="font-medium">${treatment.price?.toFixed(2)}</span>
                                                </div>
                                            ))}
                                            {selectedAppointment.extras?.map((extra: any, idx: number) => (
                                                <div key={idx} className="flex justify-between text-sm p-2 bg-muted/20 rounded">
                                                    <span>{extra.description}</span>
                                                    <span className="font-medium">${extra.price?.toFixed(2)}</span>
                                                </div>
                                            ))}
                                            {selectedAppointment.total > 0 && (
                                                <div className="flex justify-between text-sm font-bold pt-2 border-t border-border">
                                                    <span>Total</span>
                                                    <span>${selectedAppointment.total?.toFixed(2)}</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>

                            <div className="p-4 border-t border-border flex gap-3 bg-muted/10">
                                <Button variant="outline" className="flex-1">Reprogramar</Button>
                                <Button className="flex-1">Guardar</Button>
                            </div>
                        </>
                    )}
                </div>
            </div>

            {/* New Appointment Modal */}
            <Dialog open={showNewAppointmentModal} onOpenChange={setShowNewAppointmentModal}>
                <DialogContent className="sm:max-w-[500px]">
                    <DialogHeader>
                        <DialogTitle>Nueva Cita</DialogTitle>
                        <DialogDescription>
                            Complete los datos para crear una nueva cita médica
                        </DialogDescription>
                    </DialogHeader>

                    <div className="space-y-4 py-4">
                        {/* Patient Selection */}
                        <div className="space-y-2">
                            <Label htmlFor="patient">Paciente *</Label>
                            <Select
                                value={newAppointment.patient_id}
                                onValueChange={(value) => setNewAppointment({ ...newAppointment, patient_id: value })}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder={loadingPatients ? "Cargando pacientes..." : "Seleccione un paciente"} />
                                </SelectTrigger>
                                <SelectContent>
                                    {patients.map((patient) => (
                                        <SelectItem key={patient.patient_id} value={patient.patient_id.toString()}>
                                            {patient.full_name} - {patient.identification}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        {/* Doctor Selection */}
                        <div className="space-y-2">
                            <Label htmlFor="doctor">Doctor *</Label>
                            <Select
                                value={newAppointment.doctor_id}
                                onValueChange={(value) => setNewAppointment({ ...newAppointment, doctor_id: value })}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder={loadingDoctors ? "Cargando doctores..." : "Seleccione un doctor"} />
                                </SelectTrigger>
                                <SelectContent>
                                    {doctors.map((doctor) => (
                                        <SelectItem key={doctor.user_id} value={doctor.user_id.toString()}>
                                            Dr. {doctor.full_name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        {/* Date */}
                        <div className="space-y-2">
                            <Label htmlFor="date">Fecha *</Label>
                            <Input
                                id="date"
                                type="date"
                                value={newAppointment.date}
                                onChange={(e) => setNewAppointment({ ...newAppointment, date: e.target.value })}
                            />
                        </div>

                        {/* Time Range */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="start_time">Hora Inicio *</Label>
                                <Input
                                    id="start_time"
                                    type="time"
                                    value={newAppointment.start_time}
                                    onChange={(e) => setNewAppointment({ ...newAppointment, start_time: e.target.value })}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="end_time">Hora Fin *</Label>
                                <Input
                                    id="end_time"
                                    type="time"
                                    value={newAppointment.end_time}
                                    onChange={(e) => setNewAppointment({ ...newAppointment, end_time: e.target.value })}
                                />
                            </div>
                        </div>

                        {/* Reason */}
                        <div className="space-y-2">
                            <Label htmlFor="reason">Motivo de consulta</Label>
                            <Textarea
                                id="reason"
                                placeholder="Ingrese el motivo de la consulta..."
                                value={newAppointment.reason}
                                onChange={(e) => setNewAppointment({ ...newAppointment, reason: e.target.value })}
                                rows={3}
                            />
                        </div>

                        {/* Status */}
                        <div className="space-y-2">
                            <Label htmlFor="status">Estado</Label>
                            <Select
                                value={newAppointment.status}
                                onValueChange={(value) => setNewAppointment({ ...newAppointment, status: value })}
                            >
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="PENDING">Pendiente</SelectItem>
                                    <SelectItem value="CONFIRMED">Confirmada</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    <DialogFooter>
                        <Button
                            variant="outline"
                            onClick={() => setShowNewAppointmentModal(false)}
                            disabled={creatingAppointment}
                        >
                            Cancelar
                        </Button>
                        <Button onClick={handleCreateAppointment} disabled={creatingAppointment}>
                            {creatingAppointment ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Creando...
                                </>
                            ) : (
                                'Crear Cita'
                            )}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </PageTransition>
    );
}
