"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { CalendarIcon } from "lucide-react"
import { Calendar } from "@/components/ui/calendar"
import { cn } from "@/lib/utils"
import { format } from "date-fns"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { useToast } from "@/components/ui/use-toast"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { useAuth } from "@/components/auth-provider"

const patientFormSchema = z.object({
  doc_type: z.enum(["CEDULA", "RUC", "PASSPORT"], {
    required_error: "Document type is required"
  }),
  doc_number: z.string().min(10, "Document number must be at least 10 characters."),
  firstName: z.string().min(2, "First name must be at least 2 characters."),
  lastName: z.string().min(2, "Last name must be at least 2 characters."),
  dob: z.date({ required_error: "A date of birth is required." }),
  gender: z.enum(["M", "F", "Other"], { required_error: "Gender is required" }),
  contact: z.string().min(10, "Contact number must be at least 10 digits."),
  email: z.string().email("Please enter a valid email address.").optional().or(z.literal("")),
  address: z.string().min(5, "Address is too short.").optional().or(z.literal("")),
  allergies: z.string().optional(),
  conditions: z.string().optional(),
})

type PatientFormValues = z.infer<typeof patientFormSchema>

export default function NewPatientPage() {
    const { toast } = useToast()
    const router = useRouter()
    const auth = useAuth()
    const [isSubmitting, setIsSubmitting] = useState(false)

  const form = useForm<PatientFormValues>({
    resolver: zodResolver(patientFormSchema),
    defaultValues: {
      doc_type: "CEDULA",
      doc_number: "",
      firstName: "",
      lastName: "",
      email: "",
      contact: "",
      address: "",
      allergies: "",
      conditions: "",
      gender: "M"
    },
  })

  async function onSubmit(data: PatientFormValues) {
    setIsSubmitting(true);

    try {
      // Prepare patient data for backend
      const patientData = {
        doc_type: data.doc_type,
        doc_number: data.doc_number,
        first_name: data.firstName,
        last_name: data.lastName,
        email: data.email || undefined,
        phone: data.contact,
        address: data.address || undefined,
        birth_date: format(data.dob, "yyyy-MM-dd"),
        gender: data.gender
      };

      const response = await fetch('/api/historia-clinica/patients', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${auth.getToken()}`
        },
        body: JSON.stringify(patientData)
      });

      const result = await response.json();

      if (result.success && result.data?.patient) {
        const patientId = result.data.patient.patient_id;

        // If allergies or conditions provided, create/update medical history
        if (data.allergies || data.conditions) {
          const medicalHistoryData = {
            allergies: data.allergies ? data.allergies.split(',').map(a => a.trim()) : [],
            pathologies: data.conditions ? data.conditions.split(',').map(c => c.trim()) : []
          };

          await fetch(`/api/historia-clinica/patients/${patientId}/medical-history`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${auth.getToken()}`
            },
            body: JSON.stringify(medicalHistoryData)
          });
        }

        toast({
          title: "Patient Registered",
          description: `Successfully registered ${data.firstName} ${data.lastName}.`,
        });

        router.push("/patients");
      } else {
        toast({
          title: "Error",
          description: result.message || "Failed to register patient",
          variant: "destructive"
        });
      }
    } catch (error) {
      console.error('Create patient error:', error);
      toast({
        title: "Error",
        description: "An error occurred while registering the patient",
        variant: "destructive"
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Register New Patient</CardTitle>
        <CardDescription>Fill out the form below to add a new patient to the system.</CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-8">
                    <FormField
                    control={form.control}
                    name="doc_type"
                    render={({ field }) => (
                        <FormItem>
                        <FormLabel>Document Type</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                            <SelectTrigger>
                                <SelectValue placeholder="Select document type" />
                            </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                            <SelectItem value="CEDULA">Cédula</SelectItem>
                            <SelectItem value="RUC">RUC</SelectItem>
                            <SelectItem value="PASSPORT">Passport</SelectItem>
                            </SelectContent>
                        </Select>
                        <FormMessage />
                        </FormItem>
                    )}
                    />
                    <FormField
                    control={form.control}
                    name="doc_number"
                    render={({ field }) => (
                        <FormItem>
                        <FormLabel>Document Number</FormLabel>
                        <FormControl>
                            <Input placeholder="1234567890" {...field} />
                        </FormControl>
                        <FormMessage />
                        </FormItem>
                    )}
                    />
                    <FormField
                    control={form.control}
                    name="firstName"
                    render={({ field }) => (
                        <FormItem>
                        <FormLabel>First Name</FormLabel>
                        <FormControl>
                            <Input placeholder="John" {...field} />
                        </FormControl>
                        <FormMessage />
                        </FormItem>
                    )}
                    />
                    <FormField
                    control={form.control}
                    name="lastName"
                    render={({ field }) => (
                        <FormItem>
                        <FormLabel>Last Name</FormLabel>
                        <FormControl>
                            <Input placeholder="Doe" {...field} />
                        </FormControl>
                        <FormMessage />
                        </FormItem>
                    )}
                    />
                    <FormField
                    control={form.control}
                    name="dob"
                    render={({ field }) => (
                        <FormItem className="flex flex-col">
                        <FormLabel>Date of Birth</FormLabel>
                        <Popover>
                            <PopoverTrigger asChild>
                            <FormControl>
                                <Button
                                variant={"outline"}
                                className={cn(
                                    "w-full pl-3 text-left font-normal",
                                    !field.value && "text-muted-foreground"
                                )}
                                >
                                {field.value ? (
                                    format(field.value, "PPP")
                                ) : (
                                    <span>Pick a date</span>
                                )}
                                <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                                </Button>
                            </FormControl>
                            </PopoverTrigger>
                            <PopoverContent className="w-auto p-0" align="start">
                            <Calendar
                                mode="single"
                                selected={field.value}
                                onSelect={field.onChange}
                                disabled={(date) =>
                                date > new Date() || date < new Date("1900-01-01")
                                }
                                initialFocus
                            />
                            </PopoverContent>
                        </Popover>
                        <FormMessage />
                        </FormItem>
                    )}
                    />
                    <FormField
                    control={form.control}
                    name="gender"
                    render={({ field }) => (
                        <FormItem>
                        <FormLabel>Gender</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                            <SelectTrigger>
                                <SelectValue placeholder="Select a gender" />
                            </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                            <SelectItem value="M">Male</SelectItem>
                            <SelectItem value="F">Female</SelectItem>
                            <SelectItem value="Other">Other</SelectItem>
                            </SelectContent>
                        </Select>
                        <FormMessage />
                        </FormItem>
                    )}
                    />
                    <FormField
                    control={form.control}
                    name="contact"
                    render={({ field }) => (
                        <FormItem>
                        <FormLabel>Contact Number</FormLabel>
                        <FormControl>
                            <Input placeholder="+1-555-555-5555" {...field} />
                        </FormControl>
                        <FormMessage />
                        </FormItem>
                    )}
                    />
                     <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                        <FormItem>
                        <FormLabel>Email Address</FormLabel>
                        <FormControl>
                            <Input placeholder="john.doe@example.com" {...field} />
                        </FormControl>
                        <FormMessage />
                        </FormItem>
                    )}
                    />
                </div>

                <div className="space-y-8">
                   
                    <FormField
                    control={form.control}
                    name="address"
                    render={({ field }) => (
                        <FormItem>
                        <FormLabel>Address</FormLabel>
                        <FormControl>
                            <Textarea
                            placeholder="123 Main St, Anytown, USA"
                            className="resize-none h-24"
                            {...field}
                            />
                        </FormControl>
                        <FormMessage />
                        </FormItem>
                    )}
                    />
                    <FormField
                    control={form.control}
                    name="allergies"
                    render={({ field }) => (
                        <FormItem>
                        <FormLabel>Known Allergies</FormLabel>
                        <FormControl>
                            <Textarea
                            placeholder="e.g., Peanuts, Penicillin... (comma-separated)"
                            className="resize-none"
                            {...field}
                            />
                        </FormControl>
                        <FormDescription>
                            List any known allergies, separated by commas.
                        </FormDescription>
                        <FormMessage />
                        </FormItem>
                    )}
                    />
                    <FormField
                    control={form.control}
                    name="conditions"
                    render={({ field }) => (
                        <FormItem>
                        <FormLabel>Pre-existing Conditions</FormLabel>
                        <FormControl>
                            <Textarea
                            placeholder="e.g., Asthma, Hypertension... (comma-separated)"
                            className="resize-none"
                            {...field}
                            />
                        </FormControl>
                        <FormDescription>
                           List any pre-existing medical conditions, separated by commas.
                        </FormDescription>
                        <FormMessage />
                        </FormItem>
                    )}
                    />
                </div>
            </div>

            <div className="flex justify-end gap-2 pt-4">
                <Button type="button" variant="outline" onClick={() => router.back()} disabled={isSubmitting}>Cancel</Button>
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? "Registering..." : "Register Patient"}
                </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}
