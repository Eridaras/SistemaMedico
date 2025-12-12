import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { appointments, patients } from "@/lib/data";
import { Cake, Phone, Mail, MapPin, Pill, AlertTriangle, Stethoscope } from "lucide-react";
import { notFound } from "next/navigation";

export default function PatientDetailPage({ params }: { params: { id: string } }) {
  const patient = patients.find(p => p.id === params.id);
  
  if (!patient) {
    notFound();
  }

  const patientAppointments = appointments.filter(a => a.patientId === patient.id);

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader className="flex flex-col md:flex-row md:items-start md:gap-6">
          <Avatar className="h-24 w-24 border">
            <AvatarImage src={patient.avatarUrl} alt={patient.name} data-ai-hint="person portrait"/>
            <AvatarFallback>{patient.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
          </Avatar>
          <div className="flex-1 mt-4 md:mt-0">
            <CardTitle className="text-3xl">{patient.name}</CardTitle>
            <CardDescription className="mt-2 grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 text-sm">
              <span className="flex items-center gap-2"><Cake className="h-4 w-4 text-muted-foreground" /> Born on {patient.dob}</span>
              <span className="flex items-center gap-2"><Phone className="h-4 w-4 text-muted-foreground" /> {patient.contact}</span>
              <span className="flex items-center gap-2"><Mail className="h-4 w-4 text-muted-foreground" /> {patient.email}</span>
              <span className="flex items-center gap-2"><MapPin className="h-4 w-4 text-muted-foreground" /> {patient.address}</span>
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
                  {patientAppointments.map(app => (
                    <TableRow key={app.id}>
                      <TableCell>{app.date}</TableCell>
                      <TableCell className="hidden sm:table-cell">{app.time}</TableCell>
                      <TableCell>{app.reason}</TableCell>
                      <TableCell className="text-right"><Badge variant={app.status === 'Completed' ? 'default' : 'secondary'}>{app.status}</Badge></TableCell>
                    </TableRow>
                  ))}
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
                  {patient.medicalHistory.medications.map(med => (
                     <TableRow key={med.id}>
                      <TableCell className="font-medium">{med.name}</TableCell>
                      <TableCell>{med.dosage}</TableCell>
                      <TableCell>{med.frequency}</TableCell>
                      <TableCell className="text-right">{med.prescribed}</TableCell>
                    </TableRow>
                  ))}
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
                {patient.medicalHistory.allergies[0] === 'None' ? (
                     <p className="text-muted-foreground">No known allergies.</p>
                ) : patient.medicalHistory.allergies.map(allergy => (
                    <Badge variant="destructive" key={allergy} className="mr-2 text-sm"><AlertTriangle className="mr-1 h-3 w-3" />{allergy}</Badge>
                ))}
            </CardContent>
          </Card>
        </TabsContent>
         <TabsContent value="diagnoses">
           <Card>
            <CardHeader>
              <CardTitle>Medical Conditions / Diagnoses</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
                {patient.medicalHistory.conditions.map(condition => (
                    <Badge variant="outline" key={condition} className="mr-2 text-sm"><Stethoscope className="mr-1 h-3 w-3" />{condition}</Badge>
                ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
