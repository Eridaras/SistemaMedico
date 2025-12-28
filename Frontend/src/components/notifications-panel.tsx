"use client";

import * as React from "react";
import { Bell, X, Check, AlertTriangle, Calendar, Package } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { auth } from "@/lib/auth";
import { format } from "date-fns";
import { es } from "date-fns/locale";

interface Notification {
    log_id: number;
    notification_type: string;
    title: string;
    message: string;
    sent_at: string;
    read_at: string | null;
    metadata: any;
}

export function NotificationsPanel() {
    const [notifications, setNotifications] = React.useState<Notification[]>([]);
    const [unreadCount, setUnreadCount] = React.useState(0);
    const [loading, setLoading] = React.useState(true);
    const [open, setOpen] = React.useState(false);

    const fetchNotifications = React.useCallback(async () => {
        try {
            const response = await fetch('/api/notifications/notifications?limit=20', {
                headers: {
                    'Authorization': `Bearer ${auth.getToken()}`
                }
            });

            if (!response.ok) throw new Error('Failed to fetch notifications');

            const data = await response.json();

            if (data.success) {
                setNotifications(data.data.notifications || []);
                setUnreadCount(data.data.unread_count || 0);
            }
        } catch (error) {
            console.error('Error fetching notifications:', error);
        } finally {
            setLoading(false);
        }
    }, []);

    React.useEffect(() => {
        fetchNotifications();

        // Poll for new notifications every 60 seconds
        const interval = setInterval(fetchNotifications, 60000);

        return () => clearInterval(interval);
    }, [fetchNotifications]);

    const markAsRead = async (logId: number) => {
        try {
            const response = await fetch(`/api/notifications/notifications/${logId}/read`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${auth.getToken()}`
                }
            });

            if (!response.ok) throw new Error('Failed to mark as read');

            // Refresh notifications
            fetchNotifications();
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    };

    const getNotificationIcon = (type: string) => {
        switch (type) {
            case 'low_stock':
                return <Package className="h-4 w-4 text-orange-500" />;
            case 'appointment_reminder':
                return <Calendar className="h-4 w-4 text-blue-500" />;
            case 'daily_summary':
                return <Bell className="h-4 w-4 text-purple-500" />;
            default:
                return <AlertTriangle className="h-4 w-4 text-gray-500" />;
        }
    };

    return (
        <Popover open={open} onOpenChange={setOpen}>
            <PopoverTrigger asChild>
                <Button variant="ghost" size="icon" className="relative">
                    <Bell className="h-5 w-5" />
                    {unreadCount > 0 && (
                        <Badge
                            variant="destructive"
                            className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs"
                        >
                            {unreadCount > 9 ? '9+' : unreadCount}
                        </Badge>
                    )}
                </Button>
            </PopoverTrigger>
            <PopoverContent className="w-96 p-0" align="end">
                <div className="flex items-center justify-between p-4 border-b">
                    <h3 className="font-semibold">Notificaciones</h3>
                    {unreadCount > 0 && (
                        <Badge variant="secondary">{unreadCount} nuevas</Badge>
                    )}
                </div>

                <ScrollArea className="h-[400px]">
                    {loading ? (
                        <div className="p-4 text-center text-muted-foreground">
                            Cargando notificaciones...
                        </div>
                    ) : notifications.length === 0 ? (
                        <div className="p-8 text-center text-muted-foreground">
                            <Bell className="h-12 w-12 mx-auto mb-2 opacity-20" />
                            <p>No hay notificaciones</p>
                        </div>
                    ) : (
                        <div className="divide-y">
                            {notifications.map((notification) => (
                                <div
                                    key={notification.log_id}
                                    className={`p-4 hover:bg-muted/30 transition-colors ${
                                        !notification.read_at ? 'bg-blue-50/50 dark:bg-blue-950/20' : ''
                                    }`}
                                >
                                    <div className="flex items-start gap-3">
                                        <div className="mt-0.5">
                                            {getNotificationIcon(notification.notification_type)}
                                        </div>
                                        <div className="flex-1 space-y-1">
                                            <div className="flex items-start justify-between gap-2">
                                                <p className="text-sm font-medium leading-none">
                                                    {notification.title}
                                                </p>
                                                {!notification.read_at && (
                                                    <Button
                                                        variant="ghost"
                                                        size="icon"
                                                        className="h-6 w-6 shrink-0"
                                                        onClick={() => markAsRead(notification.log_id)}
                                                        title="Marcar como leída"
                                                    >
                                                        <Check className="h-3 w-3" />
                                                    </Button>
                                                )}
                                            </div>
                                            <p className="text-xs text-muted-foreground whitespace-pre-wrap line-clamp-3">
                                                {notification.message}
                                            </p>
                                            <p className="text-xs text-muted-foreground">
                                                {format(new Date(notification.sent_at), "PPp", { locale: es })}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </ScrollArea>
            </PopoverContent>
        </Popover>
    );
}
