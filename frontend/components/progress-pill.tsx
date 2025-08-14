interface ProgressPillProps {
  value: number;
}

export function ProgressPill({ value }: ProgressPillProps) {
  return (
    <span className="inline-block rounded-full bg-brand/10 px-2 py-0.5 text-xs text-brand">
      {value}% complete
    </span>
  );
}
