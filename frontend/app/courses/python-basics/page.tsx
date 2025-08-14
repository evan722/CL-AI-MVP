import Link from "next/link";
import { Button } from "@/components/ui/button";
import { SyllabusList } from "@/components/syllabus-list";
import { ProgressPill } from "@/components/progress-pill";

const syllabus = [
  { title: "Introduction", lessons: ["What is Python?", "Installing Python"] },
  { title: "Basics", lessons: ["Variables", "Control Flow"] },
];

export default function PythonBasicsPage() {
  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <div className="mb-8 rounded-xl bg-indigo-100 p-6">
        <h1 className="text-3xl font-bold">Python Basics</h1>
        <p className="mt-2 text-gray-700">
          Learn the fundamentals of Python programming in this beginner-friendly course.
        </p>
        <div className="mt-4 flex items-center gap-4">
          <Link href="/player/python-basics">
            <Button>Start Course</Button>
          </Link>
          <ProgressPill value={0} />
        </div>
      </div>
      <div className="grid gap-8 md:grid-cols-3">
        <div className="md:col-span-2">
          <h2 className="mb-4 text-xl font-semibold">Syllabus</h2>
          <SyllabusList sections={syllabus} />
        </div>
        <div>
          <h2 className="mb-4 text-xl font-semibold">About this course</h2>
          <p className="text-sm text-gray-600">
            A quick introduction to Python covering the basics of syntax,
            variables, and control flow.
          </p>
        </div>
      </div>
    </div>
  );
}
