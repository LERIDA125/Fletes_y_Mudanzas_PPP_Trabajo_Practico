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
    default: "MoviFlow | Gestión de fletes y mudanzas",
    template: "%s · MoviFlow",
  },
  description:
    "Dashboard operativo para gestionar servicios, choferes, vehículos y cobranzas.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="es-AR" suppressHydrationWarning className={`${archivo.variable} h-full`}>
      <head>
        <meta name="color-scheme" content="light dark" />
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){
              try {
                var t = localStorage.getItem('theme');
                if (t === 'dark' || (!t && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
                  document.documentElement.classList.add('dark');
                  document.documentElement.setAttribute('data-theme', 'dark');
                } else {
                  document.documentElement.classList.remove('dark');
                  document.documentElement.setAttribute('data-theme', 'light');
                }
              } catch(e){}
            })()`,
          }}
        />
      </head>
      <body className="flex min-h-full flex-col bg-[var(--papel)] text-[var(--tinta)] transition-colors duration-150">
        {children}
      </body>
    </html>
  );
}
