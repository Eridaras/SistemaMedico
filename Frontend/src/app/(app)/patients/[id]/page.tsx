"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Cake, Phone, Mail, MapPin, Pill, AlertTriangle, Stethoscope } from "lucide-react";
import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/components/auth-provider";

interface PatientDetail {
  patient_id: number;
  doc_type: string;
  doc_number: string;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  address?: string;
  birth_date?: string;
  gender?: string;
  medical_history?: {
    allergies?: string[];
    pathologies?: string[];
    medications?: Array<{
      medication_id: number;
      name: string;
      dosage: string;
      frequency: string;
      prescribed_date: string;
    }>;
  };
  appointments?: Array<{
    appointment_id: number;
    start_time: string;
    end_time: string;
    reason: string;
    status: string;
  }>;
}

export default function PatientDetailPage({ params }: { params: { id: string } }) {
  const [patient, setPatient] = useState<PatientDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const auth = useAuth();

  const fetchPatient = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/historia-clinica/patients/${params.id}`, {
        headers: {
          'Authorization': `Bearer ${auth.getToken()}`
        }
      });

      const data = await response.json();

      if (data.success && data.data) {
        setPatient(data.data);
        setError(null);
      } else {
        setError(data.message || 'Failed to load patient');
      }
    } catch (err) {
      setError('Error loading patient details');
      console.error('Fetch patient error:', err);
    } finally {
      setLoading(false);
    }
  }, [params.id, auth]);

  useEffect(() => {
    fetchPatient();
  }, [fetchPatient]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <p className="text-muted-foreground">Loading patient details...</p>
      </div>
    );
  }

  if (error || !patient) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <p className="text-destructive">{error || 'Patient not found'}</p>
      </div>
    );
  }

  const fullName = `${patient.first_name} ${patient.last_name}`;
  const allergies = patient.medical_history?.allergies || [];
  const conditions = patient.medical_history?.pathologies || [];
  const medications = patient.medical_history?.medications || [];
  const patientAppointments = patient.appointments || [];

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader className="flex flex-col md:flex-row md:items-start md:gap-6">
          <Avatar className="h-24 w-24 border">
            <AvatarFallback>{patient.first_name[0]}{patient.last_name[0]}</AvatarFallback>
          </Avatar>
          <div className="flex-1 mt-4 md:mt-0">
            <CardTitle className="text-3xl">{fullName}</CardTitle>
            <CardDescription className="mt-2 grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 text-sm">
              <span className="flex items-center gap-2"><Cake className="h-4 w-4 text-muted-foreground" /> {patient.birth_date ? `Born on ${patient.birth_date}` : 'Birth date not available'}</span>
              <span className="flex items-center gap-2"><Phone className="h-4 w-4 text-muted-foreground" /> {patient.phone || 'No phone'}</span>
              <span className="flex items-center gap-2"><Mail className="h-4 w-4 text-muted-foreground" /> {patient.email || 'No email'}</span>
              <span className="flex items-center gap-2"><MapPin className="h-4 w-4 text-muted-foreground" /> {patient.address || 'No address'}</span>
            </CardDescription>
          </div>
        </CardHeader>
      </Card>

      <Tabs defaultValue="appointments" className="w-full">
        <TabsList className="grid w-full grid-cols-2 md:grid-cols-4">
          <TabsTrigger value="appointments">Appointments</TabsTrigger>
          <TabsTrigger value="medications">Medications</TabsTrigger>
          <TabsTrigger value="allergies">Allergies</TabsTrigger>
          <TabsTrigger value="diagnoses">Diagnoses</TabsTrigger>
        </TabsList>
        <TabsContent value="appointments">
          <Card>
            <CardHeader>
              <CardTitle>Appointment History</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead className="hidden sm:table-cell">Time</TableHead>
                    <TableHead>Reason</TableHead>
                    <TableHead className="text-right">Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {patientAppointments.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={4} className="text-center text-muted-foreground">
                        No appointments found
                      </TableCell>
                    </TableRow>
                  ) : (
                    patientAppointments.map(app => {
                      const startDate = new Date(app.start_time);
                      const endDate = new Date(app.end_time);
                      return (
                        <TableRow key={app.appointment_id}>
                          <TableCell>{startDate.toLocaleDateString()}</TableCell>
                          <TableCell className="hidden sm:table-cell">
                            {startDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - {endDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </TableCell>
                          <TableCell>{app.reason}</TableCell>
                          <TableCell className="text-right">
                            <Badge variant={app.status === 'COMPLETED' ? 'default' : 'secondary'}>{app.status}</Badge>
                          </TableCell>
                        </TableRow>
                      );
                    })
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="medications">
           <Card>
            <CardHeader>
              <CardTitle>Current Medications</CardTitle>
            </CardHeader>
            <CardContent>
               <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead><Pill className="inline-block mr-2 h-4 w-4" />Name</TableHead>
                    <TableHead>Dosage</TableHead>
                    <TableHead>Frequency</TableHead>
                    <TableHead className="text-right">Prescribed On</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {medications.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={4} className="text-center text-muted-foreground">
                        No medications found
                      </TableCell>
                    </TableRow>
                  ) : (
                    medications.map(med => (
                      <TableRow key={med.medication_id}>
                        <TableCell className="font-medium">{med.name}</TableCell>
                        <TableCell>{med.dosage}</TableCell>
                        <TableCell>{med.frequency}</TableCell>
                        <TableCell className="text-right">{new Date(med.prescribed_date).toLocaleDateString()}</TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="allergies">
           <Card>
            <CardHeader>
              <CardTitle>Allergies</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
                {allergies.length === 0 ? (
                  <p className="text-muted-foreground">No known allergies.</p>
                ) : (
                  allergies.map((allergy, index) => (
                    <Badge variant="destructive" key={index} className="mr-2 text-sm">
                      <AlertTriangle className="mr-1 h-3 w-3" />{allergy}
                    </Badge>
                  ))
                )}
            </CardContent>
          </Card>
        </TabsContent>
         <TabsContent value="diagnoses">
           <Card>
            <CardHeader>
              <CardTitle>Medical Conditions / Diagnoses</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
                {conditions.length === 0 ? (
                  <p className="text-muted-foreground">No known medical conditions.</p>
                ) : (
                  conditions.map((condition, index) => (
                    <Badge variant="outline" key={index} className="mr-2 text-sm">
                      <Stethoscope className="mr-1 h-3 w-3" />{condition}
                    </Badge>
                  ))
                )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
