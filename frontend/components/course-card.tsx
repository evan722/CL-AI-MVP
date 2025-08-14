import Link from "next/link";
import { Card } from "./ui/card";
import { Button } from "./ui/button";

interface CourseCardProps {
  id: string;
  title: string;
  description: string;
  level: string;
  duration: string;
  thumbnail?: string;
}

export function CourseCard({
  id,
  title,
  description,
  level,
  duration,
  thumbnail,
}: CourseCardProps) {
  return (
    <Card className="flex flex-col overflow-hidden">
      {thumbnail && (
        <img
          src={thumbnail}
          alt=""
          className="h-40 w-full object-cover"
        />
      )}
      <div className="flex flex-1 flex-col p-4">
        <div className="mb-2 flex items-center justify-between">
          <h3 className="text-lg font-semibold">{title}</h3>
          <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs text-emerald-700">
            {level}
          </span>
        </div>
        <p className="flex-1 text-sm text-gray-600">{description}</p>
        <div className="mt-4 flex items-center justify-between">
          <span className="text-xs text-gray-500">{duration}</span>
          <Link href={`/courses/${id}`}>
            <Button>View</Button>
          </Link>
        </div>
      </div>
    </Card>
  );
}
