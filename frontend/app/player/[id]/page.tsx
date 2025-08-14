"use client";

import { useState } from "react";
import Link from "next/link";
import { LEGACY_PLAYER_PATH } from "@/lib/routes";

export default function PlayerPage({ params }: { params: { id: string } }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="flex h-full flex-col">
      <header className="flex items-center justify-between border-b p-4">
        <Link href="/courses" className="text-sm text-gray-500">
          ← Back
        </Link>
        <h1 className="font-semibold capitalize">{params.id.replace("-", " ")}</h1>
        <button
          className="text-sm text-brand"
          onClick={() => setOpen(!open)}
          aria-expanded={open}
        >
          Syllabus
        </button>
      </header>
      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1">
          <iframe
            src={`${LEGACY_PLAYER_PATH}/${params.id}`}
            className="h-full w-full border-0"
            title="Course Player"
          />
        </div>
        <aside
          className={`${
            open ? "block" : "hidden"
          } w-64 border-l bg-white p-4 md:block`}
        >
          <h2 className="mb-2 font-medium">Syllabus</h2>
          <p className="text-sm text-gray-600">Coming soon...</p>
        </aside>
      </div>
    </div>
  );
}
