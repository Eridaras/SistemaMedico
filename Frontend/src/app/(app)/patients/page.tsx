"use client";

import * as React from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Search,
  Plus,
  Edit,
  CalendarPlus,
  FileText,
  Loader2
} from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { PageTransition } from "@/components/page-transition";
import { auth } from "@/lib/auth";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface Patient {
  patient_id: number;
  first_name: string;
  last_name: string;
  doc_number: string;
  phone: string;
  email: string;
  created_at?: string;
}

export default function PatientsPage() {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = React.useState("");
  const [patients, setPatients] = React.useState<Patient[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState("");

  const fetchPatients = React.useCallback(async (search: string = "") => {
    try {
      setLoading(true);
      const query = search ? `?search=${encodeURIComponent(search)}` : "";
      const response = await fetch(`/api/historia-clinica/patients${query}`, {
        headers: {
          'Authorization': `Bearer ${auth.getToken()}`
        }
      });

      if (!response.ok) throw new Error("Error al cargar pacientes");

      const data = await response.json();
      if (data.success && data.data && data.data.patients) {
        setPatients(data.data.patients);
      } else {
        setPatients([]);
      }
    } catch (err) {
      console.error(err);
      setError("No se pudieron cargar los pacientes");
    } finally {
      setLoading(false);
    }
  }, []);

  // Debounce search
  React.useEffect(() => {
    const timer = setTimeout(() => {
      fetchPatients(searchTerm);
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm, fetchPatients]);

  return (
    <PageTransition className="flex flex-col gap-6 w-full max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Listado de Pacientes</h1>
      </div>

      <div className="bg-card rounded-xl border border-border shadow-sm p-6">
        {/* Search and Action Bar */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 mb-6">
          <div className="w-full md:max-w-md relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar por nombre o cédula..."
              className="pl-9 bg-muted/50 border-0 focus-visible:ring-1"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <Link href="/patients/new">
            <Button className="w-full md:w-auto gap-2 bg-primary hover:bg-primary/90">
              <Plus className="h-4 w-4" />
              Agregar Paciente
            </Button>
          </Link>
        </div>

        {/* Patients Table */}
        <div className="rounded-lg border border-border overflow-hidden bg-background">
          <Table>
            <TableHeader className="bg-muted/50">
              <TableRow>
                <TableHead className="w-[30%]">Nombre Completo</TableHead>
                <TableHead>Cédula de Identidad</TableHead>
                <TableHead>Teléfono</TableHead>
                <TableHead>Email</TableHead>
                <TableHead className="text-right">Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} className="h-24 text-center">
                    <div className="flex justify-center items-center gap-2 text-muted-foreground">
                      <Loader2 className="h-4 w-4 animate-spin" /> Cargando pacientes...
                    </div>
                  </TableCell>
                </TableRow>
              ) : patients.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="h-24 text-center text-muted-foreground">
                    No se encontraron pacientes
                  </TableCell>
                </TableRow>
              ) : (
                patients.map((patient) => (
                  <TableRow key={patient.patient_id} className="hover:bg-muted/30 transition-colors">
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-3">
                        <Avatar className="h-8 w-8">
                          <AvatarFallback className="bg-primary/10 text-primary text-xs">
                            {patient.first_name[0]}{patient.last_name[0]}
                          </AvatarFallback>
                        </Avatar>
                        {patient.first_name} {patient.last_name}
                      </div>
                    </TableCell>
                    <TableCell className="text-muted-foreground font-mono text-xs">{patient.doc_number}</TableCell>
                    <TableCell className="text-muted-foreground">{patient.phone}</TableCell>
                    <TableCell className="text-muted-foreground text-sm">{patient.email}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Link href={`/patients/${patient.patient_id}/edit`}>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-muted-foreground hover:text-primary"
                            title="Editar paciente"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                        </Link>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-muted-foreground hover:text-primary"
                          title="Agendar cita"
                          onClick={() => router.push(`/appointments?patient_id=${patient.patient_id}&patient_name=${encodeURIComponent(patient.first_name + ' ' + patient.last_name)}`)}
                        >
                          <CalendarPlus className="h-4 w-4" />
                        </Button>
                        <Link href={`/patients/${patient.patient_id}`}>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-muted-foreground hover:text-primary"
                            title="Ver historia clínica"
                          >
                            <FileText className="h-4 w-4" />
                          </Button>
                        </Link>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>
    </PageTransition>
  );
}
