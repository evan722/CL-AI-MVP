import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Stepper } from "@/components/stepper";
import { LEGACY_UPLOAD_PATH } from "@/lib/routes";

const steps = [
  { title: "Prepare files", description: "Slides, audio, timestamps, avatar" },
  { title: "Upload", description: "Generate your lesson" },
];

export default function CreatePage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <h1 className="mb-6 text-3xl font-bold">Design Your Own</h1>
      <p className="mb-8 text-gray-700">
        Upload your slides, audio, and timestamps to generate your lesson.
      </p>
      <Stepper steps={steps} current={0} />
      <ul className="mt-6 list-disc space-y-2 pl-6 text-sm text-gray-700">
        <li>Slides PDF or Google Slides ID</li>
        <li>Audio narration</li>
        <li>Timestamps JSON</li>
        <li>Avatar image/video (optional)</li>
      </ul>
      <div className="mt-10 flex justify-end">
        <Link href={LEGACY_UPLOAD_PATH}>
          <Button>Go to Upload</Button>
        </Link>
      </div>
    </div>
  );
}
