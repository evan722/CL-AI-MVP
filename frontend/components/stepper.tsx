interface StepperProps {
  steps: { title: string; description?: string }[];
  current: number;
}

export function Stepper({ steps, current }: StepperProps) {
  return (
    <ol className="flex flex-col gap-4 md:flex-row">
      {steps.map((s, i) => (
        <li key={s.title} className="flex items-center gap-2">
          <span
            className={`flex h-8 w-8 items-center justify-center rounded-full border-2 ${
              i <= current ? "border-brand bg-brand text-white" : "border-gray-300"
            }`}
          >
            {i + 1}
          </span>
          <div>
            <p className="font-medium">{s.title}</p>
            {s.description && (
              <p className="text-sm text-gray-500">{s.description}</p>
            )}
          </div>
        </li>
      ))}
    </ol>
  );
}
