"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { PageTransition } from "@/components/page-transition";
import { auth } from "@/lib/auth";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Save, Mail, MessageCircle, Clock, Bell, Info } from "lucide-react";

interface ReminderSettings {
  email_enabled: boolean;
  email_hours_before: number[];
  whatsapp_enabled: boolean;
  whatsapp_hours_before: number[];
  auto_send_enabled: boolean;
  send_on_days: string[];
  quiet_hours_start: string;
  quiet_hours_end: string;
  smtp_host?: string;
  smtp_port?: number;
  smtp_user?: string;
  from_email?: string;
  from_name?: string;
  twilio_account_sid?: string;
  twilio_whatsapp_number?: string;
}

const DAYS_OF_WEEK = [
  { value: 'mon', label: 'Lun' },
  { value: 'tue', label: 'Mar' },
  { value: 'wed', label: 'Mié' },
  { value: 'thu', label: 'Jue' },
  { value: 'fri', label: 'Vie' },
  { value: 'sat', label: 'Sáb' },
  { value: 'sun', label: 'Dom' },
];

const PRESET_HOURS = [
  { value: 1, label: '1 hora antes' },
  { value: 3, label: '3 horas antes' },
  { value: 6, label: '6 horas antes' },
  { value: 12, label: '12 horas antes' },
  { value: 24, label: '1 día antes' },
  { value: 48, label: '2 días antes' },
  { value: 72, label: '3 días antes' },
];

