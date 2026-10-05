"use client";

import { ChangeEvent, FormEvent, useState } from "react";

type Candidate = {
  nome?: string;
  email?: string;
  skills?: string[];
  anos_experiencia_total?: number;
};

type ScoreResponse = {
  score_final: number;
  score_heuristico: number;
  score_llm: number;
  justificativa: string;
  modelo: string;
  candidato: Candidate;
  aviso: string;
};

async function readPdf(file: File): Promise<string> {
  const pdfjs = await import("pdfjs-dist");
  pdfjs.GlobalWorkerOptions.workerSrc = new URL(
    "pdfjs-dist/build/pdf.worker.min.mjs",
    import.meta.url,
  ).toString();

  const pdf = await pdfjs.getDocument({
    data: new Uint8Array(await file.arrayBuffer()),
  }).promise;
  const pages: string[] = [];

  for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber += 1) {
    const page = await pdf.getPage(pageNumber);
    const content = await page.getTextContent();
    pages.push(
      content.items
        .map((item) => ("str" in item ? item.str : ""))
        .filter(Boolean)
        .join(" "),
    );
  }

  const text = pages.join("\n").trim();
  if (!text) {
    throw new Error(
      "Não foi possível extrair texto deste PDF. Se for um documento digitalizado, cole uma versão em texto.",
    );
  }
  return text;
}

function ScoreMetric({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold tabular-nums text-slate-800">
        {value}
        <span className="ml-1 text-sm font-normal text-slate-400">/100</span>
      </p>
    </div>
  );
}

