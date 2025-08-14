import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Upload, Play, ArrowRight } from "lucide-react";

export default function HomePage() {
  return (
    <section className="mx-auto max-w-4xl px-4 py-20 text-center">
      <h1 className="text-4xl font-bold">
        Learn from ready-made courses or build your own AI-powered lessons
      </h1>
      <div className="mt-8 flex justify-center gap-4">
        <Link href="/courses">
          <Button>Browse Courses</Button>
        </Link>
        <Link href="/create">
          <Button variant="outline">Design Your Own</Button>
        </Link>
      </div>
      <div className="mt-16 grid gap-6 md:grid-cols-3">
        <Card className="flex flex-col items-center p-6">
          <Upload className="h-12 w-12 text-brand" />
          <h3 className="mt-4 font-semibold">Upload</h3>
          <p className="mt-2 text-sm text-gray-600">Add your slides and audio.</p>
        </Card>
        <Card className="flex flex-col items-center p-6">
          <Play className="h-12 w-12 text-brand" />
          <h3 className="mt-4 font-semibold">Generate</h3>
          <p className="mt-2 text-sm text-gray-600">
            Our AI creates a talking avatar.
          </p>
        </Card>
        <Card className="flex flex-col items-center p-6">
          <ArrowRight className="h-12 w-12 text-brand" />
          <h3 className="mt-4 font-semibold">Share</h3>
          <p className="mt-2 text-sm text-gray-600">Deliver engaging courses.</p>
        </Card>
      </div>
    </section>
  );
}
