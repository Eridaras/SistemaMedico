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
  Plus,
  Loader2
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { PageTransition } from "@/components/page-transition";
import { auth } from "@/lib/auth";

// TypeScript Interfaces
interface Invoice {
  invoice_id: number;
  patient_id: number;
  patient_name: string;
  invoice_number: string;
  fecha_emision: string;
  estado_sri: 'PENDIENTE' | 'AUTORIZADO' | 'RECHAZADO' | 'ANULADO';
  subtotal_0: number;
  subtotal_15: number;
  iva: number;
  total: number;
  payment_method: string;
}

interface Stats {
  total_ingresos: number;
  total_egresos: number;
  facturas_emitidas: number;
  facturas_pendientes: number;
}

export default function BillingListPage() {
  const [invoices, setInvoices] = React.useState<Invoice[]>([]);
  const [stats, setStats] = React.useState<Stats | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState("");
  const [searchTerm, setSearchTerm] = React.useState("");

  // Fetch invoices from backend
  const fetchInvoices = React.useCallback(async (search: string = "") => {
    try {
      setLoading(true);
      const query = search ? `?search=${encodeURIComponent(search)}` : "";

      const response = await fetch(`/api/facturacion/invoices${query}`, {
        headers: {
          'Authorization': `Bearer ${auth.getToken()}`
        }
      });

      if (!response.ok) throw new Error("Error al cargar facturas");

      const data = await response.json();
      if (data.success && data.data) {
        setInvoices(data.data.invoices || []);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido");
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch stats from backend
  const fetchStats = React.useCallback(async () => {
    try {
      const response = await fetch('/api/facturacion/dashboard/stats', {
        headers: {
          'Authorization': `Bearer ${auth.getToken()}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.data) {
          setStats(data.data);
        }
      }
    } catch (err) {
      console.error("Error loading stats:", err);
    }
  }, []);

  React.useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  React.useEffect(() => {
    const timer = setTimeout(() => {
      fetchInvoices(searchTerm);
    }, 500);
    return () => clearTimeout(timer);
  }, [searchTerm, fetchInvoices]);

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
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6 flex flex-col gap-1">
            <p className="text-sm font-medium text-muted-foreground">Total Ingresos</p>
            <div className="text-2xl font-bold">${stats?.total_ingresos.toFixed(2) || '0.00'}</div>
            <p className="text-xs font-medium text-green-600 dark:text-green-500">+8.2%</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 flex flex-col gap-1">
            <p className="text-sm font-medium text-muted-foreground">Total Egresos</p>
            <div className="text-2xl font-bold">${stats?.total_egresos.toFixed(2) || '0.00'}</div>
            <p className="text-xs font-medium text-red-600 dark:text-red-500">-3.1%</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 flex flex-col gap-1">
            <p className="text-sm font-medium text-muted-foreground">Facturas Emitidas</p>
            <div className="text-2xl font-bold">{stats?.facturas_emitidas.toString() || '0'}</div>
            <p className="text-xs font-medium text-green-600 dark:text-green-500">+12</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 flex flex-col gap-1">
            <p className="text-sm font-medium text-muted-foreground">Pendientes</p>
            <div className="text-2xl font-bold">{stats?.facturas_pendientes.toString() || '0'}</div>
            <p className="text-xs font-medium text-yellow-600 dark:text-yellow-500">-2</p>
          </CardContent>
        </Card>
      </div>

      {/* Table Section */}
      <div className="bg-card rounded-xl border border-border shadow-sm overflow-hidden">
        {/* Toolbar */}
        <div className="flex flex-col md:flex-row items-center justify-between p-4 border-b border-border gap-4">
          <div className="relative w-full md:w-64">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar..."
              className="pl-9"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
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
              <TableHead>Factura N°</TableHead>
              <TableHead>Fecha</TableHead>
              <TableHead>Cliente</TableHead>
              <TableHead>Tipo</TableHead>
              <TableHead>Estado</TableHead>
              <TableHead>Total</TableHead>
              <TableHead className="text-right">Acciones</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} className="h-24 text-center">
                  <div className="flex justify-center items-center gap-2 text-muted-foreground">
                    <Loader2 className="h-4 w-4 animate-spin" /> Cargando facturas...
                  </div>
                </TableCell>
              </TableRow>
            ) : error ? (
              <TableRow>
                <TableCell colSpan={7} className="h-24 text-center text-red-500">
                  Error: {error}
                </TableCell>
              </TableRow>
            ) : invoices.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="h-24 text-center text-muted-foreground">
                  No se encontraron facturas
                </TableCell>
              </TableRow>
            ) : (
              invoices.map((invoice) => (
                <TableRow key={invoice.invoice_id} className="hover:bg-muted/30 transition-colors">
                  <TableCell className="font-medium">{invoice.invoice_number}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {new Date(invoice.fecha_emision).toLocaleDateString('es-ES')}
                  </TableCell>
                  <TableCell className="font-medium">{invoice.patient_name}</TableCell>
                  <TableCell className="text-muted-foreground">Factura</TableCell>
                  <TableCell>
                    <Badge variant={
                      invoice.estado_sri === 'AUTORIZADO' ? 'default' :
                      invoice.estado_sri === 'PENDIENTE' ? 'secondary' :
                      'destructive'
                    }>
                      {invoice.estado_sri}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground font-medium">${invoice.total.toFixed(2)}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm">Ver Detalle</Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </PageTransition>
  );
}
