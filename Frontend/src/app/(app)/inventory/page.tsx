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
    PlusCircle
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { PageTransition } from "@/components/page-transition";

// Mock Data
const inventoryItems = [
    { id: 1, name: "Guantes de Nitrilo (Caja x100)", code: "MED-001", category: "Medicamentos", quantity: 150, status: "En Stock" },
    { id: 2, name: "Jeringas 5ml (Caja x50)", code: "MED-002", category: "Medicamentos", quantity: 25, status: "Stock Bajo" },
    { id: 3, name: "Resmas de Papel A4", code: "OFI-001", category: "Suministros de Oficina", quantity: 45, status: "En Stock" },
    { id: 4, name: "Paracetamol 500mg", code: "MED-003", category: "Medicamentos", quantity: 0, status: "Agotado" },
    { id: 5, name: "Termómetro Digital", code: "EQU-001", category: "Equipos", quantity: 8, status: "Stock Bajo" },
];

export default function InventoryPage() {
    return (
        <PageTransition className="flex flex-col gap-6 w-full max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex flex-wrap justify-between items-center gap-4">
                <h1 className="text-2xl font-bold tracking-tight text-foreground">Gestión de Inventario</h1>
                <Button variant="outline" size="icon" className="md:hidden">
                    <Search className="h-4 w-4" />
                </Button>
            </div>

            {/* Search and Actions */}
            <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
                <div className="w-full sm:max-w-md relative">
                    <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input placeholder="Buscar por nombre o código..." className="pl-9" />
                </div>
                <div className="flex w-full sm:w-auto gap-3">
                    <Button variant="outline" className="flex-1 sm:flex-none gap-2">
                        <Download className="h-4 w-4" /> Exportar CSV
                    </Button>
                    <Button className="flex-1 sm:flex-none gap-2">
                        <PlusCircle className="h-4 w-4" /> Añadir Producto
                    </Button>
                </div>
            </div>

            {/* Categories / Filters */}
            <div className="flex gap-2 overflow-x-auto pb-2">
                {['Todo', 'Medicamentos', 'Suministros de Oficina', 'Equipos'].map((cat, i) => (
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
                            <TableHead>Código</TableHead>
                            <TableHead>Categoría</TableHead>
                            <TableHead className="text-center">Cantidad</TableHead>
                            <TableHead>Estado</TableHead>
                            <TableHead className="text-right">Acciones</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {inventoryItems.map((item) => (
                            <TableRow key={item.id} className="hover:bg-muted/30 transition-colors">
                                <TableCell className="font-medium">{item.name}</TableCell>
                                <TableCell className="text-muted-foreground">{item.code}</TableCell>
                                <TableCell className="text-muted-foreground">{item.category}</TableCell>
                                <TableCell className="text-center font-medium">{item.quantity}</TableCell>
                                <TableCell>
                                    <Badge variant="outline" className={`
                                border-0 px-2 py-0.5 rounded-full text-xs font-medium
                                ${item.status === 'En Stock' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : ''}
                                ${item.status === 'Stock Bajo' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300' : ''}
                                ${item.status === 'Agotado' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300' : ''}
                            `}>
                                        {item.status}
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
                        ))}
                    </TableBody>
                </Table>
            </div>
        </PageTransition>
    );
}
