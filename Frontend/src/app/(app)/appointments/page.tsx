"use client"

import * as React from "react"
import { format } from "date-fns"
import { PlusCircle } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { appointments, patients, doctors } from "@/lib/data"
import type { Appointment } from "@/lib/data"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"

export default function AppointmentsPage() {
  const [date, setDate] = React.useState<Date | undefined>(new Date())
  const [dailyAppointments, setDailyAppointments] = React.useState<Appointment[]>([])

  React.useEffect(() => {
    if (date) {
      const filtered = appointments.filter(
        (a) => new Date(a.date).toDateString() === date.toDateString()
      );
      setDailyAppointments(filtered);
    }
  }, [date])
  
  const getPatient = (id: string) => patients.find(p => p.id === id);
  const getDoctor = (id: string) => doctors.find(d => d.id === id);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-1">
        <Card>
            <CardHeader>
                <CardTitle>Schedule</CardTitle>
                <CardDescription>Select a day to view appointments.</CardDescription>
            </CardHeader>
            <CardContent>
                <Calendar
                    mode="single"
                    selected={date}
                    onSelect={setDate}
                    className="rounded-md border"
                    />
            </CardContent>
        </Card>
      </div>

      <div className="lg:col-span-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
                <CardTitle>Appointments for {date ? format(date, "PPP") : '...'}</CardTitle>
                <CardDescription>You have {dailyAppointments.length} appointments scheduled.</CardDescription>
            </div>
            <Dialog>
                <DialogTrigger asChild>
                    <Button>
                        <PlusCircle className="mr-2 h-4 w-4" />
                        New Appointment
                    </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                    <DialogTitle>Schedule New Appointment</DialogTitle>
                    <DialogDescription>
                        Fill in the details to schedule a new appointment.
                    </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="patient" className="text-right">
                            Patient
                            </Label>
                             <Select>
                                <SelectTrigger className="col-span-3">
                                    <SelectValue placeholder="Select a patient" />
                                </SelectTrigger>
                                <SelectContent>
                                    {patients.map(p => <SelectItem key={p.id} value={p.id}>{p.name}</SelectItem>)}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="doctor" className="text-right">
                            Doctor
                            </Label>
                            <Select>
                                <SelectTrigger className="col-span-3">
                                    <SelectValue placeholder="Select a doctor" />
                                </SelectTrigger>
                                <SelectContent>
                                    {doctors.map(d => <SelectItem key={d.id} value={d.id}>{d.name}</SelectItem>)}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="time" className="text-right">
                            Time
                            </Label>
                            <Input id="time" type="time" defaultValue="10:00" className="col-span-3" />
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="reason" className="text-right">
                            Reason
                            </Label>
                            <Input id="reason" placeholder="e.g. Follow-up" className="col-span-3" />
                        </div>
                    </div>
                    <DialogFooter>
                    <Button type="submit">Schedule</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
          </CardHeader>
          <CardContent className="space-y-4">
            {dailyAppointments.length > 0 ? (
                dailyAppointments.map((app) => (
                    <div key={app.id} className="flex items-center p-4 border rounded-lg shadow-sm">
                        <Avatar className="h-12 w-12 mr-4">
                            <AvatarImage src={getPatient(app.patientId)?.avatarUrl} data-ai-hint="person" />
                            <AvatarFallback>{getPatient(app.patientId)?.name.charAt(0)}</AvatarFallback>
                        </Avatar>
                        <div className="flex-1">
                            <p className="font-semibold">{getPatient(app.patientId)?.name}</p>
                            <p className="text-sm text-muted-foreground">{app.reason}</p>
                            <p className="text-xs text-muted-foreground">with {getDoctor(app.doctorId)?.name}</p>
                        </div>
                        <div className="text-right">
                            <p className="font-medium">{app.time}</p>
                            <Badge variant={app.status === "Completed" ? "default" : "outline"}>{app.status}</Badge>
                        </div>
                    </div>
                ))
            ) : (
                <div className="text-center text-muted-foreground py-16">No appointments for this day.</div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
