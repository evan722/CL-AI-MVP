import "./globals.css";
import { AppHeader } from "@/components/app-header";
import { Footer } from "@/components/footer";

export const metadata = {
  title: "CL-AI-MVP",
  description:
    "Learn from ready-made courses or build your own AI-powered lessons",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="flex min-h-screen flex-col bg-neutral-50 font-sans">
        <AppHeader />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
