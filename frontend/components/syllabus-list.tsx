interface SyllabusSection {
  title: string;
  lessons: string[];
}

export function SyllabusList({ sections }: { sections: SyllabusSection[] }) {
  return (
    <div className="space-y-4">
      {sections.map((section) => (
        <details key={section.title} className="group rounded-lg border p-3">
          <summary className="cursor-pointer font-medium group-open:mb-2">
            {section.title}
          </summary>
          <ul className="ml-4 list-disc space-y-1">
            {section.lessons.map((lesson) => (
              <li key={lesson} className="text-sm text-gray-600">
                {lesson}
              </li>
            ))}
          </ul>
        </details>
      ))}
    </div>
  );
}
