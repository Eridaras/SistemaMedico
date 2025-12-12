import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { invoices, patients } from '@/lib/data';
import { PlusCircle } from 'lucide-react';
import type { VariantProps } from "class-variance-authority";
import { badgeVariants } from "@/components/ui/badge";

const getPatientName = (id: string) => patients.find(p => p.id === id)?.name || 'Unknown';

const statusBadgeVariant: Record<string, VariantProps<typeof badgeVariants>["variant"]> = {
    'Paid': 'default',
    'Pending': 'secondary',
    'Overdue': 'destructive'
}

export default function BillingPage() {
  return (
    <>
       <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold md:text-2xl">Billing</h1>
        <Button>
            <PlusCircle className="mr-2 h-4 w-4" /> Create Invoice
        </Button>
      </div>
      <Card className="mt-4">
        <CardHeader>
          <CardTitle>Invoices</CardTitle>
          <CardDescription>
            Manage and track all patient invoices.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Invoice ID</TableHead>
                <TableHead>Patient</TableHead>
                <TableHead>Date</TableHead>
                <TableHead className="text-right">Amount</TableHead>
                <TableHead className="text-center">Status</TableHead>
                <TableHead>
                  <span className="sr-only">Actions</span>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {invoices.map((invoice) => (
                <TableRow key={invoice.id}>
                  <TableCell className="font-medium">{invoice.id.toUpperCase()}</TableCell>
                  <TableCell>{getPatientName(invoice.patientId)}</TableCell>
                  <TableCell>{invoice.date}</TableCell>
                  <TableCell className="text-right">${invoice.amount.toFixed(2)}</TableCell>
                  <TableCell className="text-center">
                    <Badge variant={statusBadgeVariant[invoice.status]}>
                      {invoice.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                     <Button variant="outline" size="sm">View</Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </>
  );
}
