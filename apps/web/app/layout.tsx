import type { Metadata } from "next";
import "./globals.css";
import Providers from "./providers";

export const metadata: Metadata = {
  title: "ZETA Platform",
  description: "Admin panel for ZETA Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-white text-[#202124] antialiased">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
