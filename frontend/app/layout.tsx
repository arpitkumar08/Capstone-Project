import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "ProcureIQ · GeM Compliance", description: "AI-assisted bid compliance review workspace" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
