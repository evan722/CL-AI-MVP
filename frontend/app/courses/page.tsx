"use client";

import { useState } from "react";
import { CourseCard } from "@/components/course-card";
import { FilterBar } from "@/components/filter-bar";
import { EmptyState } from "@/components/empty-state";

const COURSES = [
  {
    id: "python-basics",
    title: "Python Basics",
    description: "Learn the fundamentals of Python programming.",
    level: "Beginner",
    duration: "45 min",
    thumbnail: "https://placehold.co/600x400?text=Python",
  },
];

export default function CoursesPage() {
  const [search, setSearch] = useState("");
  const [level, setLevel] = useState("");

  const filtered = COURSES.filter(
    (c) =>
      c.title.toLowerCase().includes(search.toLowerCase()) &&
      (level ? c.level === level : true)
  );

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <h1 className="mb-6 text-3xl font-bold">Courses</h1>
      <FilterBar onSearch={setSearch} onLevel={setLevel} />
      {filtered.length ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((course) => (
            <CourseCard key={course.id} {...course} />
          ))}
        </div>
      ) : (
        <EmptyState
          title="No courses found"
          description="Try adjusting your search or filters."
        />
      )}
    </div>
  );
}
