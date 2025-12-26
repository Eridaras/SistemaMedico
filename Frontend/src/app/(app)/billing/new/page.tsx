"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
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
  FileText,
  Loader2
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { PageTransition } from "@/components/page-transition";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";

interface Product {
  product_id: number;
  name: string;
  unit_price: number;
  current_stock: number;
}

interface Patient {
  patient_id: number;
  full_name: string;
  identification: string;
  phone: string;
}

interface InvoiceItem {
  id: number;
  product_id?: number;
  name: string;
  quantity: number;
  price: number;
  discount: number;
}

export default function NewBillingPage() {
  const router = useRouter();
  const { toast } = useToast();

  const [items, setItems] = React.useState<InvoiceItem[]>([]);
  const [selectedPatient, setSelectedPatient] = React.useState<Patient | null>(null);
  const [searchPatient, setSearchPatient] = React.useState("");
  const [searchProduct, setSearchProduct] = React.useState("");
  const [products, setProducts] = React.useState<Product[]>([]);
  const [paymentMethod, setPaymentMethod] = React.useState("Efectivo");
  const [loading, setLoading] = React.useState(false);
  const [searchingPatient, setSearchingPatient] = React.useState(false);
  const [searchingProduct, setSearchingProduct] = React.useState(false);

  // Search patient by identification
  const handleSearchPatient = async () => {
    if (!searchPatient.trim()) return;

    setSearchingPatient(true);
    try {
      const res = await fetch(`/api/historia-clinica/patients/search?identification=${searchPatient}`);
      const data = await res.json();

      if (data.success && data.data) {
        setSelectedPatient(data.data);
        toast({
          title: "Paciente encontrado",
          description: `${data.data.full_name} - ${data.data.identification}`,
        });
      } else {
        toast({
          title: "Paciente no encontrado",
          description: "Verifique el número de cédula",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "No se pudo buscar el paciente",
        variant: "destructive",
      });
    } finally {
      setSearchingPatient(false);
    }
  };

  // Search products
  const handleSearchProduct = async () => {
    if (!searchProduct.trim()) return;

    setSearchingProduct(true);
    try {
      const res = await fetch(`/api/inventario/products?search=${searchProduct}`);
      const data = await res.json();

      if (data.success && data.data.products) {
        setProducts(data.data.products);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "No se pudo buscar productos",
        variant: "destructive",
      });
    } finally {
      setSearchingProduct(false);
    }
  };

  // Add product to invoice
  const handleAddProduct = (product: Product) => {
    const exists = items.find(item => item.product_id === product.product_id);

    if (exists) {
      setItems(items.map(item =>
        item.product_id === product.product_id
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setItems([...items, {
        id: Date.now(),
        product_id: product.product_id,
        name: product.name,
        quantity: 1,
        price: parseFloat(product.unit_price.toString()),
        discount: 0
      }]);
    }

    setSearchProduct("");
    setProducts([]);
  };

  // Remove item
  const handleRemoveItem = (id: number) => {
    setItems(items.filter(item => item.id !== id));
  };

  // Update quantity
  const handleQuantityChange = (id: number, quantity: number) => {
    if (quantity < 1) return;
    setItems(items.map(item =>
      item.id === id ? { ...item, quantity } : item
    ));
  };

  // Update discount
  const handleDiscountChange = (id: number, discount: number) => {
    if (discount < 0 || discount > 100) return;
    setItems(items.map(item =>
      item.id === id ? { ...item, discount } : item
    ));
  };

  // Calculations
  const subtotal = items.reduce((acc, item) => {
    const itemTotal = item.price * item.quantity;
    const discountAmount = itemTotal * (item.discount / 100);
    return acc + (itemTotal - discountAmount);
  }, 0);

  const totalDiscount = items.reduce((acc, item) => {
    return acc + (item.price * item.quantity * (item.discount / 100));
  }, 0);

  const ivaPercentage = 15; // Ecuador IVA 15%
  const iva = subtotal * (ivaPercentage / 100);
  const total = subtotal + iva;

  // Create invoice
  const handleCreateInvoice = async (isDraft: boolean = false) => {
    if (!selectedPatient) {
      toast({
        title: "Error",
        description: "Debe seleccionar un paciente",
        variant: "destructive",
      });
      return;
    }

    if (items.length === 0) {
      toast({
        title: "Error",
        description: "Debe agregar al menos un producto",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);

    try {
      const payload = {
        patient_id: selectedPatient.patient_id,
        subtotal: subtotal,
        iva_percentage: ivaPercentage,
        iva: iva,
        total: total,
        payment_method: paymentMethod,
        status: isDraft ? 'pending' : 'paid',
        items: items.map(item => ({
          product_id: item.product_id,
          quantity: item.quantity,
          unit_price: item.price,
          discount_percentage: item.discount
        }))
      };

      const res = await fetch('/api/facturacion/invoices', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      if (data.success) {
        toast({
          title: "Factura creada",
          description: `Factura #${data.data.invoice_id} generada exitosamente`,
        });
        router.push('/billing');
      } else {
        throw new Error(data.message || 'Error al crear factura');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "No se pudo crear la factura",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageTransition className="flex flex-col gap-8 w-full max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Nueva Factura</h1>
          <p className="text-muted-foreground">Generar nueva factura para paciente</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => router.push('/billing')}>
            Cancelar
          </Button>
          <Button
            variant="outline"
            onClick={() => handleCreateInvoice(true)}
            disabled={loading || !selectedPatient || items.length === 0}
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Save className="mr-2 h-4 w-4" />}
            Guardar Borrador
          </Button>
          <Button
            onClick={() => handleCreateInvoice(false)}
            disabled={loading || !selectedPatient || items.length === 0}
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <FileText className="mr-2 h-4 w-4" />}
            Generar Factura
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Patient Search */}
          <Card>
            <CardHeader>
              <CardTitle>Información del Paciente</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2 mb-4">
                <Input
                  placeholder="Buscar por cédula..."
                  value={searchPatient}
                  onChange={(e) => setSearchPatient(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearchPatient()}
                />
                <Button onClick={handleSearchPatient} disabled={searchingPatient}>
                  {searchingPatient ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                </Button>
              </div>

              {selectedPatient && (
                <div className="p-4 bg-muted rounded-lg">
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <p className="text-sm text-muted-foreground">Nombre</p>
                      <p className="font-medium">{selectedPatient.full_name}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Cédula</p>
                      <p className="font-medium">{selectedPatient.identification}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Teléfono</p>
                      <p className="font-medium">{selectedPatient.phone}</p>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Products Search */}
          <Card>
            <CardHeader>
              <CardTitle>Agregar Productos/Servicios</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2 mb-4">
                <Input
                  placeholder="Buscar productos..."
                  value={searchProduct}
                  onChange={(e) => setSearchProduct(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearchProduct()}
                />
                <Button onClick={handleSearchProduct} disabled={searchingProduct}>
                  {searchingProduct ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                </Button>
              </div>

              {products.length > 0 && (
                <div className="space-y-2">
                  {products.map(product => (
                    <div
                      key={product.product_id}
                      className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted cursor-pointer"
                      onClick={() => handleAddProduct(product)}
                    >
                      <div>
                        <p className="font-medium">{product.name}</p>
                        <p className="text-sm text-muted-foreground">Stock: {product.current_stock}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">${product.unit_price.toFixed(2)}</p>
                        <Button size="sm" variant="ghost">
                          <PlusCircle className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Items Table */}
          <Card>
            <CardHeader>
              <CardTitle>Detalles de la Factura</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Producto</TableHead>
                    <TableHead className="text-center">Cantidad</TableHead>
                    <TableHead className="text-right">Precio</TableHead>
                    <TableHead className="text-center">Descuento %</TableHead>
                    <TableHead className="text-right">Total</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {items.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell className="font-medium">{item.name}</TableCell>
                      <TableCell className="text-center">
                        <Input
                          type="number"
                          value={item.quantity}
                          onChange={(e) => handleQuantityChange(item.id, parseInt(e.target.value) || 1)}
                          className="w-20 text-center"
                          min="1"
                        />
                      </TableCell>
                      <TableCell className="text-right">${item.price.toFixed(2)}</TableCell>
                      <TableCell className="text-center">
                        <Input
                          type="number"
                          value={item.discount}
                          onChange={(e) => handleDiscountChange(item.id, parseFloat(e.target.value) || 0)}
                          className="w-20 text-center"
                          min="0"
                          max="100"
                        />
                      </TableCell>
                      <TableCell className="text-right font-medium">
                        ${((item.price * item.quantity) * (1 - item.discount / 100)).toFixed(2)}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleRemoveItem(item.id)}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                  {items.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                        No hay productos agregados. Busque y agregue productos arriba.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>

        {/* Summary Sidebar */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Resumen</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Subtotal</span>
                  <span className="font-medium">${subtotal.toFixed(2)}</span>
                </div>
                {totalDiscount > 0 && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Descuentos</span>
                    <span className="font-medium text-green-600">-${totalDiscount.toFixed(2)}</span>
                  </div>
                )}
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">IVA ({ivaPercentage}%)</span>
                  <span className="font-medium">${iva.toFixed(2)}</span>
                </div>
                <Separator />
                <div className="flex justify-between">
                  <span className="font-semibold">Total</span>
                  <span className="font-bold text-xl">${total.toFixed(2)}</span>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Método de Pago</label>
                <Select value={paymentMethod} onValueChange={setPaymentMethod}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Efectivo">Efectivo</SelectItem>
                    <SelectItem value="Tarjeta">Tarjeta</SelectItem>
                    <SelectItem value="Transferencia">Transferencia</SelectItem>
                    <SelectItem value="Cheque">Cheque</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageTransition>
  );
}
