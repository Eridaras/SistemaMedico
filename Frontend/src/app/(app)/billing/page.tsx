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
  Filter,
  Calendar,
  Download,
  MoreHorizontal,
  Plus
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { PageTransition } from "@/components/page-transition";

// Mock Data
const movements = [
  { id: 'FAC-00125', date: '15/07/2024', client: 'Carlos Ramirez', type: 'Venta', status: 'Pagada', total: 150.00 },
  { id: 'FAC-00124', date: '14/07/2024', client: 'Ana Torres', type: 'Venta', status: 'Pendiente', total: 200.00 },
  { id: 'COMP-0087', date: '13/07/2024', client: 'Proveedor Médico SA', type: 'Compra', status: 'Pagada', total: 850.00 },
  { id: 'FAC-00123', date: '12/07/2024', client: 'Luisa Fernandez', type: 'Venta', status: 'Anulada', total: 75.00 },
  { id: 'FAC-00122', date: '11/07/2024', client: 'Jorge Mendoza', type: 'Venta', status: 'Pagada', total: 150.00 },
];

export default function BillingListPage() {
  return (
    <PageTransition className="flex flex-col gap-8 w-full max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-wrap justify-between items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Listado de Movimientos</h1>
          <p className="text-muted-foreground">Gestión de facturas y transacciones.</p>
        </div>
        <div className="flex gap-2">
          <Button asChild className="gap-2">
            <Link href="/billing/new">
              <Plus className="h-4 w-4" /> Registrar Movimiento
            </Link>
          </Button>
          <Button variant="outline" size="icon">
            <span className="sr-only">Notificaciones</span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-4 w-4"
            >
              <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
              <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
            </svg>
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6 flex flex-col gap-1">
            <p className="text-sm font-medium text-muted-foreground">Facturado este mes</p>
            <div className="text-2xl font-bold">$12,500.00</div>
            <p className="text-xs font-medium text-green-600 dark:text-green-500">+5.2%</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 flex flex-col gap-1">
            <p className="text-sm font-medium text-muted-foreground">Pendiente de cobro</p>
            <div className="text-2xl font-bold">$3,200.00</div>
            <p className="text-xs font-medium text-green-600 dark:text-green-500">+1.8%</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 flex flex-col gap-1">
            <p className="text-sm font-medium text-muted-foreground">Total Anulado</p>
            <div className="text-2xl font-bold">$850.00</div>
            <p className="text-xs font-medium text-red-600 dark:text-red-500">-0.5%</p>
          </CardContent>
        </Card>
      </div>

      {/* Table Section */}
      <div className="bg-card rounded-xl border border-border shadow-sm overflow-hidden">
        {/* Toolbar */}
        <div className="flex flex-col md:flex-row items-center justify-between p-4 border-b border-border gap-4">
          <div className="relative w-full md:w-64">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Buscar..." className="pl-9" />
          </div>
          <div className="flex gap-2 w-full md:w-auto">
            <Button variant="outline" size="icon">
              <Filter className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon">
              <Calendar className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon">
              <Download className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Table */}
        <Table>
          <TableHeader className="bg-muted/50">
            <TableRow>
              <TableHead className="w-12 text-center">
                <Input type="checkbox" className="h-4 w-4 translate-y-0.5" />
              </TableHead>
              <TableHead>Factura N°</TableHead>
              <TableHead>Fecha</TableHead>
              <TableHead>Cliente/Proveedor</TableHead>
              <TableHead>Tipo</TableHead>
              <TableHead>Estado</TableHead>
              <TableHead>Total</TableHead>
              <TableHead className="text-right">Acciones</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {movements.map((item) => (
              <TableRow key={item.id} className="hover:bg-muted/30 transition-colors">
                <TableCell className="text-center">
                  <Input type="checkbox" className="h-4 w-4 translate-y-0.5" />
                </TableCell>
                <TableCell className="font-medium text-muted-foreground">{item.id}</TableCell>
                <TableCell className="text-muted-foreground">{item.date}</TableCell>
                <TableCell className="font-medium">{item.client}</TableCell>
                <TableCell className="text-muted-foreground">{item.type}</TableCell>
                <TableCell>
                  <Badge variant="outline" className={`
                                border-0 px-2 py-0.5 rounded-full text-xs font-medium
                                ${item.status === 'Pagada' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : ''}
                                ${item.status === 'Pendiente' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300' : ''}
                                ${item.status === 'Anulada' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300' : ''}
                            `}>
                    {item.status}
                  </Badge>
                </TableCell>
                <TableCell className="text-muted-foreground font-medium">${item.total.toFixed(2)}</TableCell>
                <TableCell className="text-right">
                  <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-primary">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </PageTransition>
  );
}
