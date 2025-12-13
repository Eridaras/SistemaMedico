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
  FileText
} from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { PageTransition } from "@/components/page-transition";

// Mock data matching the design
const patientsData = [
  { id: 1, name: "Carlos Ramirez", cedula: "1712345678", phone: "0998765432", lastVisit: "2023-10-15" },
  { id: 2, name: "Sofia Vega", cedula: "0987654321", phone: "0987123456", lastVisit: "2023-10-12" },
  { id: 3, name: "Juan Martinez", cedula: "1809876543", phone: "0976543210", lastVisit: "2023-10-11" },
  { id: 4, name: "Lucia Fernandez", cedula: "0123456789", phone: "0965432109", lastVisit: "2023-10-09" },
  { id: 5, name: "Mateo Castillo", cedula: "1098765432", phone: "0954321098", lastVisit: "2023-10-05" },
];

export default function PatientsPage() {
  const [searchTerm, setSearchTerm] = React.useState("");

  const filteredPatients = patientsData.filter(patient =>
    patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.cedula.includes(searchTerm)
  );

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
          <Button className="w-full md:w-auto gap-2 bg-primary hover:bg-primary/90">
            <Plus className="h-4 w-4" />
            Agregar Paciente
          </Button>
        </div>

        {/* Patients Table */}
        <div className="rounded-lg border border-border overflow-hidden">
          <Table>
            <TableHeader className="bg-muted/50">
              <TableRow>
                <TableHead className="w-[30%]">Nombre Completo</TableHead>
                <TableHead>Cédula de Identidad</TableHead>
                <TableHead>Teléfono</TableHead>
                <TableHead>Última Cita</TableHead>
                <TableHead className="text-right">Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredPatients.map((patient) => (
                <TableRow key={patient.id} className="hover:bg-muted/30 transition-colors">
                  <TableCell className="font-medium">
                    <div className="flex items-center gap-3">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="bg-primary/10 text-primary text-xs">
                          {patient.name.split(' ').map(n => n[0]).join('').substring(0, 2)}
                        </AvatarFallback>
                      </Avatar>
                      {patient.name}
                    </div>
                  </TableCell>
                  <TableCell className="text-muted-foreground">{patient.cedula}</TableCell>
                  <TableCell className="text-muted-foreground">{patient.phone}</TableCell>
                  <TableCell>
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400">
                      {patient.lastVisit}
                    </span>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-primary">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-primary">
                        <CalendarPlus className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-primary">
                        <FileText className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>
    </PageTransition>
  );
}
