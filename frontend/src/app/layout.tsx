import type { Metadata } from "next";
import { Archivo } from "next/font/google";

import "./globals.css";

const archivo = Archivo({
  variable: "--font-archivo",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Clientes · Fletes y Mudanzas Express",
    template: "%s · Fletes y Mudanzas Express",
  },
  description: "Gestión de clientes, servicios y cobros de Fletes y Mudanzas Express.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="es-AR" className={`${archivo.variable} h-full`}>
      <body className="flex min-h-full flex-col">{children}</body>
    </html>
  );
}
