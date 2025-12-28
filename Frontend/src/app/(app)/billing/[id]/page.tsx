"use client";

import * as React from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { PageTransition } from "@/components/page-transition";
import { auth } from "@/lib/auth";
import { useToast } from "@/hooks/use-toast";
import { Loader2, ArrowLeft, Printer, FileDown, Mail } from "lucide-react";
import Link from "next/link";
import { format } from "date-fns";
import { es } from "date-fns/locale";

interface InvoiceItem {
  item_id: number;
  product_id: number;
  product_name: string;
  quantity: number;
  unit_price: number;
  discount: number;
  subtotal: number;
}

interface Invoice {
  invoice_id: number;
  invoice_number: string;
  patient_id: number;
  patient_name: string;
  patient_doc_number: string;
  invoice_date: string;
  due_date: string;
  subtotal: number;
  tax: number;
  discount: number;
  total: number;
  status: string;
  payment_method: string;
  notes: string;
  items: InvoiceItem[];
}

export default function InvoiceDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const invoiceId = params.id as string;

  const [loading, setLoading] = React.useState(true);
  const [invoice, setInvoice] = React.useState<Invoice | null>(null);

  React.useEffect(() => {
    const fetchInvoice = async () => {
      try {
        const response = await fetch(`/api/facturacion/invoices/${invoiceId}`, {
          headers: {
            'Authorization': `Bearer ${auth.getToken()}`
          }
        });

        if (!response.ok) throw new Error("Error al cargar factura");

        const data = await response.json();
        if (data.success && data.data) {
          setInvoice(data.data.invoice);
        }
      } catch (error) {
        console.error(error);
        toast({
          title: "Error",
          description: "No se pudo cargar la factura",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchInvoice();
  }, [invoiceId, toast]);

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadPDF = () => {
    toast({
      title: "Función en desarrollo",
      description: "La descarga de PDF estará disponible próximamente",
    });
  };

  const handleSendEmail = () => {
    toast({
      title: "Función en desarrollo",
      description: "El envío por email estará disponible próximamente",
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'overdue':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'cancelled':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'paid':
        return 'Pagada';
      case 'pending':
        return 'Pendiente';
      case 'overdue':
        return 'Vencida';
      case 'cancelled':
        return 'Cancelada';
      case 'draft':
        return 'Borrador';
      default:
        return status;
    }
  };

  if (loading) {
    return (
      <PageTransition className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>Cargando factura...</span>
        </div>
      </PageTransition>
    );
  }

  if (!invoice) {
    return (
      <PageTransition className="flex flex-col items-center justify-center min-h-[400px] gap-4">
        <p className="text-muted-foreground">Factura no encontrada</p>
        <Link href="/billing">
          <Button variant="outline">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver al listado
          </Button>
        </Link>
      </PageTransition>
    );
  }

  return (
    <PageTransition className="flex flex-col gap-6 w-full max-w-5xl mx-auto">
      {/* Header - Oculto al imprimir */}
      <div className="flex items-center justify-between print:hidden">
        <div className="flex items-center gap-4">
          <Link href="/billing">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              Factura #{invoice.invoice_number}
            </h1>
            <p className="text-muted-foreground">
              {format(new Date(invoice.invoice_date), "PPP", { locale: es })}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleSendEmail}>
            <Mail className="h-4 w-4 mr-2" />
            Enviar Email
          </Button>
          <Button variant="outline" size="sm" onClick={handleDownloadPDF}>
            <FileDown className="h-4 w-4 mr-2" />
            Descargar PDF
          </Button>
          <Button size="sm" onClick={handlePrint}>
            <Printer className="h-4 w-4 mr-2" />
            Imprimir
          </Button>
        </div>
      </div>

      {/* Factura - Diseño para impresión */}
      <Card className="print:shadow-none print:border-0">
        <CardContent className="p-8 space-y-8">
          {/* Header de la Factura */}
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-3xl font-bold text-primary">Clínica Bienestar</h2>
              <p className="text-sm text-muted-foreground mt-1">
                Sistema de Gestión Médica
              </p>
              <p className="text-sm text-muted-foreground">
                Quito, Ecuador
              </p>
            </div>

            <div className="text-right">
              <Badge variant="outline" className={`${getStatusColor(invoice.status)} border-0 text-sm px-3 py-1 mb-2`}>
                {getStatusLabel(invoice.status)}
              </Badge>
              <p className="text-2xl font-bold">#{invoice.invoice_number}</p>
              <p className="text-sm text-muted-foreground">
                Fecha: {format(new Date(invoice.invoice_date), "dd/MM/yyyy")}
              </p>
            </div>
          </div>

          <Separator />

          {/* Información del Paciente */}
          <div className="grid grid-cols-2 gap-8">
            <div>
              <h3 className="text-sm font-semibold text-muted-foreground mb-2">FACTURADO A:</h3>
              <p className="font-semibold text-lg">{invoice.patient_name}</p>
              <p className="text-sm text-muted-foreground">CI: {invoice.patient_doc_number}</p>
            </div>

            <div className="text-right">
              <h3 className="text-sm font-semibold text-muted-foreground mb-2">DETALLES:</h3>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Fecha de Emisión:</span>
                  <span className="font-medium">{format(new Date(invoice.invoice_date), "dd/MM/yyyy")}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Fecha de Vencimiento:</span>
                  <span className="font-medium">{format(new Date(invoice.due_date), "dd/MM/yyyy")}</span>
                </div>
                {invoice.payment_method && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Método de Pago:</span>
                    <span className="font-medium capitalize">{invoice.payment_method}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          <Separator />

          {/* Items de la Factura */}
          <div>
            <h3 className="text-sm font-semibold text-muted-foreground mb-4">PRODUCTOS/SERVICIOS</h3>
            <div className="border rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-muted/50">
                  <tr className="border-b">
                    <th className="text-left p-3 text-sm font-semibold">Descripción</th>
                    <th className="text-center p-3 text-sm font-semibold">Cantidad</th>
                    <th className="text-right p-3 text-sm font-semibold">Precio Unit.</th>
                    <th className="text-right p-3 text-sm font-semibold">Descuento</th>
                    <th className="text-right p-3 text-sm font-semibold">Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  {invoice.items.map((item, index) => (
                    <tr key={item.item_id} className={index !== invoice.items.length - 1 ? "border-b" : ""}>
                      <td className="p-3 text-sm">{item.product_name}</td>
                      <td className="p-3 text-sm text-center">{item.quantity}</td>
                      <td className="p-3 text-sm text-right">${item.unit_price.toFixed(2)}</td>
                      <td className="p-3 text-sm text-right">${item.discount.toFixed(2)}</td>
                      <td className="p-3 text-sm text-right font-medium">${item.subtotal.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Totales */}
          <div className="flex justify-end">
            <div className="w-80 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Subtotal:</span>
                <span className="font-medium">${invoice.subtotal.toFixed(2)}</span>
              </div>

              {invoice.discount > 0 && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Descuento:</span>
                  <span className="font-medium text-red-600">-${invoice.discount.toFixed(2)}</span>
                </div>
              )}

              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">IVA (15%):</span>
                <span className="font-medium">${invoice.tax.toFixed(2)}</span>
              </div>

              <Separator />

              <div className="flex justify-between text-lg font-bold">
                <span>TOTAL:</span>
                <span className="text-primary">${invoice.total.toFixed(2)}</span>
              </div>
            </div>
          </div>

          {/* Notas */}
          {invoice.notes && (
            <>
              <Separator />
              <div>
                <h3 className="text-sm font-semibold text-muted-foreground mb-2">NOTAS:</h3>
                <p className="text-sm text-muted-foreground whitespace-pre-wrap">{invoice.notes}</p>
              </div>
            </>
          )}

          {/* Footer */}
          <Separator className="print:block hidden" />
          <div className="text-center text-xs text-muted-foreground print:block hidden">
            <p>Gracias por confiar en Clínica Bienestar</p>
            <p className="mt-1">Este documento es una representación impresa de una factura electrónica</p>
          </div>
        </CardContent>
      </Card>
    </PageTransition>
  );
}
