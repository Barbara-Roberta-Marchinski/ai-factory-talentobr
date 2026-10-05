# TalentoBR Web

Frontend estático em Next.js para a API FastAPI do TalentoBR.

## Desenvolvimento local

Requer Node.js 20 ou superior.

1. Instale as dependências:

   ```powershell
   npm ci
   ```

2. Crie `talentobr-web/.env.local` com a URL da API:

   ```env
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```

3. Inicie o frontend:

   ```powershell
   npm run dev
   ```

Abra `http://localhost:3000`. O backend local deve permitir essa origem pela
variável `FRONTEND_ORIGINS` (o padrão é `http://localhost:3000`).

## Build estático para Render

O `next.config.ts` usa `output: "export"`; o build gera os arquivos estáticos
em `out/`.

- **Root Directory:** `talentobr-web`
- **Build Command:** `npm ci && npm run build`
- **Publish Directory:** `out`
- **Environment Variable:** `NEXT_PUBLIC_API_BASE_URL=https://<sua-api>.onrender.com`

`NEXT_PUBLIC_API_BASE_URL` é incorporada ao bundle durante o build. Configure-a
no serviço Static Site antes de publicar. No serviço da API, configure
`FRONTEND_ORIGINS` com a origem completa do site (por exemplo,
`https://talentobr-web.onrender.com`), sem barra final. Várias origens podem
ser informadas separadas por vírgulas.

Currículos em PDF são extraídos no navegador antes do envio. PDFs digitalizados
sem camada de texto precisam de OCR, que ainda não está implementado.

## Scripts

```powershell
npm run lint
npm run build
```