export default function SettingsPage() {
  const { toast } = useToast();
  const [loading, setLoading] = React.useState(true);
  const [saving, setSaving] = React.useState(false);

  const [settings, setSettings] = React.useState<ReminderSettings>({
    email_enabled: true,
    email_hours_before: [24, 3],
    whatsapp_enabled: false,
    whatsapp_hours_before: [24],
    auto_send_enabled: true,
    send_on_days: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
    quiet_hours_start: '22:00:00',
    quiet_hours_end: '08:00:00',
  });

  React.useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await fetch('/api/notifications/reminder-settings', {
        headers: {
          'Authorization': `Bearer ${auth.getToken()}`
        }
      });

      if (!response.ok) throw new Error("Error al cargar configuración");

      const data = await response.json();
      if (data.success && data.data) {
        setSettings(data.data);
      }
    } catch (error) {
      console.error(error);
      toast({
        title: "Error",
        description: "No se pudo cargar la configuración",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);

      const response = await fetch('/api/notifications/reminder-settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${auth.getToken()}`
        },
        body: JSON.stringify(settings)
      });

      const data = await response.json();

      if (data.success) {
        toast({
          title: "Éxito",
          description: "Configuración guardada correctamente",
        });
      } else {
        throw new Error(data.message || 'Error al guardar');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "No se pudo guardar la configuración",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const toggleDay = (day: string) => {
    setSettings(prev => {
      const days = prev.send_on_days.includes(day)
        ? prev.send_on_days.filter(d => d !== day)
        : [...prev.send_on_days, day];
      return { ...prev, send_on_days: days };
    });
  };

  const toggleEmailHour = (hour: number) => {
    setSettings(prev => {
      const hours = prev.email_hours_before.includes(hour)
        ? prev.email_hours_before.filter(h => h !== hour)
        : [...prev.email_hours_before, hour].sort((a, b) => b - a);
      return { ...prev, email_hours_before: hours };
    });
  };

  const toggleWhatsAppHour = (hour: number) => {
    setSettings(prev => {
      const hours = prev.whatsapp_hours_before.includes(hour)
        ? prev.whatsapp_hours_before.filter(h => h !== hour)
        : [...prev.whatsapp_hours_before, hour].sort((a, b) => b - a);
      return { ...prev, whatsapp_hours_before: hours };
    });
  };

  if (loading) {
    return (
      <PageTransition className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>Cargando configuración...</span>
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition className="flex flex-col gap-6 w-full max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Configuración de Recordatorios</h1>
        <p className="text-muted-foreground mt-1">
          Configure cómo y cuándo se envían los recordatorios de citas a sus pacientes
        </p>
      </div>

      {/* General Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Configuración General
          </CardTitle>
          <CardDescription>
            Active o desactive el envío automático de recordatorios
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="auto_send">Envío Automático</Label>
              <p className="text-sm text-muted-foreground">
                Los recordatorios se enviarán automáticamente según la configuración
              </p>
            </div>
            <Switch
              id="auto_send"
              checked={settings.auto_send_enabled}
              onCheckedChange={(checked) => setSettings(prev => ({ ...prev, auto_send_enabled: checked }))}
            />
          </div>

          <Separator />

          <div className="space-y-3">
            <Label>Días de Envío</Label>
            <p className="text-sm text-muted-foreground">
              Seleccione los días en los que se enviarán recordatorios
            </p>
            <div className="flex gap-2">
              {DAYS_OF_WEEK.map(day => (
                <Button
                  key={day.value}
                  variant={settings.send_on_days.includes(day.value) ? "default" : "outline"}
                  size="sm"
                  onClick={() => toggleDay(day.value)}
                >
                  {day.label}
                </Button>
              ))}
            </div>
          </div>

          <Separator />

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="quiet_start">Hora Silenciosa Inicio</Label>
              <p className="text-sm text-muted-foreground mb-2">
                No enviar desde esta hora
              </p>
              <Input
                id="quiet_start"
                type="time"
                value={settings.quiet_hours_start?.slice(0, 5) || '22:00'}
                onChange={(e) => setSettings(prev => ({ ...prev, quiet_hours_start: e.target.value + ':00' }))}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="quiet_end">Hora Silenciosa Fin</Label>
              <p className="text-sm text-muted-foreground mb-2">
                No enviar hasta esta hora
              </p>
              <Input
                id="quiet_end"
                type="time"
                value={settings.quiet_hours_end?.slice(0, 5) || '08:00'}
                onChange={(e) => setSettings(prev => ({ ...prev, quiet_hours_end: e.target.value + ':00' }))}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Email Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mail className="h-5 w-5" />
            Recordatorios por Email
          </CardTitle>
          <CardDescription>
            Configure los recordatorios enviados por correo electrónico
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="email_enabled">Habilitar Emails</Label>
              <p className="text-sm text-muted-foreground">
                Enviar recordatorios por correo electrónico
              </p>
            </div>
            <Switch
              id="email_enabled"
              checked={settings.email_enabled}
              onCheckedChange={(checked) => setSettings(prev => ({ ...prev, email_enabled: checked }))}
            />
          </div>

          {settings.email_enabled && (
            <>
              <Separator />
              <div className="space-y-3">
                <Label className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  Cuándo Enviar
                </Label>
                <p className="text-sm text-muted-foreground">
                  Seleccione cuántas horas antes de la cita enviar el recordatorio
                </p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {PRESET_HOURS.map(hour => (
                    <Button
                      key={hour.value}
                      variant={settings.email_hours_before.includes(hour.value) ? "default" : "outline"}
                      size="sm"
                      onClick={() => toggleEmailHour(hour.value)}
                      className="justify-start"
                    >
                      {hour.label}
                    </Button>
                  ))}
                </div>
                {settings.email_hours_before.length > 0 && (
                  <div className="flex items-center gap-2 p-3 bg-blue-50 dark:bg-blue-950 rounded-md">
                    <Info className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                    <p className="text-sm text-blue-600 dark:text-blue-400">
                      Se enviarán {settings.email_hours_before.length} recordatorio(s) por email
                    </p>
                  </div>
                )}
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* WhatsApp Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageCircle className="h-5 w-5" />
            Recordatorios por WhatsApp
          </CardTitle>
          <CardDescription>
            Configure los recordatorios enviados por WhatsApp (requiere configuración Twilio)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="whatsapp_enabled">Habilitar WhatsApp</Label>
              <p className="text-sm text-muted-foreground">
                Enviar recordatorios por WhatsApp
              </p>
            </div>
            <Switch
              id="whatsapp_enabled"
              checked={settings.whatsapp_enabled}
              onCheckedChange={(checked) => setSettings(prev => ({ ...prev, whatsapp_enabled: checked }))}
            />
          </div>

          {settings.whatsapp_enabled && (
            <>
              <Separator />
              <div className="space-y-3">
                <Label className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  Cuándo Enviar
                </Label>
                <p className="text-sm text-muted-foreground">
                  Seleccione cuántas horas antes de la cita enviar el recordatorio
                </p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {PRESET_HOURS.map(hour => (
                    <Button
                      key={hour.value}
                      variant={settings.whatsapp_hours_before.includes(hour.value) ? "default" : "outline"}
                      size="sm"
                      onClick={() => toggleWhatsAppHour(hour.value)}
                      className="justify-start"
                    >
                      {hour.label}
                    </Button>
                  ))}
                </div>
                {settings.whatsapp_hours_before.length > 0 && (
                  <div className="flex items-center gap-2 p-3 bg-green-50 dark:bg-green-950 rounded-md">
                    <Info className="h-4 w-4 text-green-600 dark:text-green-400" />
                    <p className="text-sm text-green-600 dark:text-green-400">
                      Se enviarán {settings.whatsapp_hours_before.length} recordatorio(s) por WhatsApp
                    </p>
                  </div>
                )}
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end gap-3">
        <Button
          onClick={handleSave}
          disabled={saving}
          size="lg"
          className="gap-2"
        >
          {saving ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Guardando...
            </>
          ) : (
            <>
              <Save className="h-4 w-4" />
              Guardar Configuración
            </>
          )}
        </Button>
      </div>
    </PageTransition>
  );
}
