import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
    return (
        <div className="flex flex-col gap-6 w-full max-w-7xl mx-auto p-6 animate-in fade-in duration-500">
            {/* Header Skeleton */}
            <div className="flex flex-col gap-2 mb-4">
                <Skeleton className="h-8 w-64" />
                <Skeleton className="h-4 w-96" />
            </div>

            {/* KPI Cards Skeleton */}
            <div className="grid gap-4 md:grid-cols-2 md:gap-8 lg:grid-cols-4">
                {[...Array(4)].map((_, i) => (
                    <div key={i} className="rounded-xl border border-muted p-6 shadow-sm">
                        <div className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <Skeleton className="h-4 w-24" />
                            <Skeleton className="h-4 w-4 rounded-full" />
                        </div>
                        <div className="mt-2">
                            <Skeleton className="h-8 w-32" />
                            <Skeleton className="h-3 w-20 mt-1" />
                        </div>
                    </div>
                ))}
            </div>

            {/* Main Content Skeleton */}
            <div className="mt-4 grid gap-4 md:gap-8 lg:grid-cols-2 xl:grid-cols-3">
                <div className="col-span-2 rounded-xl border border-muted p-6 shadow-sm h-[400px]">
                    <div className="flex flex-col gap-4 h-full">
                        <Skeleton className="h-6 w-48" />
                        <div className="flex-1 flex items-end gap-2">
                            {[...Array(6)].map((_, i) => (
                                <Skeleton key={i} className="w-full rounded-t-lg" style={{ height: `${Math.random() * 80 + 20}%` }} />
                            ))}
                        </div>
                    </div>
                </div>
                <div className="rounded-xl border border-muted p-6 shadow-sm h-[400px]">
                    <Skeleton className="h-6 w-48 mb-6" />
                    <div className="space-y-4">
                        {[...Array(5)].map((_, i) => (
                            <div key={i} className="flex items-center gap-4">
                                <Skeleton className="h-10 w-10 rounded-full" />
                                <div className="space-y-2 flex-1">
                                    <Skeleton className="h-4 w-full" />
                                    <Skeleton className="h-3 w-1/2" />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
