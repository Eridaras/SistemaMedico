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
    Edit,
    Download,
    PlusCircle,
    Loader2
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { PageTransition } from "@/components/page-transition";
import { auth } from "@/lib/auth";

interface Product {
    product_id: number;
    sku: string;
    name: string;
    description: string;
    stock_quantity: number;
    min_stock_alert: number;
    sale_price: number;
    category?: string; // Optional if not returned by listing
}

export default function InventoryPage() {
    const [searchTerm, setSearchTerm] = React.useState("");
    const [products, setProducts] = React.useState<Product[]>([]);
    const [loading, setLoading] = React.useState(true);

    const fetchProducts = React.useCallback(async (search: string = "") => {
        try {
            setLoading(true);
            const query = search ? `?search=${encodeURIComponent(search)}` : "";
            const response = await fetch(`/api/inventario/products${query}`, {
                headers: {
                    'Authorization': `Bearer ${auth.getToken()}`
                }
            });

            if (!response.ok) throw new Error("Error fetching products");

            const data = await response.json();

            // API returns { success: true, data: { products: [] } } or similar
            if (data.success && data.data && data.data.products) {
                setProducts(data.data.products);
            } else {
                setProducts([]);
            }
        } catch (error) {
            console.error(error);
            setProducts([]);
        } finally {
            setLoading(false);
        }
    }, []);

    // Debounce search
    React.useEffect(() => {
        const timer = setTimeout(() => {
            fetchProducts(searchTerm);
        }, 500);
        return () => clearTimeout(timer);
    }, [searchTerm, fetchProducts]);

    const getStockStatus = (stock: number, min: number) => {
        if (stock === 0) return { label: 'Agotado', variant: 'destructive', color: 'bg-red-100 text-red-800 border-red-200' };
        if (stock <= min) return { label: 'Stock Bajo', variant: 'warning', color: 'bg-yellow-100 text-yellow-800 border-yellow-200' };
        return { label: 'En Stock', variant: 'success', color: 'bg-green-100 text-green-800 border-green-200' };
    };

    return (
        <PageTransition className="flex flex-col gap-6 w-full max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex flex-wrap justify-between items-center gap-4">
                <h1 className="text-2xl font-bold tracking-tight text-foreground">Gestión de Inventario</h1>
            </div>

            {/* Search and Actions */}
            <div className="flex flex-col sm:flex-row justify-between items-center gap-4 bg-card p-4 rounded-xl border border-border shadow-sm">
                <div className="w-full sm:max-w-md relative">
                    <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder="Buscar por nombre o SKU..."
                        className="pl-9"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
                <div className="flex w-full sm:w-auto gap-3">
                    <Button variant="outline" className="flex-1 sm:flex-none gap-2">
                        <Download className="h-4 w-4" /> Exportar
                    </Button>
                    <Button className="flex-1 sm:flex-none gap-2">
                        <PlusCircle className="h-4 w-4" /> Añadir Producto
                    </Button>
                </div>
            </div>

            {/* Categories / Filters - TODO: Connect to dynamic categories */}
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin">
                {['Todo', 'Medicamentos', 'Insumos', 'Equipos'].map((cat, i) => (
                    <Button
                        key={cat}
                        variant={i === 0 ? "secondary" : "ghost"}
                        className={`rounded-full h-8 text-sm ${i === 0 ? "bg-primary/10 text-primary hover:bg-primary/20" : "bg-muted/50 hover:bg-muted"}`}
                    >
                        {cat}
                    </Button>
                ))}
            </div>

            {/* Inventory Table */}
            <div className="rounded-xl border border-border shadow-sm overflow-hidden bg-card">
                <Table>
                    <TableHeader className="bg-muted/30">
                        <TableRow>
                            <TableHead>Producto</TableHead>
                            <TableHead>SKU</TableHead>
                            <TableHead className="text-right">Precio Venta</TableHead>
                            <TableHead className="text-center">Existencias</TableHead>
                            <TableHead>Estado</TableHead>
                            <TableHead className="text-right">Acciones</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {loading ? (
                            <TableRow>
                                <TableCell colSpan={6} className="h-24 text-center">
                                    <div className="flex justify-center items-center gap-2 text-muted-foreground">
                                        <Loader2 className="h-4 w-4 animate-spin" /> Cargando inventario...
                                    </div>
                                </TableCell>
                            </TableRow>
                        ) : products.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={6} className="h-24 text-center text-muted-foreground">
                                    No se encontraron productos
                                </TableCell>
                            </TableRow>
                        ) : (
                            products.map((item) => {
                                const status = getStockStatus(item.stock_quantity, item.min_stock_alert);
                                return (
                                    <TableRow key={item.product_id} className="hover:bg-muted/30 transition-colors">
                                        <TableCell className="font-medium">
                                            <div>{item.name}</div>
                                            <div className="text-xs text-muted-foreground line-clamp-1">{item.description}</div>
                                        </TableCell>
                                        <TableCell className="text-muted-foreground font-mono text-xs">{item.sku}</TableCell>
                                        <TableCell className="text-right font-medium">${item.sale_price.toFixed(2)}</TableCell>
                                        <TableCell className="text-center font-medium">{item.stock_quantity}</TableCell>
                                        <TableCell>
                                            <Badge variant="outline" className={`border-0 px-2 py-0.5 rounded-full text-xs font-medium ${status.color}`}>
                                                {status.label}
                                            </Badge>
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <div className="flex items-center justify-end gap-1">
                                                <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-primary">
                                                    <Edit className="h-4 w-4" />
                                                </Button>
                                                <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-red-500">
                                                    <Trash2 className="h-4 w-4" />
                                                </Button>
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                );
                            })
                        )}
                    </TableBody>
                </Table>
            </div>
        </PageTransition>
    );
}
