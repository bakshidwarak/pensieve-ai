const API_BASE_URL = 'http://localhost:3001/api';

export interface ApiKeyResponse {
  success: boolean;
  message: string;
  has_key: boolean;
}

export const apiKeyApi = {
  async setApiKey(apiKey: string): Promise<ApiKeyResponse> {
    const response = await fetch(`${API_BASE_URL}/templates/settings/api-key`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ api_key: apiKey }),
    });

    if (!response.ok) {
      throw new Error(`Failed to set API key: ${response.statusText}`);
    }

    return response.json();
  },

  async getApiKeyStatus(): Promise<ApiKeyResponse> {
    const response = await fetch(`${API_BASE_URL}/templates/settings/api-key`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get API key status: ${response.statusText}`);
    }

    return response.json();
  },
};
