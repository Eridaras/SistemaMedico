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
import { CalendarIcon, Plus, X, AlertTriangle, UserCheck } from "lucide-react"
import { Calendar } from "@/components/ui/calendar"
import { cn } from "@/lib/utils"
import { format, differenceInYears } from "date-fns"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { useToast } from "@/components/ui/use-toast"
import { useRouter } from "next/navigation"
import { useState, useEffect } from "react"
import { useAuth } from "@/components/auth-provider"
import { Checkbox } from "@/components/ui/checkbox"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { PhotoUploader } from "@/components/photo-uploader"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { validateEcuadorianCedula } from "@/lib/validators"

// Schema del formulario de historia clínica capilar
const hairClinicFormSchema = z.object({
  // SECCIÓN 1: DATOS PERSONALES
  doc_number: z.string().min(10, "El número de cédula debe tener al menos 10 caracteres"),
  firstName: z.string().min(2, "El nombre debe tener al menos 2 caracteres"),
  lastName: z.string().min(2, "El apellido debe tener al menos 2 caracteres"),
  dob: z.date({ required_error: "La fecha de nacimiento es requerida" }),
  contact: z.string().min(10, "El teléfono debe tener al menos 10 dígitos"),
  email: z.string().email("Ingrese un email válido"),
  address: z.string().min(5, "La dirección es requerida"),
  occupation: z.string().min(2, "La ocupación es requerida"),
  bloodType: z.enum(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "DESCONOCIDO"], {
    required_error: "El tipo de sangre es requerido"
  }),
  gender: z.enum(["M", "F"], { required_error: "El sexo es requerido" }),

  // SECCIÓN 2: ANTECEDENTES
  personalPathological: z.string(),
  personalPathologicalNR: z.boolean().default(false),
  allergies: z.string(),
  familyPathological: z.string(),
  familyPathologicalNR: z.boolean().default(false),
  previousProcedures: z.array(z.object({
    procedure: z.string(),
    medication: z.string(),
    duration: z.string(),
    timeAgo: z.string(),
  })),

  // SECCIÓN 3: MOTIVO DE CONSULTA Y EXAMEN
  motivoConsulta: z.string().min(3, "El motivo de consulta es requerido"),
  examenFisico: z.enum(["DIFUSA", "CORONILLA", "ENTRADAS"], {
    required_error: "Debe seleccionar un tipo de examen físico"
  }),

  // SECCIÓN 4: FOTOS (se manejará aparte)

  // SECCIÓN 5: TRATAMIENTOS (se manejarán aparte como array)
})

type HairClinicFormValues = z.infer<typeof hairClinicFormSchema>

