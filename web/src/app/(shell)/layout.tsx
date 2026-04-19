import { AppShell } from "@/components/AppShell";
import { WattyProfileProvider } from "@/context/WattyProfileContext";

export default function ShellLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <WattyProfileProvider>
      <AppShell>{children}</AppShell>
    </WattyProfileProvider>
  );
}
