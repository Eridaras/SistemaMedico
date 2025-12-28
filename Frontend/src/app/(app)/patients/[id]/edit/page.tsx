"use client";

import * as React from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageTransition } from "@/components/page-transition";
import { auth } from "@/lib/auth";
import { useToast } from "@/hooks/use-toast";
import { Loader2, ArrowLeft, Save } from "lucide-react";
import Link from "next/link";

interface Patient {
  patient_id: number;
  first_name: string;
  last_name: string;
  doc_number: string;
  phone: string;
  email: string;
  birth_date: string;
  gender: string;
  address: string;
  city: string;
  emergency_contact: string;
  emergency_phone: string;
  blood_type: string;
}

export default function EditPatientPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const patientId = params.id as string;

  const [loading, setLoading] = React.useState(true);
  const [saving, setSaving] = React.useState(false);
  const [patient, setPatient] = React.useState<Patient | null>(null);

  const [formData, setFormData] = React.useState({
    first_name: "",
    last_name: "",
    doc_number: "",
    phone: "",
    email: "",
    birth_date: "",
    gender: "",
    address: "",
    city: "",
    emergency_contact: "",
    emergency_phone: "",
    blood_type: "",
  });

  React.useEffect(() => {
    const fetchPatient = async () => {
      try {
        const response = await fetch(`/api/historia-clinica/patients/${patientId}`, {
          headers: {
            'Authorization': `Bearer ${auth.getToken()}`
          }
        });

        if (!response.ok) throw new Error("Error al cargar paciente");

        const data = await response.json();
        if (data.success && data.data) {
          const patientData = data.data.patient;
          setPatient(patientData);
          setFormData({
            first_name: patientData.first_name || "",
            last_name: patientData.last_name || "",
            doc_number: patientData.doc_number || "",
            phone: patientData.phone || "",
            email: patientData.email || "",
            birth_date: patientData.birth_date ? patientData.birth_date.split('T')[0] : "",
            gender: patientData.gender || "",
            address: patientData.address || "",
            city: patientData.city || "",
            emergency_contact: patientData.emergency_contact || "",
            emergency_phone: patientData.emergency_phone || "",
            blood_type: patientData.blood_type || "",
          });
        }
      } catch (error) {
        console.error(error);
        toast({
          title: "Error",
          description: "No se pudo cargar la información del paciente",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchPatient();
  }, [patientId, toast]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validaciones
    if (!formData.first_name || !formData.last_name || !formData.doc_number) {
      toast({
        title: "Error",
        description: "Nombre, apellido y cédula son obligatorios",
        variant: "destructive",
      });
      return;
    }

    try {
      setSaving(true);

      const response = await fetch(`/api/historia-clinica/patients/${patientId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${auth.getToken()}`
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (data.success) {
        toast({
          title: "Éxito",
          description: "Paciente actualizado correctamente",
        });
        router.push(`/patients/${patientId}`);
      } else {
        throw new Error(data.message || 'Error al actualizar paciente');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "No se pudo actualizar el paciente",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  if (loading) {
    return (
      <PageTransition className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>Cargando paciente...</span>
        </div>
      </PageTransition>
    );
  }

  if (!patient) {
    return (
      <PageTransition className="flex flex-col items-center justify-center min-h-[400px] gap-4">
        <p className="text-muted-foreground">Paciente no encontrado</p>
        <Link href="/patients">
          <Button variant="outline">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver al listado
          </Button>
        </Link>
      </PageTransition>
    );
  }

  return (
    <PageTransition className="flex flex-col gap-6 w-full max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/patients">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Editar Paciente</h1>
          <p className="text-muted-foreground">
            {patient.first_name} {patient.last_name}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>Información del Paciente</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Información Personal */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="first_name">Nombres *</Label>
                <Input
                  id="first_name"
                  value={formData.first_name}
                  onChange={(e) => handleChange('first_name', e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="last_name">Apellidos *</Label>
                <Input
                  id="last_name"
                  value={formData.last_name}
                  onChange={(e) => handleChange('last_name', e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="doc_number">Cédula de Identidad *</Label>
                <Input
                  id="doc_number"
                  value={formData.doc_number}
                  onChange={(e) => handleChange('doc_number', e.target.value)}
                  required
                  maxLength={10}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="birth_date">Fecha de Nacimiento</Label>
                <Input
                  id="birth_date"
                  type="date"
                  value={formData.birth_date}
                  onChange={(e) => handleChange('birth_date', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="gender">Género</Label>
                <select
                  id="gender"
                  value={formData.gender}
                  onChange={(e) => handleChange('gender', e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <option value="">Seleccionar...</option>
                  <option value="M">Masculino</option>
                  <option value="F">Femenino</option>
                  <option value="O">Otro</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="blood_type">Tipo de Sangre</Label>
                <select
                  id="blood_type"
                  value={formData.blood_type}
                  onChange={(e) => handleChange('blood_type', e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <option value="">Seleccionar...</option>
                  <option value="A+">A+</option>
                  <option value="A-">A-</option>
                  <option value="B+">B+</option>
                  <option value="B-">B-</option>
                  <option value="AB+">AB+</option>
                  <option value="AB-">AB-</option>
                  <option value="O+">O+</option>
                  <option value="O-">O-</option>
                </select>
              </div>
            </div>

            {/* Contacto */}
            <div className="pt-4 border-t">
              <h3 className="text-lg font-semibold mb-4">Información de Contacto</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="phone">Teléfono</Label>
                  <Input
                    id="phone"
                    value={formData.phone}
                    onChange={(e) => handleChange('phone', e.target.value)}
                    maxLength={10}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleChange('email', e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="city">Ciudad</Label>
                  <Input
                    id="city"
                    value={formData.city}
                    onChange={(e) => handleChange('city', e.target.value)}
                  />
                </div>

                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="address">Dirección</Label>
                  <Input
                    id="address"
                    value={formData.address}
                    onChange={(e) => handleChange('address', e.target.value)}
                  />
                </div>
              </div>
            </div>

            {/* Contacto de Emergencia */}
            <div className="pt-4 border-t">
              <h3 className="text-lg font-semibold mb-4">Contacto de Emergencia</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="emergency_contact">Nombre del Contacto</Label>
                  <Input
                    id="emergency_contact"
                    value={formData.emergency_contact}
                    onChange={(e) => handleChange('emergency_contact', e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="emergency_phone">Teléfono de Emergencia</Label>
                  <Input
                    id="emergency_phone"
                    value={formData.emergency_phone}
                    onChange={(e) => handleChange('emergency_phone', e.target.value)}
                    maxLength={10}
                  />
                </div>
              </div>
            </div>

            {/* Botones de Acción */}
            <div className="flex gap-3 pt-4 border-t">
              <Link href={`/patients/${patientId}`} className="flex-1">
                <Button type="button" variant="outline" className="w-full" disabled={saving}>
                  Cancelar
                </Button>
              </Link>
              <Button type="submit" className="flex-1 gap-2" disabled={saving}>
                {saving ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Guardando...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4" />
                    Guardar Cambios
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </PageTransition>
  );
}
