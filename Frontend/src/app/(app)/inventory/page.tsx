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
    Loader2,
    Package
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { PageTransition } from "@/components/page-transition";
import { auth } from "@/lib/auth";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";

interface Product {
    product_id: number;
    sku: string;
    name: string;
    description: string;
    current_stock: number;
    minimum_stock: number;
    unit_price: number;
    category?: string;
    type?: string;
}

export default function InventoryPage() {
    const { toast } = useToast();
    const [searchTerm, setSearchTerm] = React.useState("");
    const [products, setProducts] = React.useState<Product[]>([]);
    const [loading, setLoading] = React.useState(true);

    // Edit product modal
    const [showEditModal, setShowEditModal] = React.useState(false);
    const [editingProduct, setEditingProduct] = React.useState<Product | null>(null);
    const [editForm, setEditForm] = React.useState({
        name: "",
        description: "",
        unit_price: "",
        minimum_stock: "",
        category: "",
        type: ""
    });
    const [saving, setSaving] = React.useState(false);

    // Stock adjustment modal
    const [showStockModal, setShowStockModal] = React.useState(false);
    const [stockProduct, setStockProduct] = React.useState<Product | null>(null);
    const [stockAdjustment, setStockAdjustment] = React.useState("");
    const [adjusting, setAdjusting] = React.useState(false);

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

    // Open edit modal
    const handleEdit = (product: Product) => {
        setEditingProduct(product);
        setEditForm({
            name: product.name,
            description: product.description || "",
            unit_price: product.unit_price.toString(),
            minimum_stock: product.minimum_stock.toString(),
            category: product.category || "",
            type: product.type || ""
        });
        setShowEditModal(true);
    };

    // Save edited product
    const handleSaveEdit = async () => {
        if (!editingProduct) return;

        try {
            setSaving(true);

            const payload = {
                name: editForm.name,
                description: editForm.description,
                unit_price: parseFloat(editForm.unit_price),
                minimum_stock: parseInt(editForm.minimum_stock),
                category: editForm.category,
                type: editForm.type
            };

            const response = await fetch(`/api/inventario/products/${editingProduct.product_id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${auth.getToken()}`
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (data.success) {
                toast({
                    title: "Producto actualizado",
                    description: "Los cambios se han guardado exitosamente",
                });
                setShowEditModal(false);
                fetchProducts(searchTerm);
            } else {
                throw new Error(data.message || 'Error al actualizar producto');
            }
        } catch (error) {
            toast({
                title: "Error",
                description: error instanceof Error ? error.message : "No se pudo actualizar el producto",
                variant: "destructive",
            });
        } finally {
            setSaving(false);
        }
    };

    // Open stock adjustment modal
    const handleAdjustStock = (product: Product) => {
        setStockProduct(product);
        setStockAdjustment(product.current_stock.toString());
        setShowStockModal(true);
    };

    // Save stock adjustment
    const handleSaveStock = async () => {
        if (!stockProduct) return;

        try {
            setAdjusting(true);

            const newStock = parseInt(stockAdjustment);

            if (isNaN(newStock) || newStock < 0) {
                toast({
                    title: "Error",
                    description: "La cantidad debe ser un número válido mayor o igual a 0",
                    variant: "destructive",
                });
                return;
            }

            const response = await fetch(`/api/inventario/products/${stockProduct.product_id}/stock`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${auth.getToken()}`
                },
                body: JSON.stringify({ current_stock: newStock })
            });

            const data = await response.json();

            if (data.success) {
                toast({
                    title: "Stock actualizado",
                    description: `Stock de "${stockProduct.name}" ajustado a ${newStock} unidades`,
                });
                setShowStockModal(false);
                fetchProducts(searchTerm);
            } else {
                throw new Error(data.message || 'Error al actualizar stock');
            }
        } catch (error) {
            toast({
                title: "Error",
                description: error instanceof Error ? error.message : "No se pudo actualizar el stock",
                variant: "destructive",
            });
        } finally {
            setAdjusting(false);
        }
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

                <div className="flex gap-2 w-full sm:w-auto">
                    <Button variant="outline" className="flex-1 sm:flex-initial gap-2">
                        <Download className="h-4 w-4" />
                        Exportar
                    </Button>
                    <Button className="flex-1 sm:flex-initial gap-2">
                        <PlusCircle className="h-4 w-4" />
                        Nuevo Producto
                    </Button>
                </div>
            </div>

            {/* Products Table */}
            <div className="bg-card border border-border shadow-sm rounded-xl overflow-hidden">
                <Table>
                    <TableHeader className="bg-muted/50">
                        <TableRow>
                            <TableHead>Producto</TableHead>
                            <TableHead>SKU</TableHead>
                            <TableHead className="text-right">Precio</TableHead>
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
                                const status = getStockStatus(item.current_stock, item.minimum_stock);
                                return (
                                    <TableRow key={item.product_id} className="hover:bg-muted/30 transition-colors">
                                        <TableCell className="font-medium">
                                            <div>{item.name}</div>
                                            <div className="text-xs text-muted-foreground line-clamp-1">{item.description}</div>
                                        </TableCell>
                                        <TableCell className="text-muted-foreground font-mono text-xs">{item.sku}</TableCell>
                                        <TableCell className="text-right font-medium">${item.unit_price.toFixed(2)}</TableCell>
                                        <TableCell className="text-center font-medium">
                                            <button
                                                onClick={() => handleAdjustStock(item)}
                                                className="hover:text-primary transition-colors underline decoration-dotted cursor-pointer"
                                            >
                                                {item.current_stock}
                                            </button>
                                        </TableCell>
                                        <TableCell>
                                            <Badge variant="outline" className={`border-0 px-2 py-0.5 rounded-full text-xs font-medium ${status.color}`}>
                                                {status.label}
                                            </Badge>
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <div className="flex items-center justify-end gap-1">
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    className="h-8 w-8 text-muted-foreground hover:text-primary"
                                                    onClick={() => handleEdit(item)}
                                                >
                                                    <Edit className="h-4 w-4" />
                                                </Button>
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    className="h-8 w-8 text-muted-foreground hover:text-primary"
                                                    onClick={() => handleAdjustStock(item)}
                                                    title="Ajustar stock"
                                                >
                                                    <Package className="h-4 w-4" />
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

            {/* Edit Product Modal */}
            <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
                <DialogContent className="sm:max-w-[500px]">
                    <DialogHeader>
                        <DialogTitle>Editar Producto</DialogTitle>
                        <DialogDescription>
                            Modifica la información del producto
                        </DialogDescription>
                    </DialogHeader>

                    <div className="space-y-4 py-4">
                        <div className="space-y-2">
                            <Label htmlFor="name">Nombre *</Label>
                            <Input
                                id="name"
                                value={editForm.name}
                                onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="description">Descripción</Label>
                            <Textarea
                                id="description"
                                value={editForm.description}
                                onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                                rows={3}
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="unit_price">Precio Unitario *</Label>
                                <Input
                                    id="unit_price"
                                    type="number"
                                    step="0.01"
                                    value={editForm.unit_price}
                                    onChange={(e) => setEditForm({ ...editForm, unit_price: e.target.value })}
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="minimum_stock">Stock Mínimo *</Label>
                                <Input
                                    id="minimum_stock"
                                    type="number"
                                    value={editForm.minimum_stock}
                                    onChange={(e) => setEditForm({ ...editForm, minimum_stock: e.target.value })}
                                />
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="category">Categoría</Label>
                                <Input
                                    id="category"
                                    value={editForm.category}
                                    onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="type">Tipo</Label>
                                <Input
                                    id="type"
                                    value={editForm.type}
                                    onChange={(e) => setEditForm({ ...editForm, type: e.target.value })}
                                    placeholder="medicamento, insumo, equipo"
                                />
                            </div>
                        </div>
                    </div>

                    <DialogFooter>
                        <Button
                            variant="outline"
                            onClick={() => setShowEditModal(false)}
                            disabled={saving}
                        >
                            Cancelar
                        </Button>
                        <Button onClick={handleSaveEdit} disabled={saving}>
                            {saving ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Guardando...
                                </>
                            ) : (
                                'Guardar Cambios'
                            )}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Stock Adjustment Modal */}
            <Dialog open={showStockModal} onOpenChange={setShowStockModal}>
                <DialogContent className="sm:max-w-[400px]">
                    <DialogHeader>
                        <DialogTitle>Ajustar Stock</DialogTitle>
                        <DialogDescription>
                            Modifica la cantidad en inventario de "{stockProduct?.name}"
                        </DialogDescription>
                    </DialogHeader>

                    <div className="space-y-4 py-4">
                        <div className="space-y-2">
                            <Label htmlFor="current_stock">Stock Actual</Label>
                            <div className="flex items-center gap-4">
                                <div className="flex-1 text-2xl font-bold text-muted-foreground">
                                    {stockProduct?.current_stock}
                                </div>
                                <div className="text-muted-foreground">→</div>
                                <Input
                                    id="new_stock"
                                    type="number"
                                    min="0"
                                    value={stockAdjustment}
                                    onChange={(e) => setStockAdjustment(e.target.value)}
                                    className="flex-1 text-2xl font-bold text-center"
                                    autoFocus
                                />
                            </div>
                        </div>

                        <div className="bg-muted/30 p-3 rounded-lg">
                            <div className="text-sm text-muted-foreground">Stock mínimo</div>
                            <div className="font-medium">{stockProduct?.minimum_stock} unidades</div>
                        </div>
                    </div>

                    <DialogFooter>
                        <Button
                            variant="outline"
                            onClick={() => setShowStockModal(false)}
                            disabled={adjusting}
                        >
                            Cancelar
                        </Button>
                        <Button onClick={handleSaveStock} disabled={adjusting}>
                            {adjusting ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Ajustando...
                                </>
                            ) : (
                                'Actualizar Stock'
                            )}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </PageTransition>
    );
}
