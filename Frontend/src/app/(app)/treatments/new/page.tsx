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
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { useToast } from "@/components/ui/use-toast"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { useAuth } from "@/components/auth-provider"
import { Switch } from "@/components/ui/switch"

const treatmentFormSchema = z.object({
  name: z.string().min(3, "El nombre debe tener al menos 3 caracteres"),
  description: z.string().optional(),
  duration: z.string().min(2, "La duración es requerida (ej: 6 meses, 3 semanas)"),
  number_of_sessions: z.number().min(1, "Debe tener al menos 1 sesión"),
  price: z.number().min(0, "El precio debe ser mayor o igual a 0"),
  is_active: z.boolean().default(true),
})

type TreatmentFormValues = z.infer<typeof treatmentFormSchema>

export default function NewTreatmentPage() {
  const { toast } = useToast()
  const router = useRouter()
  const auth = useAuth()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const form = useForm<TreatmentFormValues>({
    resolver: zodResolver(treatmentFormSchema),
    defaultValues: {
      name: "",
      description: "",
      duration: "",
      number_of_sessions: 1,
      price: 0,
      is_active: true,
    },
  })

  async function onSubmit(data: TreatmentFormValues) {
    setIsSubmitting(true)

    try {
      const response = await fetch('/api/historia-clinica/treatments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${auth.getToken()}`
        },
        body: JSON.stringify(data)
      })

      const result = await response.json()

      if (result.success) {
        toast({
          title: "Tratamiento Creado",
          description: `${data.name} ha sido creado exitosamente.`,
        })
        router.push("/treatments")
      } else {
        toast({
          title: "Error",
          description: result.message || "Error al crear tratamiento",
          variant: "destructive"
        })
      }
    } catch (error) {
      console.error('Create treatment error:', error)
      toast({
        title: "Error",
        description: "Ocurrió un error al crear el tratamiento",
        variant: "destructive"
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Card className="max-w-3xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl">Nuevo Tratamiento Capilar</CardTitle>
        <CardDescription>Crea un nuevo tratamiento disponible para los pacientes</CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nombre del Tratamiento</FormLabel>
                  <FormControl>
                    <Input placeholder="RECUPERACION CAPILAR" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Descripción</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Descripción detallada del tratamiento..."
                      className="resize-none h-24"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    Describe los beneficios y características del tratamiento
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <FormField
                control={form.control}
                name="duration"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Duración</FormLabel>
                    <FormControl>
                      <Input placeholder="6 meses" {...field} />
                    </FormControl>
                    <FormDescription>Ej: 3 meses, 6 semanas</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="number_of_sessions"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Cantidad de Sesiones</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        min="1"
                        {...field}
                        onChange={(e) => field.onChange(parseInt(e.target.value))}
                      />
                    </FormControl>
                    <FormDescription>Número total de citas</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="price"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Precio ($)</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        min="0"
                        step="0.01"
                        {...field}
                        onChange={(e) => field.onChange(parseFloat(e.target.value))}
                      />
                    </FormControl>
                    <FormDescription>Precio total</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="is_active"
              render={({ field }) => (
                <FormItem className="flex items-center justify-between rounded-lg border p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">Tratamiento Activo</FormLabel>
                    <FormDescription>
                      Este tratamiento estará disponible para asignar a pacientes
                    </FormDescription>
                  </div>
                  <FormControl>
                    <Switch
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />

            <div className="flex justify-end gap-3 pt-6 border-t">
              <Button type="button" variant="outline" onClick={() => router.back()} disabled={isSubmitting}>
                Cancelar
              </Button>
              <Button type="submit" disabled={isSubmitting} size="lg">
                {isSubmitting ? "Creando..." : "Crear Tratamiento"}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}
