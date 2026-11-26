import axios from "axios";

import type {
  TranslationRequest,
  TranslationResponse
} from "../types/translation";

const api = axios.create({
  baseURL: "/api",
  timeout: 60000,
  headers: {
    "Content-Type": "application/json"
  }
});

export const translateText = async (
  payload: TranslationRequest
): Promise<TranslationResponse> => {

  const response = await api.post<TranslationResponse>(
    "/translate",
    payload
  );

  return response.data;
};

export const checkHealth = async () => {
  const response = await api.get("/health");
  return response.data;
};

export default api;