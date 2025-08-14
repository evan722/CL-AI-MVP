"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CourseCard } from "@/components/course-card";
import { EmptyState } from "@/components/empty-state";
import { Button } from "@/components/ui/button";

interface LibraryCourse {
  id: string;
  title: string;
  description: string;
  level: string;
  duration: string;
  thumbnail?: string;
}

export default function LibraryPage() {
  const [courses, setCourses] = useState<LibraryCourse[] | null>(null);

  useEffect(() => {
    fetch("/api/library")
      .then((res) => res.json())
      .then((data) => setCourses(data))
      .catch(() => setCourses([]));
  }, []);

  if (courses === null) {
    return <div className="p-10">Loading...</div>;
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <h1 className="mb-6 text-3xl font-bold">My Library</h1>
      {courses.length ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {courses.map((course) => (
            <CourseCard key={course.id} {...course} />
          ))}
        </div>
      ) : (
        <EmptyState
          title="No courses yet"
          description="Create your first course to see it here."
          action={
            <Link href="/create">
              <Button>Create a course</Button>
            </Link>
          }
        />
      )}
    </div>
  );
}