export default function Home() {
  const [vagaTitulo, setVagaTitulo] = useState("AI Engineer Pleno");
  const [vagaDescricao, setVagaDescricao] = useState("");
  const [vagaSkills, setVagaSkills] = useState(
    "Python, FastAPI, Docker, LLM, PostgreSQL",
  );
  const [cvTexto, setCvTexto] = useState("");
  const [arquivoNome, setArquivoNome] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isReadingFile, setIsReadingFile] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ScoreResponse | null>(null);
  const [decisionMessage, setDecisionMessage] = useState<string | null>(null);

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    event.currentTarget.value = "";
    setError(null);
    setIsReadingFile(true);
    setArquivoNome(file.name);
    setCvTexto("");

    try {
      const extension = file.name.split(".").pop()?.toLowerCase();
      if (extension !== "pdf" && extension !== "txt") {
        throw new Error("Formato não suportado. Selecione um arquivo .txt ou .pdf.");
      }

      const text = extension === "pdf" ? await readPdf(file) : await file.text();
      if (!text.trim()) {
        throw new Error("O arquivo não contém texto para analisar.");
      }
      setCvTexto(text);
    } catch (caughtError) {
      setArquivoNome("");
      setError(
        caughtError instanceof Error
          ? `${file.name}: ${caughtError.message}`
          : `Não foi possível ler ${file.name}.`,
      );
    } finally {
      setIsReadingFile(false);
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setDecisionMessage(null);
    setResult(null);

    if (!cvTexto.trim()) {
      setError("Informe o texto do currículo ou carregue um arquivo.");
      return;
    }

    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
    if (!apiBaseUrl) {
      setError(
        "A URL da API não está configurada. Defina NEXT_PUBLIC_API_BASE_URL no ambiente de build.",
      );
      return;
    }

    const payload = {
      cv_texto: cvTexto,
      vaga: {
        titulo: vagaTitulo,
        descricao: vagaDescricao,
        skills_obrigatorias: vagaSkills
          .split(",")
          .map((skill) => skill.trim())
          .filter(Boolean),
      },
    };

    setIsLoading(true);
    try {
      const response = await fetch(`${apiBaseUrl.replace(/\/+$/, "")}/score`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(
            "O endpoint de pontuação não foi encontrado. Verifique a URL configurada para a API.",
          );
        }
        if (response.status >= 500) {
          throw new Error(
            "A API não conseguiu concluir a análise. Tente novamente mais tarde.",
          );
        }
        throw new Error(
          "Os dados enviados não foram aceitos pela API. Confira os campos e tente novamente.",
        );
      }

      const data = (await response.json()) as ScoreResponse;
      setResult(data);
      // TODO: Persistir a análise e sua versão no Supabase/Postgres, com controles LGPD.
    } catch (caughtError) {
      setError(
        caughtError instanceof TypeError
          ? "Não foi possível conectar à API. Verifique se ela está disponível e se o domínio do frontend está permitido no CORS."
          : caughtError instanceof Error
          ? caughtError.message
          : "Não foi possível conectar à API. Verifique a configuração e tente novamente.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleDecision = (decision: "Concordo" | "Discordo") => {
    // TODO: Persistir a decisão humana e vinculá-la à análise para auditoria.
    setDecisionMessage(
      `Sua opção "${decision}" foi selecionada. O registro persistente estará disponível em uma próxima etapa.`,
    );
  };

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 text-slate-800 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-8 flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-6">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.16em] text-blue-700">
              TalentoBR
            </p>
            <h1 className="mt-1 text-2xl font-semibold tracking-tight text-slate-900 sm:text-3xl">
              Análise de aderência profissional
            </h1>
            <p className="mt-2 max-w-2xl text-sm text-slate-500">
              Uma visão estruturada para apoiar a avaliação de currículos.
            </p>
          </div>
          <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-2 text-sm text-slate-600 shadow-sm">
            <span
              aria-hidden="true"
              className="h-2 w-2 rounded-full bg-blue-500"
            />
            Revisão humana
          </div>
        </header>

        <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,0.9fr)]">
          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7">
            <div className="mb-6">
              <p className="text-sm font-semibold text-blue-700">01 / ENTRADA</p>
              <h2 className="mt-1 text-xl font-semibold text-slate-900">
                Dados da triagem
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                Informe os requisitos da vaga e o conteúdo do currículo.
              </p>
            </div>

            <form className="space-y-5" onSubmit={handleSubmit}>
              <div>
                <label
                  className="mb-1.5 block text-sm font-medium text-slate-700"
                  htmlFor="vaga-titulo"
                >
                  Título da vaga
                </label>
                <input
                  className="w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                  id="vaga-titulo"
                  onChange={(event) => setVagaTitulo(event.target.value)}
                  required
                  value={vagaTitulo}
                />
              </div>

              <div>
                <label
                  className="mb-1.5 block text-sm font-medium text-slate-700"
                  htmlFor="vaga-skills"
                >
                  Competências obrigatórias
                </label>
                <input
                  className="w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                  id="vaga-skills"
                  onChange={(event) => setVagaSkills(event.target.value)}
                  placeholder="Ex.: Python, React, AWS"
                  value={vagaSkills}
                />
                <p className="mt-1.5 text-xs text-slate-500">
                  Separe cada competência por vírgula.
                </p>
              </div>

              <div>
                <label
                  className="mb-1.5 block text-sm font-medium text-slate-700"
                  htmlFor="vaga-descricao"
                >
                  Descrição da vaga{" "}
                  <span className="font-normal text-slate-400">(opcional)</span>
                </label>
                <textarea
                  className="min-h-24 w-full resize-y rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                  id="vaga-descricao"
                  onChange={(event) => setVagaDescricao(event.target.value)}
                  placeholder="Responsabilidades, contexto da equipe e outros requisitos..."
                  value={vagaDescricao}
                />
              </div>

              <div>
                <div className="mb-1.5 flex flex-wrap items-center justify-between gap-2">
                  <label
                    className="text-sm font-medium text-slate-700"
                    htmlFor="cv-texto"
                  >
                    Currículo
                  </label>
                  <label
                    className={`relative inline-flex items-center gap-2 rounded-lg border border-blue-200 bg-white px-3.5 py-2 text-sm font-semibold text-blue-800 shadow-sm transition hover:border-blue-300 hover:bg-blue-50 focus-within:ring-2 focus-within:ring-blue-500 focus-within:ring-offset-2 ${
                      isReadingFile || isLoading
                        ? "cursor-wait opacity-60"
                        : "cursor-pointer"
                    }`}
                  >
                    <svg
                      aria-hidden="true"
                      className="h-4 w-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        d="M12 16V4m0 0L7 9m5-5 5 5M5 14v4a2 2 0 002 2h10a2 2 0 002-2v-4"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="1.7"
                      />
                    </svg>
                    {arquivoNome ? "Trocar currículo" : "Carregar currículo"}
                    <input
                      accept=".txt,.pdf,text/plain,application/pdf"
                      aria-label="Selecionar arquivo de currículo"
                      className="absolute inset-0 h-full w-full cursor-pointer opacity-0 disabled:cursor-wait"
                      disabled={isReadingFile || isLoading}
                      onChange={handleFileChange}
                      type="file"
                    />
                  </label>
                </div>
                {isReadingFile && (
                  <div
                    aria-live="polite"
                    className="mb-3 flex items-center gap-2 rounded-lg border border-blue-200 bg-blue-50 px-3.5 py-3 text-sm text-blue-900"
                    role="status"
                  >
                    <svg
                      aria-hidden="true"
                      className="h-4 w-4 animate-spin text-blue-700"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-90"
                        d="M4 12a8 8 0 018-8"
                        stroke="currentColor"
                        strokeLinecap="round"
                        strokeWidth="4"
                      />
                    </svg>
                    <span>
                      {arquivoNome
                        ? `Lendo ${arquivoNome} e extraindo o texto...`
                        : "Carregando e extraindo texto do currículo..."}
                    </span>
                  </div>
                )}
                {!isReadingFile && arquivoNome && cvTexto.trim() && (
                  <div
                    aria-live="polite"
                    className="mb-3 flex items-start gap-3 rounded-lg border border-blue-200 bg-blue-50 px-3.5 py-3 text-sm text-blue-950 shadow-sm"
                    role="status"
                  >
                    <svg
                      aria-hidden="true"
                      className="mt-0.5 h-5 w-5 shrink-0 text-blue-700"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        d="m5 12 4 4L19 6"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                      />
                    </svg>
                    <div className="min-w-0">
                      <p className="font-semibold">Currículo carregado com sucesso</p>
                      <p className="mt-0.5 break-all text-blue-800">
                        {arquivoNome} · {cvTexto.length.toLocaleString("pt-BR")} caracteres extraídos
                      </p>
                    </div>
                  </div>
                )}
                {!isReadingFile && !arquivoNome && cvTexto.trim() && (
                  <div
                    aria-live="polite"
                    className="mb-3 flex items-start gap-3 rounded-lg border border-slate-200 bg-slate-50 px-3.5 py-3 text-sm text-slate-700"
                    role="status"
                  >
                    <svg
                      aria-hidden="true"
                      className="mt-0.5 h-5 w-5 shrink-0 text-slate-500"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="1.5"
                      />
                    </svg>
                    <div>
                      <p className="font-semibold">Texto do currículo inserido</p>
                      <p className="mt-0.5 text-slate-600">
                        {cvTexto.length.toLocaleString("pt-BR")} caracteres · inserido manualmente
                      </p>
                    </div>
                  </div>
                )}
                {!isReadingFile && !arquivoNome && !cvTexto.trim() && (
                  <div
                    aria-live="polite"
                    className="mb-3 flex items-start gap-3 rounded-lg border border-slate-200 bg-slate-50 px-3.5 py-3 text-sm text-slate-600"
                    role="status"
                  >
                    <svg
                      aria-hidden="true"
                      className="mt-0.5 h-5 w-5 shrink-0 text-slate-400"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="1.5"
                      />
                    </svg>
                    <div>
                      <p className="font-semibold text-slate-700">Nenhum currículo carregado</p>
                      <p className="mt-0.5">
                        Selecione um arquivo .txt ou .pdf, ou cole o texto abaixo.
                      </p>
                    </div>
                  </div>
                )}
                <textarea
                  className="min-h-48 w-full resize-y rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm leading-6 text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                  id="cv-texto"
                  onChange={(event) => {
                    setCvTexto(event.target.value);
                    setArquivoNome("");
                  }}
                  placeholder="Cole aqui o texto do currículo ou carregue um arquivo."
                  required
                  value={cvTexto}
                />
                <p className="mt-1.5 text-xs text-slate-500">
                  PDFs digitalizados sem camada de texto não podem ser extraídos.
                </p>
              </div>

              {error && (
                <div
                  aria-live="assertive"
                  className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900"
                  role="alert"
                >
                  {error}
                </div>
              )}

              <button
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-700 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:bg-blue-400"
                disabled={isLoading || isReadingFile}
                type="submit"
              >
                {isLoading && (
                  <svg
                    aria-hidden="true"
                    className="h-4 w-4 animate-spin"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-90"
                      d="M4 12a8 8 0 018-8"
                      stroke="currentColor"
                      strokeLinecap="round"
                      strokeWidth="4"
                    />
                  </svg>
                )}
                {isLoading ? "Analisando currículo..." : "Gerar análise"}
              </button>
            </form>
          </section>

          <section
            aria-labelledby="resultado-titulo"
            aria-live="polite"
            className="rounded-2xl border border-slate-200 bg-slate-100/80 p-5 sm:p-7"
          >
            <div className="mb-6">
              <p className="text-sm font-semibold text-blue-700">02 / RESULTADO</p>
              <h2
                className="mt-1 text-xl font-semibold text-slate-900"
                id="resultado-titulo"
              >
                Painel de análise
              </h2>
            </div>

            {isLoading ? (
              <div className="flex min-h-80 flex-col items-center justify-center rounded-xl border border-slate-200 bg-white px-6 text-center">
                <span className="relative flex h-12 w-12 items-center justify-center">
                  <span className="absolute h-12 w-12 animate-ping rounded-full bg-blue-200 opacity-60" />
                  <svg
                    aria-hidden="true"
                    className="relative h-7 w-7 animate-spin text-blue-700"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-90"
                      d="M4 12a8 8 0 018-8"
                      stroke="currentColor"
                      strokeLinecap="round"
                      strokeWidth="4"
                    />
                  </svg>
                </span>
                <p className="mt-5 font-medium text-slate-800">
                  Analisando aderência
                </p>
                <p className="mt-1 text-sm text-slate-500">
                  A análise pode levar alguns instantes.
                </p>
              </div>
            ) : result ? (
              <div className="space-y-4">
                <div className="rounded-xl border border-blue-100 bg-white p-5 shadow-sm">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">
                        Score híbrido final
                      </p>
                      <p className="mt-1 text-sm text-slate-500">
                        Síntese da análise heurística e semântica
                      </p>
                    </div>
                    <p className="shrink-0 text-4xl font-bold tabular-nums tracking-tight text-blue-700">
                      {result.score_final}
                      <span className="text-lg font-medium text-blue-300">
                        /100
                      </span>
                    </p>
                  </div>
                  <div
                    aria-label={`Score final ${result.score_final} de 100`}
                    className="mt-5 h-2 overflow-hidden rounded-full bg-slate-100"
                    role="img"
                  >
                    <div
                      className="h-full rounded-full bg-blue-600 transition-all"
                      style={{
                        width: `${Math.max(0, Math.min(100, result.score_final))}%`,
                      }}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <ScoreMetric
                    label="Correspondência de skills"
                    value={result.score_heuristico}
                  />
                  <ScoreMetric label="Avaliação LLM" value={result.score_llm} />
                </div>

                <div className="rounded-xl border border-slate-200 bg-white p-5">
                  <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">
                    Justificativa da análise
                  </p>
                  <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                    {result.justificativa}
                  </p>
                </div>

                <div className="rounded-xl border border-blue-200 bg-blue-50 p-4">
                  <p className="text-sm font-medium text-blue-950">
                    Revisão e decisão humana
                  </p>
                  <p className="mt-1 text-sm leading-5 text-blue-900">
                    {result.aviso} Modelo: {result.modelo}.
                  </p>
                  <div className="mt-4 flex flex-col gap-2 sm:flex-row">
                    <button
                      className="flex-1 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:border-blue-300 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                      onClick={() => handleDecision("Concordo")}
                      type="button"
                    >
                      Concordo com a análise
                    </button>
                    <button
                      className="flex-1 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:border-blue-300 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                      onClick={() => handleDecision("Discordo")}
                      type="button"
                    >
                      Discordo da análise
                    </button>
                  </div>
                  {decisionMessage && (
                    <p aria-live="polite" className="mt-3 text-xs text-blue-900">
                      {decisionMessage}
                    </p>
                  )}
                  {/* TODO: Registrar a decisão e o resultado com trilha de auditoria. */}
                </div>
              </div>
            ) : (
              <div className="flex min-h-80 flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 bg-white/70 px-6 text-center">
                <svg
                  aria-hidden="true"
                  className="h-10 w-10 text-slate-300"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="1.5"
                  />
                </svg>
                <p className="mt-4 font-medium text-slate-700">
                  Sua análise aparecerá aqui
                </p>
                <p className="mt-1 max-w-sm text-sm leading-5 text-slate-500">
                  Preencha os dados da vaga e do currículo para gerar uma
                  avaliação de apoio.
                </p>
              </div>
            )}
          </section>
        </div>

        <footer className="mx-auto mt-6 max-w-3xl text-center text-xs leading-5 text-slate-500">
          Esta ferramenta oferece apoio à triagem e não substitui a avaliação
          humana. Envie apenas dados autorizados para processamento.
        </footer>
      </div>
    </main>
  );
}
