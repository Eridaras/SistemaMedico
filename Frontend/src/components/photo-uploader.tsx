"use client"

import { useState, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Camera, Upload, X, ImageIcon } from 'lucide-react'
import { cn } from '@/lib/utils'
import Image from 'next/image'

interface Photo {
  id: string
  file: File
  preview: string
  compressed?: Blob
}

interface PhotoUploaderProps {
  maxPhotos?: number
  sessionLabel?: string
  patientName?: string
  onPhotosChange?: (photos: Photo[]) => void
}

export function PhotoUploader({
  maxPhotos = 5,
  sessionLabel = "Cita 1 Historia Clínica",
  patientName = "",
  onPhotosChange
}: PhotoUploaderProps) {
  const [photos, setPhotos] = useState<Photo[]>([])
  const [isCompressing, setIsCompressing] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)

  // Comprimir imagen usando Canvas
  const compressImage = async (file: File): Promise<Blob> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = (event) => {
        const img = document.createElement('img')
        img.src = event.target?.result as string
        img.onload = () => {
          const canvas = document.createElement('canvas')
          const ctx = canvas.getContext('2d')

          // Calcular dimensiones manteniendo aspect ratio
          let width = img.width
          let height = img.height
          const maxDimension = 1920 // Max 1920px en cualquier lado

          if (width > height && width > maxDimension) {
            height = (height / width) * maxDimension
            width = maxDimension
          } else if (height > maxDimension) {
            width = (width / height) * maxDimension
            height = maxDimension
          }

          canvas.width = width
          canvas.height = height

          ctx?.drawImage(img, 0, 0, width, height)

          // Comprimir con calidad 0.8
          canvas.toBlob(
            (blob) => {
              if (blob) {
                resolve(blob)
              } else {
                reject(new Error('Failed to compress image'))
              }
            },
            'image/jpeg',
            0.8
          )
        }
      }
      reader.onerror = reject
    })
  }

  const handleFileSelect = async (files: FileList | null) => {
    if (!files) return

    const remainingSlots = maxPhotos - photos.length
    if (remainingSlots <= 0) {
      alert(`Máximo ${maxPhotos} fotos permitidas`)
      return
    }

    setIsCompressing(true)

    const newPhotos: Photo[] = []
    const filesToProcess = Array.from(files).slice(0, remainingSlots)

    for (const file of filesToProcess) {
      if (!file.type.startsWith('image/')) {
        continue
      }

      try {
        const compressed = await compressImage(file)
        const preview = URL.createObjectURL(file)

        newPhotos.push({
          id: `${Date.now()}-${Math.random()}`,
          file,
          preview,
          compressed
        })
      } catch (error) {
        console.error('Error compressing image:', error)
      }
    }

    const updatedPhotos = [...photos, ...newPhotos]
    setPhotos(updatedPhotos)
    onPhotosChange?.(updatedPhotos)
    setIsCompressing(false)
  }

  const removePhoto = (id: string) => {
    const photo = photos.find(p => p.id === id)
    if (photo) {
      URL.revokeObjectURL(photo.preview)
    }
    const updatedPhotos = photos.filter(p => p.id !== id)
    setPhotos(updatedPhotos)
    onPhotosChange?.(updatedPhotos)
  }

  const handleFileInputClick = () => {
    fileInputRef.current?.click()
  }

  const handleCameraClick = () => {
    cameraInputRef.current?.click()
  }

  const getPhotoSizeInfo = (photo: Photo) => {
    const originalSize = (photo.file.size / 1024).toFixed(0) // KB
    const compressedSize = photo.compressed ? (photo.compressed.size / 1024).toFixed(0) : originalSize
    return { originalSize, compressedSize }
  }

  return (
    <div className="space-y-4">
      {/* Información de almacenamiento */}
      <div className="bg-muted/50 p-3 rounded-md">
        <p className="text-sm text-muted-foreground">
          <strong>Ubicación:</strong> Google Drive / {patientName || '[Nombre Paciente]'} / {sessionLabel}
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          Las fotos se comprimen automáticamente para optimizar el espacio ({photos.length}/{maxPhotos} fotos)
        </p>
      </div>

      {/* Botones de acción */}
      <div className="flex gap-3">
        <Button
          type="button"
          variant="outline"
          onClick={handleFileInputClick}
          disabled={photos.length >= maxPhotos || isCompressing}
          className="flex-1"
        >
          <Upload className="h-4 w-4 mr-2" />
          Subir Fotos
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={handleCameraClick}
          disabled={photos.length >= maxPhotos || isCompressing}
          className="flex-1"
        >
          <Camera className="h-4 w-4 mr-2" />
          Tomar Foto
        </Button>
      </div>

      {/* Inputs ocultos */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        multiple
        onChange={(e) => handleFileSelect(e.target.files)}
        className="hidden"
      />
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        onChange={(e) => handleFileSelect(e.target.files)}
        className="hidden"
      />

      {/* Indicador de compresión */}
      {isCompressing && (
        <div className="text-center py-4">
          <p className="text-sm text-muted-foreground">Comprimiendo fotos...</p>
        </div>
      )}

      {/* Grid de fotos */}
      {photos.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {photos.map((photo, index) => {
            const { originalSize, compressedSize } = getPhotoSizeInfo(photo)
            return (
              <div
                key={photo.id}
                className="relative group aspect-square rounded-lg overflow-hidden border-2 border-border bg-muted"
              >
                <Image
                  src={photo.preview}
                  alt={`Foto ${index + 1}`}
                  fill
                  className="object-cover"
                />
                <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center text-white text-xs p-2">
                  <p className="font-medium">Foto {index + 1}</p>
                  <p className="mt-1">Original: {originalSize} KB</p>
                  <p>Comprimida: {compressedSize} KB</p>
                </div>
                <button
                  type="button"
                  onClick={() => removePhoto(photo.id)}
                  className="absolute top-2 right-2 p-1 bg-destructive text-destructive-foreground rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-destructive/90"
                >
                  <X className="h-4 w-4" />
                </button>
                <div className="absolute bottom-2 left-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                  #{index + 1}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Placeholder cuando no hay fotos */}
      {photos.length === 0 && !isCompressing && (
        <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
          <ImageIcon className="h-12 w-12 mx-auto text-muted-foreground/50 mb-3" />
          <p className="text-sm text-muted-foreground">No hay fotos agregadas</p>
          <p className="text-xs text-muted-foreground mt-1">
            Usa los botones de arriba para agregar fotos
          </p>
        </div>
      )}
    </div>
  )
}
