"use client";

import * as React from "react";
import { Package, AlertTriangle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { auth } from "@/lib/auth";

interface LowStockProduct {
    product_id: number;
    sku: string;
    name: string;
    current_stock: number;
    minimum_stock: number;
    units_needed: number;
    category: string;
    type: string;
}

export function LowStockWidget() {
    const [products, setProducts] = React.useState<LowStockProduct[]>([]);
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
        const fetchLowStock = async () => {
            try {
                const response = await fetch('/api/notifications/low-stock', {
                    headers: {
                        'Authorization': `Bearer ${auth.getToken()}`
                    }
                });

                if (!response.ok) throw new Error('Failed to fetch low stock products');

                const result = await response.json();

                if (result.success) {
                    setProducts(result.data.products || []);
                }
            } catch (error) {
                console.error('Error fetching low stock products:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchLowStock();

        // Refresh every 10 minutes
        const interval = setInterval(fetchLowStock, 10 * 60 * 1000);

        return () => clearInterval(interval);
    }, []);

    const getSeverityColor = (current: number, minimum: number) => {
        if (current === 0) {
            return 'text-red-600';
        }
        const percentage = (current / minimum) * 100;
        if (percentage <= 50) {
            return 'text-orange-600';
        }
        return 'text-yellow-600';
    };

    if (loading) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Package className="h-5 w-5" />
                        Stock Bajo
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex items-center justify-center h-40 text-muted-foreground">
                        Cargando inventario...
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Package className="h-5 w-5" />
                        Stock Bajo
                    </div>
                    {products.length > 0 && (
                        <Badge variant="destructive" className="font-normal">
                            {products.length} {products.length === 1 ? 'producto' : 'productos'}
                        </Badge>
                    )}
                </CardTitle>
            </CardHeader>
            <CardContent>
                {products.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-40 text-center text-muted-foreground">
                        <Package className="h-12 w-12 mb-2 opacity-20" />
                        <p className="font-medium">Todo el inventario está bien</p>
                        <p className="text-sm">No hay productos con stock bajo</p>
                    </div>
                ) : (
                    <ScrollArea className="h-[400px] pr-4">
                        <div className="space-y-3">
                            {products.map((product) => (
                                <div
                                    key={product.product_id}
                                    className="flex items-start justify-between gap-4 rounded-lg border p-3 hover:bg-muted/30 transition-colors"
                                >
                                    <div className="flex-1 space-y-1">
                                        <div className="flex items-start gap-2">
                                            <AlertTriangle
                                                className={`h-4 w-4 mt-0.5 ${getSeverityColor(product.current_stock, product.minimum_stock)}`}
                                            />
                                            <div className="flex-1">
                                                <p className="font-medium leading-none mb-1">{product.name}</p>
                                                <p className="text-xs text-muted-foreground">SKU: {product.sku}</p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-4 pl-6 text-sm">
                                            <div>
                                                <span className="text-muted-foreground">Actual: </span>
                                                <span className={`font-semibold ${getSeverityColor(product.current_stock, product.minimum_stock)}`}>
                                                    {product.current_stock}
                                                </span>
                                            </div>
                                            <div>
                                                <span className="text-muted-foreground">Mínimo: </span>
                                                <span className="font-medium">{product.minimum_stock}</span>
                                            </div>
                                            <div>
                                                <span className="text-muted-foreground">Necesita: </span>
                                                <span className="font-semibold text-primary">+{product.units_needed}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </ScrollArea>
                )}

                {products.length > 0 && (
                    <div className="mt-4 pt-4 border-t">
                        <Button variant="outline" className="w-full" size="sm">
                            <Package className="h-4 w-4 mr-2" />
                            Ir a Inventario
                        </Button>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
