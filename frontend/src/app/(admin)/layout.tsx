import { exigirRol } from "@/lib/auth/guards";

import { AdminShell } from "./admin-shell";

export const instant = false;

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const usuario = await exigirRol("ADMIN");

  return <AdminShell usuario={usuario}>{children}</AdminShell>;
}
