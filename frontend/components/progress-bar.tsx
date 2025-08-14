interface ProgressBarProps {
  value: number; // 0-100
}

export function ProgressBar({ value }: ProgressBarProps) {
  return (
    <div className="w-full rounded-full bg-gray-200">
      <div
        className="h-2 rounded-full bg-brand"
        style={{ width: `${value}%` }}
      />
    </div>
  );
}
