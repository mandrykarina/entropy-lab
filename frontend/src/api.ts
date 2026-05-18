import type { ApiErrorResponse, EntropyResponse, ExampleCase } from "./types";

const API_BASE_URL = "http://127.0.0.1:8000";

function extractApiErrorMessage(data: ApiErrorResponse): string {
  if (typeof data.detail === "string") {
    return data.detail;
  }

  if (Array.isArray(data.detail) && data.detail.length > 0) {
    return data.detail
      .map((item) => item.msg ?? "Ошибка валидации данных.")
      .join(" ");
  }

  return "Backend вернул ошибку. Проверьте входные данные.";
}

async function requestJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);

  if (!response.ok) {
    let errorMessage = `Ошибка запроса: ${response.status}`;

    try {
      const errorData = (await response.json()) as ApiErrorResponse;
      errorMessage = extractApiErrorMessage(errorData);
    } catch {
      errorMessage = "Не удалось обработать ответ backend.";
    }

    throw new Error(errorMessage);
  }

  return response.json() as Promise<T>;
}

export async function calculateEntropy(
  systemA: number[],
  systemB: number[]
): Promise<EntropyResponse> {
  return requestJson<EntropyResponse>(`${API_BASE_URL}/calculate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      systemA,
      systemB
    })
  });
}

export async function getExamples(): Promise<ExampleCase[]> {
  return requestJson<ExampleCase[]>(`${API_BASE_URL}/examples`);
}