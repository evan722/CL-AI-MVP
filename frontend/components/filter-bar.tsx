"use client";

interface FilterBarProps {
  onSearch: (term: string) => void;
  onLevel: (level: string) => void;
}

export function FilterBar({ onSearch, onLevel }: FilterBarProps) {
  return (
    <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      <input
        type="text"
        placeholder="Search courses"
        onChange={(e) => onSearch(e.target.value)}
        className="w-full rounded-md border px-3 py-2 md:w-1/3"
      />
      <div className="flex gap-4">
        <select
          onChange={(e) => onLevel(e.target.value)}
          className="rounded-md border px-3 py-2"
        >
          <option value="">All Levels</option>
          <option value="Beginner">Beginner</option>
          <option value="Intermediate">Intermediate</option>
          <option value="Advanced">Advanced</option>
        </select>
      </div>
    </div>
  );
}
