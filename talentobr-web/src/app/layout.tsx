import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TalentoBR | Análise de currículos",
  description:
    "Ferramenta de apoio à análise de aderência entre currículos e vagas, com revisão humana.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="pt-BR" className="h-full antialiased">
      <body className="min-h-full">{children}</body>
    </html>
  );
}