export default function NewPatientPage() {
  const { toast } = useToast()
  const router = useRouter()
  const auth = useAuth()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [age, setAge] = useState<number | null>(null)
  const [procedures, setProcedures] = useState<any[]>([])
  const [photos, setPhotos] = useState<any[]>([])
  const [treatments, setTreatments] = useState<any[]>([])
  const [selectedTreatments, setSelectedTreatments] = useState<any[]>([])

  // Estados para validación de cédula y modal de duplicado
  const [cedulaValidationState, setCedulaValidationState] = useState<'idle' | 'invalid' | 'checking' | 'valid' | 'duplicate'>('idle')
  const [duplicatePatient, setDuplicatePatient] = useState<any>(null)
  const [showDuplicateModal, setShowDuplicateModal] = useState(false)

  const form = useForm<HairClinicFormValues>({
    resolver: zodResolver(hairClinicFormSchema),
    defaultValues: {
      doc_number: "",
      firstName: "",
      lastName: "",
      email: "",
      contact: "",
      address: "",
      occupation: "",
      gender: "M",
      bloodType: "DESCONOCIDO",
      personalPathological: "",
      personalPathologicalNR: false,
      allergies: "",
      familyPathological: "",
      familyPathologicalNR: false,
      previousProcedures: [],
      motivoConsulta: "",
      examenFisico: "DIFUSA",
    },
  })

  // Cargar tratamientos disponibles
  useEffect(() => {
    const fetchTreatments = async () => {
      try {
        const response = await fetch('/api/historia-clinica/treatments', {
          headers: {
            'Authorization': `Bearer ${auth.getToken()}`
          }
        })
        const data = await response.json()
        if (data.success) {
          setTreatments(data.data?.treatments?.filter((t: any) => t.is_active) || [])
        }
      } catch (error) {
        console.error('Error loading treatments:', error)
      }
    }
    fetchTreatments()
  }, [])

  // Validar cédula en tiempo real
  const handleCedulaChange = async (cedula: string) => {
    // Limpiar estado si está vacío
    if (!cedula || cedula.length === 0) {
      setCedulaValidationState('idle')
      return
    }

    // Si tiene menos de 10 dígitos, esperar
    if (cedula.length < 10) {
      setCedulaValidationState('idle')
      return
    }

    // Validar formato de cédula ecuatoriana
    if (!validateEcuadorianCedula(cedula)) {
      setCedulaValidationState('invalid')
      return
    }

    // Cédula válida, ahora verificar si existe en el sistema
    setCedulaValidationState('checking')

    try {
      const response = await fetch(`/api/historia-clinica/patients/search?doc_number=${cedula}`, {
        headers: {
          'Authorization': `Bearer ${auth.getToken()}`
        }
      })

      const data = await response.json()

      if (data.success && data.data?.patient) {
        // Paciente existe
        setDuplicatePatient(data.data.patient)
        setCedulaValidationState('duplicate')
        setShowDuplicateModal(true)
      } else {
        // No existe, cédula válida y disponible
        setCedulaValidationState('valid')
      }
    } catch (error) {
      console.error('Error checking cedula:', error)
      setCedulaValidationState('valid') // Asumir válida si hay error de red
    }
  }

  // Calcular edad cuando cambia la fecha de nacimiento
  const handleDobChange = (date: Date | undefined) => {
    if (date) {
      const years = differenceInYears(new Date(), date)
      setAge(years)
    } else {
      setAge(null)
    }
  }

  // Agregar procedimiento previo
  const addProcedure = () => {
    setProcedures([...procedures, { procedure: "", medication: "", duration: "", timeAgo: "" }])
  }

  // Remover procedimiento
  const removeProcedure = (index: number) => {
    setProcedures(procedures.filter((_, i) => i !== index))
  }

  // Agregar tratamiento
  const addTreatment = (treatmentId: number) => {
    const treatment = treatments.find(t => t.hair_treatment_id === treatmentId)
    if (treatment && !selectedTreatments.find(t => t.hair_treatment_id === treatmentId)) {
      setSelectedTreatments([...selectedTreatments, { ...treatment, start_date: new Date() }])
    }
  }

  // Remover tratamiento
  const removeTreatment = (treatmentId: number) => {
    setSelectedTreatments(selectedTreatments.filter(t => t.hair_treatment_id !== treatmentId))
  }

  // Manejar reactivación de paciente inactivo
  const handleReactivatePatient = async () => {
    if (!duplicatePatient) return

    try {
      const reactivateResponse = await fetch(`/api/historia-clinica/patients/${duplicatePatient.patient_id}/reactivate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${auth.getToken()}`
        }
      })

      const reactivateResult = await reactivateResponse.json()

      if (reactivateResult.success) {
        toast({
          title: "Paciente Reactivado",
          description: `${duplicatePatient.first_name} ${duplicatePatient.last_name} ha sido reactivado exitosamente.`
        })
        setShowDuplicateModal(false)
        router.push(`/patients/${duplicatePatient.patient_id}`)
      } else {
        toast({
          title: "Error",
          description: "No se pudo reactivar el paciente",
          variant: "destructive"
        })
      }
    } catch (error) {
      console.error('Reactivate error:', error)
      toast({
        title: "Error",
        description: "Ocurrió un error al reactivar el paciente",
        variant: "destructive"
      })
    }
  }

  async function onSubmit(data: HairClinicFormValues) {
    // Validar que no sea un paciente duplicado antes de enviar
    if (cedulaValidationState === 'duplicate') {
      setShowDuplicateModal(true)
      return
    }

    setIsSubmitting(true);

    try {
      // 1. Crear paciente
      const patientData = {
        doc_type: "CEDULA",
        doc_number: data.doc_number,
        first_name: data.firstName,
        last_name: data.lastName,
        email: data.email || undefined,
        phone: data.contact,
        address: data.address || undefined,
        birth_date: format(data.dob, "yyyy-MM-dd"),
        gender: data.gender,
        occupation: data.occupation,
        medical_record_opening_date: format(new Date(), "yyyy-MM-dd")
      };

      const patientResponse = await fetch('/api/historia-clinica/patients', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${auth.getToken()}`
        },
        body: JSON.stringify(patientData)
      });

      const patientResult = await patientResponse.json();

      if (patientResult.success && patientResult.data?.patient) {
        const patientId = patientResult.data.patient.patient_id;

        // 2. Crear historia médica completa
        const medicalHistoryData = {
          blood_type: data.bloodType !== "DESCONOCIDO" ? data.bloodType : null,
          allergies: data.allergies ? data.allergies.split(',').map(a => a.trim()).filter(a => a) : [],
          personal_pathological_history: data.personalPathologicalNR ? null : data.personalPathological,
          personal_pathological_nr: data.personalPathologicalNR,
          family_pathological_history: data.familyPathologicalNR ? null : data.familyPathological,
          family_pathological_nr: data.familyPathologicalNR,
          previous_procedures: procedures.length > 0 ? procedures : null
        };

        await fetch(`/api/historia-clinica/patients/${patientId}/medical-history`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${auth.getToken()}`
          },
          body: JSON.stringify(medicalHistoryData)
        });

        // 3. Crear registro clínico (motivo de consulta y examen físico)
        const clinicalRecordData = {
          patient_id: patientId,
          motivo_consulta: data.motivoConsulta,
          examen_fisico: data.examenFisico
        };

        await fetch(`/api/historia-clinica/clinical-records`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${auth.getToken()}`
          },
          body: JSON.stringify(clinicalRecordData)
        });

        // 4. Subir fotos si hay
        if (photos.length > 0) {
          const formData = new FormData()
          formData.append('session_number', '1')

          photos.forEach((photo) => {
            if (photo.compressed) {
              // Crear archivo desde el blob comprimido
              const compressedFile = new File([photo.compressed], photo.file.name, {
                type: 'image/jpeg'
              })
              formData.append('photos', compressedFile)
            } else {
              formData.append('photos', photo.file)
            }
          })

          await fetch(`/api/historia-clinica/patients/${patientId}/photos`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${auth.getToken()}`
            },
            body: formData
          })
        }

        // 5. Asignar tratamientos si hay seleccionados
        for (const treatment of selectedTreatments) {
          await fetch(`/api/historia-clinica/patients/${patientId}/treatments`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${auth.getToken()}`
            },
            body: JSON.stringify({
              hair_treatment_id: treatment.hair_treatment_id,
              start_date: format(treatment.start_date, "yyyy-MM-dd")
            })
          })
        }

        toast({
          title: "Paciente Registrado",
          description: `${data.firstName} ${data.lastName} ha sido registrado exitosamente con su historia clínica capilar${photos.length > 0 ? ` y ${photos.length} foto(s)` : ''}.`,
        });

        router.push(`/patients/${patientId}`);
      } else {
        toast({
          title: "Error",
          description: patientResult.message || "Error al registrar paciente",
          variant: "destructive"
        });
      }
    } catch (error) {
      console.error('Create patient error:', error);
      toast({
        title: "Error",
        description: "Ocurrió un error al registrar el paciente",
        variant: "destructive"
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Card className="max-w-6xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl">Nueva Historia Clínica Capilar</CardTitle>
        <CardDescription>Complete todos los campos para crear la historia clínica completa del paciente</CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-10">

            {/* ============ SECCIÓN 1: DATOS PERSONALES ============ */}
            <div className="space-y-4">
              <div className="border-b pb-2">
                <h3 className="text-lg font-semibold">Datos Personales</h3>
                <p className="text-sm text-muted-foreground">Información del paciente</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <FormField
                  control={form.control}
                  name="doc_number"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Cédula</FormLabel>
                      <FormControl>
                        <div className="relative">
                          <Input
                            placeholder="1234567890"
                            {...field}
                            onChange={(e) => {
                              field.onChange(e)
                              handleCedulaChange(e.target.value)
                            }}
                            className={cn(
                              cedulaValidationState === 'invalid' && "border-destructive focus-visible:ring-destructive",
                              cedulaValidationState === 'valid' && "border-green-500 focus-visible:ring-green-500",
                              cedulaValidationState === 'duplicate' && "border-destructive focus-visible:ring-destructive"
                            )}
                          />
                          {cedulaValidationState === 'checking' && (
                            <div className="absolute right-3 top-2.5">
                              <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                            </div>
                          )}
                          {cedulaValidationState === 'valid' && (
                            <UserCheck className="absolute right-3 top-2.5 h-5 w-5 text-green-500" />
                          )}
                          {cedulaValidationState === 'invalid' && (
                            <AlertTriangle className="absolute right-3 top-2.5 h-5 w-5 text-destructive" />
                          )}
                          {cedulaValidationState === 'duplicate' && (
                            <AlertTriangle className="absolute right-3 top-2.5 h-5 w-5 text-destructive" />
                          )}
                        </div>
                      </FormControl>
                      {cedulaValidationState === 'invalid' && (
                        <p className="text-sm font-medium text-destructive">
                          Cédula ecuatoriana inválida. Verifique el número ingresado.
                        </p>
                      )}
                      {cedulaValidationState === 'duplicate' && (
                        <p className="text-sm font-medium text-destructive">
                          Este paciente ya existe en el sistema.
                        </p>
                      )}
                      {cedulaValidationState === 'valid' && (
                        <p className="text-sm font-medium text-green-600">
                          Cédula válida y disponible.
                        </p>
                      )}
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="firstName"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Nombres</FormLabel>
                      <FormControl>
                        <Input placeholder="WILMER" {...field} />
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
                      <FormLabel>Apellidos</FormLabel>
                      <FormControl>
                        <Input placeholder="QUIMI" {...field} />
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
                      <FormLabel>Fecha de Nacimiento {age !== null && <span className="text-xs text-muted-foreground ml-2">({age} años)</span>}</FormLabel>
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
                                format(field.value, "dd/MM/yyyy")
                              ) : (
                                <span>Seleccione una fecha</span>
                              )}
                              <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                            </Button>
                          </FormControl>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0" align="start">
                          <Calendar
                            mode="single"
                            selected={field.value}
                            onSelect={(date) => {
                              field.onChange(date)
                              handleDobChange(date)
                            }}
                            disabled={(date) =>
                              date > new Date() || date < new Date("1900-01-01")
                            }
                            initialFocus
                          />
                        </PopoverContent>
                      </Popover>
                      <FormDescription>Edad se calcula automáticamente</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="contact"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Teléfono</FormLabel>
                      <FormControl>
                        <Input placeholder="0978845001" {...field} />
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
                      <FormLabel>Correo</FormLabel>
                      <FormControl>
                        <Input placeholder="paciente@email.com" type="email" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="address"
                  render={({ field }) => (
                    <FormItem className="md:col-span-2">
                      <FormLabel>Dirección</FormLabel>
                      <FormControl>
                        <Input placeholder="Av. Principal, Quito" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="occupation"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Ocupación</FormLabel>
                      <FormControl>
                        <Input placeholder="Ingeniero" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="bloodType"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Tipo de Sangre</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Seleccione" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="A+">A+</SelectItem>
                          <SelectItem value="A-">A-</SelectItem>
                          <SelectItem value="B+">B+</SelectItem>
                          <SelectItem value="B-">B-</SelectItem>
                          <SelectItem value="AB+">AB+</SelectItem>
                          <SelectItem value="AB-">AB-</SelectItem>
                          <SelectItem value="O+">O+</SelectItem>
                          <SelectItem value="O-">O-</SelectItem>
                          <SelectItem value="DESCONOCIDO">Desconocido</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="gender"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Sexo</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Seleccione" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="M">Masculino</SelectItem>
                          <SelectItem value="F">Femenino</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="md:col-span-3 bg-muted/50 p-3 rounded-md">
                  <p className="text-sm text-muted-foreground">
                    <strong>Fecha Apertura Historia Clínica:</strong> {format(new Date(), "dd/MM/yyyy")}
                  </p>
                </div>
              </div>
            </div>

            {/* ============ SECCIÓN 2: ANTECEDENTES ============ */}
            <div className="space-y-6">
              <div className="border-b pb-2">
                <h3 className="text-lg font-semibold">Antecedentes</h3>
                <p className="text-sm text-muted-foreground">Historia médica del paciente</p>
              </div>

              {/* Antecedentes Patológicos Personales */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <FormLabel>Antecedentes Patológicos Personales</FormLabel>
                  <FormField
                    control={form.control}
                    name="personalPathologicalNR"
                    render={({ field }) => (
                      <FormItem className="flex items-center space-x-2 space-y-0">
                        <FormControl>
                          <Checkbox
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                        <FormLabel className="text-sm font-normal cursor-pointer">NR (No Registra)</FormLabel>
                      </FormItem>
                    )}
                  />
                </div>
                <FormField
                  control={form.control}
                  name="personalPathological"
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Textarea
                          placeholder="Ej: HTA TTO LOSARTAN 10 MG"
                          className={cn(
                            "resize-none h-20 transition-all",
                            form.watch("personalPathologicalNR") && "opacity-40 pointer-events-none"
                          )}
                          {...field}
                          disabled={form.watch("personalPathologicalNR")}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              {/* Alergias */}
              <FormField
                control={form.control}
                name="allergies"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Alergias</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Penicilina, Polen, Mariscos (separadas por comas)"
                        className="resize-none h-20"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Antecedentes Patológicos Familiares */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <FormLabel>Antecedentes Patológicos Familiares</FormLabel>
                  <FormField
                    control={form.control}
                    name="familyPathologicalNR"
                    render={({ field }) => (
                      <FormItem className="flex items-center space-x-2 space-y-0">
                        <FormControl>
                          <Checkbox
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                        <FormLabel className="text-sm font-normal cursor-pointer">NR (No Registra)</FormLabel>
                      </FormItem>
                    )}
                  />
                </div>
                <FormField
                  control={form.control}
                  name="familyPathological"
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Textarea
                          placeholder="Ej: MADRE HTA"
                          className={cn(
                            "resize-none h-20 transition-all",
                            form.watch("familyPathologicalNR") && "opacity-40 pointer-events-none"
                          )}
                          {...field}
                          disabled={form.watch("familyPathologicalNR")}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              {/* Procedimientos Previos */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <FormLabel>Procedimientos Previos</FormLabel>
                  <Button type="button" size="sm" variant="outline" onClick={addProcedure}>
                    <Plus className="h-4 w-4 mr-1" />
                    Agregar Procedimiento
                  </Button>
                </div>
                {procedures.length === 0 && (
                  <p className="text-sm text-muted-foreground">No hay procedimientos registrados</p>
                )}
                {procedures.map((proc, index) => (
                  <div key={index} className="grid grid-cols-1 md:grid-cols-5 gap-3 p-3 border rounded-md">
                    <Input
                      placeholder="Procedimiento"
                      value={proc.procedure}
                      onChange={(e) => {
                        const updated = [...procedures]
                        updated[index].procedure = e.target.value
                        setProcedures(updated)
                      }}
                    />
                    <Input
                      placeholder="Medicamento"
                      value={proc.medication}
                      onChange={(e) => {
                        const updated = [...procedures]
                        updated[index].medication = e.target.value
                        setProcedures(updated)
                      }}
                    />
                    <Input
                      placeholder="Duración"
                      value={proc.duration}
                      onChange={(e) => {
                        const updated = [...procedures]
                        updated[index].duration = e.target.value
                        setProcedures(updated)
                      }}
                    />
                    <Input
                      placeholder="Hace cuánto"
                      value={proc.timeAgo}
                      onChange={(e) => {
                        const updated = [...procedures]
                        updated[index].timeAgo = e.target.value
                        setProcedures(updated)
                      }}
                    />
                    <Button
                      type="button"
                      variant="destructive"
                      size="sm"
                      onClick={() => removeProcedure(index)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            {/* ============ SECCIÓN 3: MOTIVO DE CONSULTA Y EXAMEN FÍSICO ============ */}
            <div className="space-y-6">
              <div className="border-b pb-2">
                <h3 className="text-lg font-semibold">Motivo de Consulta y Examen Físico</h3>
                <p className="text-sm text-muted-foreground">Consulta actual</p>
              </div>

              <FormField
                control={form.control}
                name="motivoConsulta"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Motivo de Consulta y Enfermedad Actual</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="ALOPECIA"
                        className="resize-none h-32"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="examenFisico"
                render={({ field }) => (
                  <FormItem className="space-y-3">
                    <FormLabel>Examen Físico</FormLabel>
                    <FormControl>
                      <RadioGroup
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                        className="flex gap-6"
                      >
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="DIFUSA" id="difusa" />
                          <Label htmlFor="difusa" className="cursor-pointer">DIFUSA</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="CORONILLA" id="coronilla" />
                          <Label htmlFor="coronilla" className="cursor-pointer">CORONILLA</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="ENTRADAS" id="entradas" />
                          <Label htmlFor="entradas" className="cursor-pointer">ENTRADAS</Label>
                        </div>
                      </RadioGroup>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {/* ============ SECCIÓN 4: TRATAMIENTOS ============ */}
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b pb-2">
                <div>
                  <h3 className="text-lg font-semibold">Tratamientos Capilares</h3>
                  <p className="text-sm text-muted-foreground">Asigna uno o varios tratamientos al paciente</p>
                </div>
              </div>

              {/* Selector de tratamiento */}
              <div className="flex gap-2">
                <Select
                  onValueChange={(value) => {
                    if (value !== "none") {
                      addTreatment(parseInt(value))
                    }
                  }}
                  value="none"
                >
                  <SelectTrigger className="flex-1">
                    <SelectValue placeholder="Seleccione un tratamiento para agregar" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Seleccione un tratamiento...</SelectItem>
                    {treatments
                      .filter(t => !selectedTreatments.find(st => st.hair_treatment_id === t.hair_treatment_id))
                      .map((treatment) => (
                        <SelectItem
                          key={treatment.hair_treatment_id}
                          value={treatment.hair_treatment_id.toString()}
                        >
                          {treatment.name} - ${parseFloat(treatment.price || '0').toFixed(2)} ({treatment.number_of_sessions} sesiones)
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Lista de tratamientos seleccionados */}
              {selectedTreatments.length > 0 ? (
                <div className="space-y-3">
                  {selectedTreatments.map((treatment) => (
                    <Card key={treatment.hair_treatment_id} className="relative">
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="absolute top-2 right-2 h-8 w-8"
                        onClick={() => removeTreatment(treatment.hair_treatment_id)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                      <CardContent className="pt-6">
                        <div className="grid grid-cols-2 gap-4">
                          <div className="col-span-2">
                            <p className="font-semibold text-lg">{treatment.name}</p>
                            <p className="text-sm text-muted-foreground">{treatment.description || 'Sin descripción'}</p>
                          </div>
                          <div>
                            <Label className="text-xs text-muted-foreground">Duración</Label>
                            <p className="text-sm font-medium">{treatment.duration}</p>
                          </div>
                          <div>
                            <Label className="text-xs text-muted-foreground">Sesiones</Label>
                            <p className="text-sm font-medium">{treatment.number_of_sessions} sesiones</p>
                          </div>
                          <div>
                            <Label className="text-xs text-muted-foreground">Precio</Label>
                            <p className="text-sm font-medium">${parseFloat(treatment.price || '0').toFixed(2)}</p>
                          </div>
                          <div>
                            <Label className="text-xs text-muted-foreground">Fecha de Inicio</Label>
                            <p className="text-sm font-medium">{format(treatment.start_date, "dd/MM/yyyy")}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4 border-2 border-dashed rounded-lg">
                  No hay tratamientos asignados. Selecciona uno arriba para agregarlo.
                </p>
              )}
            </div>

            {/* ============ SECCIÓN 5: FOTOS ============ */}
            <div className="space-y-4">
              <div className="border-b pb-2">
                <h3 className="text-lg font-semibold">Fotos</h3>
                <p className="text-sm text-muted-foreground">Máximo 5 fotos (Cita 1 Historia Clínica)</p>
              </div>
              <PhotoUploader
                maxPhotos={5}
                sessionLabel="Cita 1 Historia Clínica"
                patientName={`${form.watch("firstName")} ${form.watch("lastName")}`.trim()}
                onPhotosChange={setPhotos}
              />
            </div>

            {/* BOTONES */}
            <div className="flex justify-end gap-3 pt-6 border-t">
              <Button type="button" variant="outline" onClick={() => router.back()} disabled={isSubmitting}>
                Cancelar
              </Button>
              <Button type="submit" disabled={isSubmitting} size="lg">
                {isSubmitting ? "Creando Historia Clínica..." : "Crear Historia Clínica"}
              </Button>
            </div>
          </form>
        </Form>

        {/* MODAL DE PACIENTE DUPLICADO */}
        <Dialog open={showDuplicateModal} onOpenChange={setShowDuplicateModal}>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-destructive">
                <AlertTriangle className="h-5 w-5" />
                Paciente Ya Existe
              </DialogTitle>
              <DialogDescription>
                Ya existe un paciente registrado con esta cédula en el sistema.
              </DialogDescription>
            </DialogHeader>

            {duplicatePatient && (
              <div className="space-y-4 py-4">
                <div className="rounded-lg border bg-muted/50 p-4 space-y-3">
                  <div>
                    <Label className="text-xs text-muted-foreground">Nombre Completo</Label>
                    <p className="font-semibold">
                      {duplicatePatient.first_name} {duplicatePatient.last_name}
                    </p>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <Label className="text-xs text-muted-foreground">Cédula</Label>
                      <p className="text-sm font-medium">{duplicatePatient.doc_number}</p>
                    </div>
                    <div>
                      <Label className="text-xs text-muted-foreground">Teléfono</Label>
                      <p className="text-sm font-medium">{duplicatePatient.phone || 'N/A'}</p>
                    </div>
                  </div>
                  <div>
                    <Label className="text-xs text-muted-foreground">Estado</Label>
                    <p className="text-sm font-medium">
                      {duplicatePatient.is_active ? (
                        <span className="text-green-600">ACTIVO</span>
                      ) : (
                        <span className="text-destructive">INACTIVO</span>
                      )}
                    </p>
                  </div>
                </div>

                {!duplicatePatient.is_active && (
                  <div className="rounded-lg border border-amber-200 bg-amber-50 p-3">
                    <p className="text-sm text-amber-900">
                      Este paciente está marcado como INACTIVO. Puede reactivarlo para continuar usando su historia clínica.
                    </p>
                  </div>
                )}
              </div>
            )}

            <DialogFooter className="flex-col sm:flex-row gap-2">
              <Button
                variant="outline"
                onClick={() => {
                  setShowDuplicateModal(false)
                  form.setValue('doc_number', '')
                  setCedulaValidationState('idle')
                }}
                className="w-full sm:w-auto"
              >
                Cancelar
              </Button>

              {duplicatePatient?.is_active ? (
                <Button
                  onClick={() => {
                    setShowDuplicateModal(false)
                    router.push(`/patients/${duplicatePatient.patient_id}`)
                  }}
                  className="w-full sm:w-auto"
                >
                  Ver Paciente
                </Button>
              ) : (
                <Button
                  onClick={handleReactivatePatient}
                  className="w-full sm:w-auto"
                >
                  <UserCheck className="h-4 w-4 mr-2" />
                  Reactivar Paciente
                </Button>
              )}
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  )
}
