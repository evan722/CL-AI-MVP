"use client";

import Link from "next/link";
import { useState } from "react";
import { Menu } from "lucide-react";
import { Button } from "./ui/button";

const navItems = [
  { href: "/courses", label: "Courses" },
  { href: "/create", label: "Design Your Own" },
  { href: "/library", label: "My Library" },
];

export function AppHeader() {
  const [open, setOpen] = useState(false);
  return (
    <header className="border-b bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between p-4">
        <Link href="/" className="text-xl font-semibold text-brand">
          CL-AI-MVP
        </Link>
        <nav className="hidden gap-6 md:flex">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="text-sm font-medium text-gray-700 hover:text-brand"
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <Button
          variant="ghost"
          className="md:hidden"
          onClick={() => setOpen(!open)}
          aria-label="Toggle Menu"
        >
          <Menu className="h-6 w-6" />
        </Button>
      </div>
      {open && (
        <div className="space-y-2 px-4 pb-4 md:hidden">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="block rounded-md p-2 text-sm font-medium hover:bg-brand/10"
            >
              {item.label}
            </Link>
          ))}
        </div>
      )}
    </header>
  );
}
