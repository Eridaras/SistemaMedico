"use client";

import * as React from "react";
import { Calendar, Clock, User, Phone, FileText } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { auth } from "@/lib/auth";
import { format } from "date-fns";
import { es } from "date-fns/locale";

interface Appointment {
    appointment_id: number;
    start_time: string;
    end_time: string;
    status: string;
    reason: string;
    patient_name: string;
    patient_phone: string;
    patient_email: string;
    doc_number: string;
}

interface TodayAppointmentsData {
    count: number;
    appointments: Appointment[];
    date: string;
}

export function TodayAppointmentsWidget() {
    const [data, setData] = React.useState<TodayAppointmentsData | null>(null);
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
        const fetchTodayAppointments = async () => {
            try {
                const response = await fetch('/api/notifications/appointments/today', {
                    headers: {
                        'Authorization': `Bearer ${auth.getToken()}`
                    }
                });

                if (!response.ok) {
                    // If user is not a doctor, they won't have access
                    if (response.status === 403) {
                        setLoading(false);
                        return;
                    }
                    throw new Error('Failed to fetch appointments');
                }

                const result = await response.json();

                if (result.success) {
                    setData(result.data);
                }
            } catch (error) {
                console.error('Error fetching today appointments:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchTodayAppointments();

        // Refresh every 5 minutes
        const interval = setInterval(fetchTodayAppointments, 5 * 60 * 1000);

        return () => clearInterval(interval);
    }, []);

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'CONFIRMED':
                return 'bg-green-100 text-green-800 border-green-200';
            case 'PENDING':
                return 'bg-yellow-100 text-yellow-800 border-yellow-200';
            case 'COMPLETED':
                return 'bg-blue-100 text-blue-800 border-blue-200';
            case 'CANCELLED':
                return 'bg-red-100 text-red-800 border-red-200';
            default:
                return 'bg-gray-100 text-gray-800 border-gray-200';
        }
    };

    const getStatusLabel = (status: string) => {
        switch (status) {
            case 'CONFIRMED':
                return 'Confirmada';
            case 'PENDING':
                return 'Pendiente';
            case 'COMPLETED':
                return 'Completada';
            case 'CANCELLED':
                return 'Cancelada';
            default:
                return status;
        }
    };

    if (loading) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Calendar className="h-5 w-5" />
                        Citas de Hoy
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex items-center justify-center h-40 text-muted-foreground">
                        Cargando citas...
                    </div>
                </CardContent>
            </Card>
        );
    }

    // If data is null, user is not a doctor
    if (!data) {
        return null;
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Calendar className="h-5 w-5" />
                        Citas de Hoy
                    </div>
                    <Badge variant="secondary" className="font-normal">
                        {data.count} {data.count === 1 ? 'cita' : 'citas'}
                    </Badge>
                </CardTitle>
            </CardHeader>
            <CardContent>
                {data.count === 0 ? (
                    <div className="flex flex-col items-center justify-center h-40 text-center text-muted-foreground">
                        <Calendar className="h-12 w-12 mb-2 opacity-20" />
                        <p className="font-medium">No hay citas programadas para hoy</p>
                        <p className="text-sm">Disfruta tu día libre</p>
                    </div>
                ) : (
                    <ScrollArea className="h-[400px] pr-4">
                        <div className="space-y-4">
                            {data.appointments.map((appointment, index) => (
                                <div key={appointment.appointment_id}>
                                    {index > 0 && <Separator className="my-4" />}
                                    <div className="space-y-3">
                                        <div className="flex items-start justify-between gap-4">
                                            <div className="space-y-1">
                                                <div className="flex items-center gap-2">
                                                    <Clock className="h-4 w-4 text-muted-foreground" />
                                                    <span className="font-semibold text-lg">
                                                        {format(new Date(appointment.start_time), 'HH:mm')}
                                                    </span>
                                                    <span className="text-muted-foreground">-</span>
                                                    <span className="text-muted-foreground">
                                                        {format(new Date(appointment.end_time), 'HH:mm')}
                                                    </span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <User className="h-4 w-4 text-muted-foreground" />
                                                    <span className="font-medium">{appointment.patient_name}</span>
                                                </div>
                                            </div>
                                            <Badge
                                                variant="outline"
                                                className={`${getStatusColor(appointment.status)} border-0 px-2 py-0.5`}
                                            >
                                                {getStatusLabel(appointment.status)}
                                            </Badge>
                                        </div>

                                        {appointment.reason && (
                                            <div className="flex items-start gap-2 pl-6">
                                                <FileText className="h-4 w-4 text-muted-foreground mt-0.5" />
                                                <p className="text-sm text-muted-foreground">{appointment.reason}</p>
                                            </div>
                                        )}

                                        {appointment.patient_phone && (
                                            <div className="flex items-center gap-2 pl-6">
                                                <Phone className="h-4 w-4 text-muted-foreground" />
                                                <a
                                                    href={`tel:${appointment.patient_phone}`}
                                                    className="text-sm text-primary hover:underline"
                                                >
                                                    {appointment.patient_phone}
                                                </a>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </ScrollArea>
                )}
            </CardContent>
        </Card>
    );
}
