const API_BASE_URL = 'http://localhost:3001/api';

export interface Template {
  id: string;
  name: string;
  shortcut: string;
  description: string;
  icon: string;
  template: string;
  is_builtin: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

class TemplateApiService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    try {
      console.log(`API: Making request to ${API_BASE_URL}${endpoint}`, options);
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      console.log(`API: Response status: ${response.status}`);
      const data = await response.json();
      console.log(`API: Response data:`, data);

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error('API request failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  // Get all templates
  async getAllTemplates(): Promise<ApiResponse<Template[]>> {
    return this.request<Template[]>('/templates/');
  }

  // Get template by ID
  async getTemplateById(id: string): Promise<ApiResponse<Template>> {
    return this.request<Template>(`/templates/${id}`);
  }

  // Create new template
  async createTemplate(template: Omit<Template, 'id' | 'is_builtin' | 'created_at' | 'updated_at'>): Promise<ApiResponse<Template>> {
    console.log('API: Creating template:', template);
    return this.request<Template>('/templates/', {
      method: 'POST',
      body: JSON.stringify(template),
    });
  }

  // Update template
  async updateTemplate(id: string, template: Omit<Template, 'id' | 'is_builtin' | 'created_at' | 'updated_at'>): Promise<ApiResponse<Template>> {
    console.log('API: Updating template:', id, template);
    return this.request<Template>(`/templates/${id}`, {
      method: 'PUT',
      body: JSON.stringify(template),
    });
  }

  // Delete template
  async deleteTemplate(id: string): Promise<ApiResponse<{ deleted: boolean }>> {
    return this.request<{ deleted: boolean }>(`/templates/${id}`, {
      method: 'DELETE',
    });
  }

  // Create custom copy of built-in template
  async createCustomCopy(id: string, template: Partial<Omit<Template, 'id' | 'is_builtin' | 'created_at' | 'updated_at'>>): Promise<ApiResponse<Template>> {
    console.log('API: Creating custom copy:', id, template);
    return this.request<Template>(`/templates/${id}/copy`, {
      method: 'POST',
      body: JSON.stringify(template),
    });
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<{ message: string; timestamp: string }>> {
    return this.request<{ message: string; timestamp: string }>('/health');
  }
}

export const templateApi = new TemplateApiService();
