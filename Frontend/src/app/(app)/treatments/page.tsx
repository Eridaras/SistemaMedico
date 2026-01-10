"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Plus, Pencil, Trash2 } from 'lucide-react'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '@/components/auth-provider'
import { useToast } from '@/components/ui/use-toast'
import { useRouter } from 'next/navigation'

interface Treatment {
  hair_treatment_id: number
  name: string
  description: string
  duration: string
  number_of_sessions: number
  price: number
  is_active: boolean
}

export default function TreatmentsPage() {
  const [treatments, setTreatments] = useState<Treatment[]>([])
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()
  const auth = useAuth()
  const router = useRouter()

  useEffect(() => {
    fetchTreatments()
  }, [])

  const fetchTreatments = async () => {
    try {
      const response = await fetch('/api/historia-clinica/treatments', {
        headers: {
          'Authorization': `Bearer ${auth.getToken()}`
        }
      })

      const data = await response.json()

      if (data.success) {
        setTreatments(data.data?.treatments || [])
      }
    } catch (error) {
      console.error('Error fetching treatments:', error)
      toast({
        title: "Error",
        description: "No se pudieron cargar los tratamientos",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('¿Está seguro de eliminar este tratamiento?')) return

    try {
      const response = await fetch(`/api/historia-clinica/treatments/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${auth.getToken()}`
        }
      })

      const data = await response.json()

      if (data.success) {
        toast({
          title: "Tratamiento Eliminado",
          description: "El tratamiento ha sido eliminado exitosamente"
        })
        fetchTreatments()
      } else {
        toast({
          title: "Error",
          description: data.message || "No se pudo eliminar el tratamiento",
          variant: "destructive"
        })
      }
    } catch (error) {
      console.error('Error deleting treatment:', error)
      toast({
        title: "Error",
        description: "Ocurrió un error al eliminar el tratamiento",
        variant: "destructive"
      })
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Gestión de Tratamientos</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Administra los tratamientos capilares disponibles
          </p>
        </div>
        <Button onClick={() => router.push('/treatments/new')} className="gap-2">
          <Plus className="h-4 w-4" />
          Nuevo Tratamiento
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Tratamientos Capilares</CardTitle>
          <CardDescription>
            Lista de todos los tratamientos disponibles en la clínica
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">
              Cargando tratamientos...
            </div>
          ) : treatments.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No hay tratamientos registrados
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nombre</TableHead>
                  <TableHead>Descripción</TableHead>
                  <TableHead>Duración</TableHead>
                  <TableHead className="text-center">Sesiones</TableHead>
                  <TableHead className="text-right">Precio</TableHead>
                  <TableHead className="text-center">Estado</TableHead>
                  <TableHead className="text-right">Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {treatments.map((treatment) => (
                  <TableRow key={treatment.hair_treatment_id}>
                    <TableCell className="font-medium">{treatment.name}</TableCell>
                    <TableCell className="max-w-xs truncate">
                      {treatment.description || '-'}
                    </TableCell>
                    <TableCell>{treatment.duration || '-'}</TableCell>
                    <TableCell className="text-center">{treatment.number_of_sessions}</TableCell>
                    <TableCell className="text-right">
                      ${parseFloat(treatment.price || '0').toFixed(2)}
                    </TableCell>
                    <TableCell className="text-center">
                      <Badge variant={treatment.is_active ? "default" : "secondary"}>
                        {treatment.is_active ? 'Activo' : 'Inactivo'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => router.push(`/treatments/${treatment.hair_treatment_id}`)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(treatment.hair_treatment_id)}
                          className="text-destructive hover:text-destructive"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
