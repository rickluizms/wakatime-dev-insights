# 📊 Dev Insights API - Guia de Integração

Documentação completa da API para integração com aplicações **Vite/React**.

## Índice

- [Visão Geral](#visão-geral)
- [Autenticação](#autenticação)
- [Configuração do Cliente HTTP](#configuração-do-cliente-http)
- [Modelos de Dados](#modelos-de-dados)
- [Endpoints](#endpoints)
- [Exemplos de Implementação React](#exemplos-de-implementação-react)
- [Tratamento de Erros](#tratamento-de-erros)

---

## Visão Geral

| Informação | Valor |
|------------|-------|
| **Base URL** | `http://localhost:8000` |
| **Formato** | JSON |
| **Autenticação** | API Key via Header |
| **Documentação Interativa** | `/docs` (Swagger UI) |
| **Documentação Alternativa** | `/redoc` (ReDoc) |

---

## Autenticação

A API utiliza autenticação via **API Key** enviada no header HTTP.

### Header de Autenticação

```
X-API-Key: sua-chave-aqui
```

### Chaves Disponíveis

| Chave | Permissão |
|-------|-----------|
| `dev-insights-key-2026` | Admin (leitura completa) |
| `readonly-key-2026` | Apenas leitura |

### Respostas de Erro de Autenticação

| Código | Descrição |
|--------|-----------|
| `401` | API Key não fornecida ou inválida |

**Exemplo de resposta de erro:**

```json
{
  "detail": "API Key não fornecida. Use o header X-API-Key."
}
```

---

## Configuração do Cliente HTTP

### Instalação de Dependências

```bash
npm install axios
# ou
npm install @tanstack/react-query axios
```

### Configuração do Axios (Recomendado)

Crie um arquivo `src/lib/api.ts`:

```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || 'dev-insights-key-2026';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
  },
});

// Interceptor para tratamento de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('Erro de autenticação: API Key inválida');
    }
    return Promise.reject(error);
  }
);
```

### Variáveis de Ambiente (.env)

```env
VITE_API_URL=http://localhost:8000
VITE_API_KEY=dev-insights-key-2026
```

---

## Modelos de Dados

### TypeScript Interfaces

Crie um arquivo `src/types/api.ts`:

```typescript
// =============================
// RESUMO DIÁRIO
// =============================
export interface DailySummary {
  id: number;
  date: string;                    // Formato: "YYYY-MM-DD"
  total_seconds: number;
  digital: string | null;          // Formato: "H:MM"
  hours: number | null;
  minutes: number | null;
  text: string | null;             // Ex: "5 hrs 30 mins"
  ai_additions: number | null;
  ai_deletions: number | null;
  human_additions: number | null;
  human_deletions: number | null;
  created_at: string | null;       // Timestamp ISO
}

// =============================
// LINGUAGENS
// =============================
export interface Language {
  id: number;
  summary_date: string;
  name: string;
  total_seconds: number;
  percent: number | null;
  digital: string | null;
  hours: number | null;
  minutes: number | null;
}

export interface LanguageStats {
  name: string;
  total_seconds: number;
  total_hours: number;
  percentage: number;
}

// =============================
// PROJETOS
// =============================
export interface Project {
  id: number;
  summary_date: string;
  name: string;
  total_seconds: number;
  percent: number | null;
  digital: string | null;
  hours: number | null;
  minutes: number | null;
  ai_additions: number | null;
  ai_deletions: number | null;
  human_additions: number | null;
  human_deletions: number | null;
}

export interface ProjectStats {
  name: string;
  total_seconds: number;
  total_hours: number;
  percentage: number;
  ai_additions: number;
  ai_deletions: number;
  human_additions: number;
  human_deletions: number;
}

// =============================
// EDITORES
// =============================
export interface Editor {
  id: number;
  summary_date: string;
  name: string;
  total_seconds: number;
  percent: number | null;
  digital: string | null;
  hours: number | null;
  minutes: number | null;
}

// =============================
// ESTATÍSTICAS GERAIS
// =============================
export interface OverallStats {
  total_days: number;
  total_seconds: number;
  total_hours: number;
  average_seconds_per_day: number;
  average_hours_per_day: number;
  top_language: string | null;
  top_project: string | null;
  top_editor: string | null;
}

// =============================
// HEALTH CHECK
// =============================
export interface HealthStatus {
  status: string;
  database: string;
  tables_count: number;
}

// =============================
// PARÂMETROS DE QUERY
// =============================
export interface DateRangeParams {
  start_date?: string;    // Formato: "YYYY-MM-DD"
  end_date?: string;      // Formato: "YYYY-MM-DD"
  limit?: number;         // Padrão: 30, Max: 365
}

// =============================
// RESPOSTA DE ERRO
// =============================
export interface ApiError {
  detail: string;
}
```

---

## Endpoints

### 🔓 Endpoints Públicos

#### `GET /health`

Verifica o status da API e do banco de dados.

**Autenticação:** Não requer

**Resposta:**

```json
{
  "status": "healthy",
  "database": "connected",
  "tables_count": 10
}
```

---

### 🔐 Endpoints Protegidos

> Todos os endpoints abaixo requerem o header `X-API-Key`

---

### Resumos Diários

#### `GET /summaries`

Retorna lista de resumos diários.

**Parâmetros de Query:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `start_date` | string | Não | Data inicial (YYYY-MM-DD) |
| `end_date` | string | Não | Data final (YYYY-MM-DD) |
| `limit` | integer | Não | Limite de resultados (1-365, padrão: 30) |

**Exemplo de requisição:**

```
GET /summaries?start_date=2026-01-01&end_date=2026-01-15&limit=15
```

**Resposta:**

```json
[
  {
    "id": 1,
    "date": "2026-01-16",
    "total_seconds": 18396.0,
    "digital": "5:06",
    "hours": 5,
    "minutes": 6,
    "text": "5 hrs 6 mins",
    "ai_additions": 150,
    "ai_deletions": 45,
    "human_additions": 320,
    "human_deletions": 89,
    "created_at": "2026-01-17T02:30:24"
  }
]
```

---

#### `GET /summaries/{target_date}`

Retorna o resumo de uma data específica.

**Parâmetros de Path:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `target_date` | string | Data no formato YYYY-MM-DD |

**Exemplo de requisição:**

```
GET /summaries/2026-01-16
```

**Resposta:** Objeto `DailySummary`

**Erros:**

| Código | Descrição |
|--------|-----------|
| `404` | Resumo não encontrado para a data |

---

### Linguagens

#### `GET /languages`

Retorna dados de linguagens por dia.

**Parâmetros de Query:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `start_date` | string | Não | Data inicial |
| `end_date` | string | Não | Data final |
| `limit` | integer | Não | Limite (1-1000, padrão: 100) |

**Resposta:**

```json
[
  {
    "id": 1,
    "summary_date": "2026-01-16",
    "name": "TypeScript",
    "total_seconds": 7200.0,
    "percent": 45.5,
    "digital": "2:00",
    "hours": 2,
    "minutes": 0
  }
]
```

---

#### `GET /languages/stats`

Retorna estatísticas agregadas de linguagens.

**Parâmetros de Query:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `start_date` | string | Não | Data inicial |
| `end_date` | string | Não | Data final |
| `limit` | integer | Não | Top N linguagens (1-50, padrão: 10) |

**Resposta:**

```json
[
  {
    "name": "TypeScript",
    "total_seconds": 36000.0,
    "total_hours": 10.0,
    "percentage": 45.5
  },
  {
    "name": "Python",
    "total_seconds": 28800.0,
    "total_hours": 8.0,
    "percentage": 36.36
  }
]
```

---

### Projetos

#### `GET /projects`

Retorna dados de projetos por dia.

**Parâmetros de Query:** Mesmos de `/languages`

**Resposta:**

```json
[
  {
    "id": 1,
    "summary_date": "2026-01-16",
    "name": "dev-insights",
    "total_seconds": 18000.0,
    "percent": 85.0,
    "digital": "5:00",
    "hours": 5,
    "minutes": 0,
    "ai_additions": 150,
    "ai_deletions": 45,
    "human_additions": 320,
    "human_deletions": 89
  }
]
```

---

#### `GET /projects/stats`

Retorna estatísticas agregadas de projetos com métricas de AI.

**Parâmetros de Query:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `start_date` | string | Não | Data inicial |
| `end_date` | string | Não | Data final |
| `limit` | integer | Não | Top N projetos (1-50, padrão: 10) |

**Resposta:**

```json
[
  {
    "name": "dev-insights",
    "total_seconds": 36000.0,
    "total_hours": 10.0,
    "percentage": 75.0,
    "ai_additions": 500,
    "ai_deletions": 120,
    "human_additions": 1200,
    "human_deletions": 300
  }
]
```

---

### Editores

#### `GET /editors`

Retorna dados de editores por dia.

**Parâmetros de Query:** Mesmos de `/languages`

**Resposta:**

```json
[
  {
    "id": 1,
    "summary_date": "2026-01-16",
    "name": "VS Code",
    "total_seconds": 18000.0,
    "percent": 95.0,
    "digital": "5:00",
    "hours": 5,
    "minutes": 0
  }
]
```

---

### Estatísticas Gerais

#### `GET /stats`

Retorna estatísticas gerais consolidadas.

**Parâmetros de Query:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `start_date` | string | Não | Data inicial |
| `end_date` | string | Não | Data final |

**Resposta:**

```json
{
  "total_days": 15,
  "total_seconds": 270000.0,
  "total_hours": 75.0,
  "average_seconds_per_day": 18000.0,
  "average_hours_per_day": 5.0,
  "top_language": "TypeScript",
  "top_project": "dev-insights",
  "top_editor": "VS Code"
}
```

---

## Exemplos de Implementação React

### Serviço de API

Crie `src/services/devInsightsService.ts`:

```typescript
import { api } from '../lib/api';
import type {
  DailySummary,
  LanguageStats,
  ProjectStats,
  OverallStats,
  DateRangeParams,
  HealthStatus,
} from '../types/api';

export const devInsightsService = {
  // Health Check
  async getHealth(): Promise<HealthStatus> {
    const { data } = await api.get('/health');
    return data;
  },

  // Resumos
  async getSummaries(params?: DateRangeParams): Promise<DailySummary[]> {
    const { data } = await api.get('/summaries', { params });
    return data;
  },

  async getSummaryByDate(date: string): Promise<DailySummary> {
    const { data } = await api.get(`/summaries/${date}`);
    return data;
  },

  // Linguagens
  async getLanguagesStats(params?: DateRangeParams): Promise<LanguageStats[]> {
    const { data } = await api.get('/languages/stats', { params });
    return data;
  },

  // Projetos
  async getProjectsStats(params?: DateRangeParams): Promise<ProjectStats[]> {
    const { data } = await api.get('/projects/stats', { params });
    return data;
  },

  // Estatísticas Gerais
  async getOverallStats(params?: DateRangeParams): Promise<OverallStats> {
    const { data } = await api.get('/stats', { params });
    return data;
  },
};
```

---

### Hook com React Query (Recomendado)

Crie `src/hooks/useDevInsights.ts`:

```typescript
import { useQuery } from '@tanstack/react-query';
import { devInsightsService } from '../services/devInsightsService';
import type { DateRangeParams } from '../types/api';

// Hook para estatísticas gerais
export function useOverallStats(params?: DateRangeParams) {
  return useQuery({
    queryKey: ['stats', params],
    queryFn: () => devInsightsService.getOverallStats(params),
    staleTime: 1000 * 60 * 5, // 5 minutos
  });
}

// Hook para resumos diários
export function useSummaries(params?: DateRangeParams) {
  return useQuery({
    queryKey: ['summaries', params],
    queryFn: () => devInsightsService.getSummaries(params),
    staleTime: 1000 * 60 * 5,
  });
}

// Hook para linguagens
export function useLanguagesStats(params?: DateRangeParams) {
  return useQuery({
    queryKey: ['languages-stats', params],
    queryFn: () => devInsightsService.getLanguagesStats(params),
    staleTime: 1000 * 60 * 5,
  });
}

// Hook para projetos
export function useProjectsStats(params?: DateRangeParams) {
  return useQuery({
    queryKey: ['projects-stats', params],
    queryFn: () => devInsightsService.getProjectsStats(params),
    staleTime: 1000 * 60 * 5,
  });
}

// Hook para resumo de data específica
export function useSummaryByDate(date: string) {
  return useQuery({
    queryKey: ['summary', date],
    queryFn: () => devInsightsService.getSummaryByDate(date),
    enabled: !!date,
  });
}
```

---

### Componente de Exemplo

```tsx
// src/components/Dashboard.tsx
import { useOverallStats, useLanguagesStats } from '../hooks/useDevInsights';

export function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useOverallStats();
  const { data: languages, isLoading: langsLoading } = useLanguagesStats({ limit: 5 });

  if (statsLoading || langsLoading) {
    return <div>Carregando...</div>;
  }

  return (
    <div className="dashboard">
      {/* Estatísticas Gerais */}
      <section className="stats-overview">
        <h2>Visão Geral</h2>
        <div className="stats-grid">
          <div className="stat-card">
            <span className="stat-value">{stats?.total_hours.toFixed(1)}h</span>
            <span className="stat-label">Total de Horas</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{stats?.average_hours_per_day.toFixed(1)}h</span>
            <span className="stat-label">Média Diária</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{stats?.total_days}</span>
            <span className="stat-label">Dias Ativos</span>
          </div>
        </div>
      </section>

      {/* Top Linguagens */}
      <section className="languages">
        <h2>Top Linguagens</h2>
        <ul>
          {languages?.map((lang) => (
            <li key={lang.name}>
              <span>{lang.name}</span>
              <span>{lang.total_hours.toFixed(1)}h ({lang.percentage}%)</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
```

---

### Configuração do React Query

```tsx
// src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>
);
```

---

## Tratamento de Erros

### Tipos de Erro

| Código HTTP | Descrição | Ação Recomendada |
|-------------|-----------|------------------|
| `400` | Parâmetros inválidos | Validar input do usuário |
| `401` | Não autenticado | Verificar API Key |
| `404` | Recurso não encontrado | Mostrar mensagem amigável |
| `500` | Erro interno | Retry ou contatar suporte |

### Exemplo de Tratamento

```typescript
import axios from 'axios';

export function handleApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const detail = error.response?.data?.detail;

    switch (status) {
      case 401:
        return 'Erro de autenticação. Verifique sua API Key.';
      case 404:
        return detail || 'Recurso não encontrado.';
      case 500:
        return 'Erro interno do servidor. Tente novamente.';
      default:
        return detail || 'Ocorreu um erro inesperado.';
    }
  }
  
  return 'Erro de conexão. Verifique sua internet.';
}
```

---

## Utilitários

### Formatação de Tempo

```typescript
// src/utils/formatTime.ts
export function formatSeconds(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
}

export function formatHours(hours: number): string {
  return `${hours.toFixed(1)}h`;
}
```

### Formatação de Datas

```typescript
// src/utils/formatDate.ts
export function toApiDate(date: Date): string {
  return date.toISOString().split('T')[0]; // "YYYY-MM-DD"
}

export function getLast7Days(): { start_date: string; end_date: string } {
  const end = new Date();
  const start = new Date();
  start.setDate(start.getDate() - 6);
  
  return {
    start_date: toApiDate(start),
    end_date: toApiDate(end),
  };
}

export function getLast30Days(): { start_date: string; end_date: string } {
  const end = new Date();
  const start = new Date();
  start.setDate(start.getDate() - 29);
  
  return {
    start_date: toApiDate(start),
    end_date: toApiDate(end),
  };
}
```

---

## Estrutura de Pastas Sugerida

```
src/
├── components/
│   ├── ...
├── hooks/
│   └── useDevInsights.ts
├── lib/
│   └── api.ts
├── services/
│   └── devInsightsService.ts
├── types/
│   └── api.ts
├── utils/
│   ├── formatTime.ts
│   └── formatDate.ts
├── App.tsx
└── main.tsx
```

---

## Suporte

- **Documentação Interativa:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **Health Check:** `http://localhost:8000/health`
