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
  Trash2,
  PlusCircle,
  Save,
  FileText
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { PageTransition } from "@/components/page-transition";

// Mock Data
const initialItems = [
  { id: 1, name: "Consulta General Especializada", quantity: 1, price: 150000, discount: 10 },
  { id: 2, name: "Kit de Bioseguridad", quantity: 1, price: 25000, discount: 0 },
];

export default function BillingPage() {
  const [items, setItems] = React.useState(initialItems);

  // Calculations
  const subtotal = items.reduce((acc, item) => {
    const itemTotal = item.price * item.quantity;
    const discountAmount = itemTotal * (item.discount / 100);
    return acc + (itemTotal - discountAmount);
  }, 0);

  const totalDiscount = items.reduce((acc, item) => {
    return acc + (item.price * item.quantity * (item.discount / 100));
  }, 0);

  const tax = subtotal * 0.19; // 19% IVA
  const total = subtotal + tax;

  return (
    <PageTransition className="flex flex-col gap-8 w-full max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-wrap justify-between items-center gap-4">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-foreground">Generar Nueva Factura</h1>
          <p className="text-muted-foreground">Crea y envía facturas a tus pacientes de forma rápida y sencilla.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" className="gap-2">
            <Save className="h-4 w-4" /> Guardar Borrador
          </Button>
          <Button className="gap-2">
            <FileText className="h-4 w-4" /> Generar Factura
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 flex flex-col gap-6">
          {/* Patient Data */}
          <Card>
            <CardHeader>
              <CardTitle>Datos del Paciente</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Buscar Paciente</label>
                  <div className="relative">
                    <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input placeholder="Escribe el nombre o DNI" className="pl-9" defaultValue="Ana María Torres" />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Fecha de Factura</label>
                  <Input type="date" defaultValue="2023-10-27" />
                </div>
                <div className="md:col-span-2 space-y-2">
                  <label className="text-sm font-medium">Descripción (Opcional)</label>
                  <Input placeholder="Ej: Consulta de seguimiento, procedimiento dental, etc." />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Invoice Items */}
          <Card>
            <CardHeader>
              <CardTitle>Detalles de la Factura</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Producto / Servicio</TableHead>
                    <TableHead className="w-24">Cant.</TableHead>
                    <TableHead className="w-32">Precio Unit.</TableHead>
                    <TableHead className="w-24">Desc. %</TableHead>
                    <TableHead className="text-right">Subtotal</TableHead>
                    <TableHead className="w-12"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {items.map((item) => {
                    const itemTotal = item.price * item.quantity * (1 - item.discount / 100);
                    return (
                      <TableRow key={item.id}>
                        <TableCell className="font-medium">{item.name}</TableCell>
                        <TableCell>{item.quantity}</TableCell>
                        <TableCell>${item.price.toLocaleString()}</TableCell>
                        <TableCell>
                          <Input className="h-8 w-16" defaultValue={item.discount} />
                        </TableCell>
                        <TableCell className="text-right font-medium">${itemTotal.toLocaleString()}</TableCell>
                        <TableCell>
                          <Button variant="ghost" size="icon" className="hover:text-red-500 hover:bg-red-50">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
              <Button variant="ghost" className="mt-4 gap-2 text-primary hover:text-primary hover:bg-primary/10 w-full justify-start">
                <PlusCircle className="h-4 w-4" />
                Agregar producto o servicio
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Summary Side Panel */}
        <div className="lg:col-span-1">
          <Card className="sticky top-6">
            <CardHeader>
              <CardTitle>Resumen de Pago</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between text-muted-foreground">
                <span>Subtotal</span>
                <span className="text-foreground font-medium">${subtotal.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-muted-foreground">
                <span>Descuentos</span>
                <span className="text-red-500 font-medium">-${totalDiscount.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-muted-foreground">
                <span>Impuestos (IVA 19%)</span>
                <span className="text-foreground font-medium">${tax.toLocaleString()}</span>
              </div>
              <Separator />
              <div className="flex justify-between text-xl font-bold">
                <span>Total a Pagar</span>
                <span>${total.toLocaleString()}</span>
              </div>

              <div className="pt-4 space-y-3">
                <Button className="w-full h-12 text-base shadow-md">
                  Generar y Enviar Factura
                </Button>
                <Button variant="outline" className="w-full h-12 text-base">
                  Guardar Borrador
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageTransition>
  );
}
