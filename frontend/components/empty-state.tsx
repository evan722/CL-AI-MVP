import { ReactNode } from "react";

interface EmptyStateProps {
  title: string;
  description: string;
  action?: ReactNode;
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <p className="text-xl font-semibold">{title}</p>
      <p className="mt-2 max-w-md text-gray-600">{description}</p>
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}
