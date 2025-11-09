import api from './api';

export interface Template {
  id: number;
  trigger: string;
  label: string;
  description?: string;
  content: string;
  category?: string;
  is_system: boolean;
  variables?: string[];
  created_at: string;
  updated_at: string;
}

export interface TemplateCreate {
  trigger: string;
  label: string;
  description?: string;
  content: string;
  category?: string;
  variables?: string[];
}

export interface TemplateUpdate {
  trigger?: string;
  label?: string;
  description?: string;
  content?: string;
  category?: string;
  variables?: string[];
}

export interface TemplateExpand {
  template_id: number;
  values: Record<string, string>;
}

export interface TemplateExpandResponse {
  content: string;
  trigger: string;
  label: string;
}

export const templatesApi = {
  getAll: async (category?: string): Promise<Template[]> => {
    const params = category ? { category } : {};
    const response = await api.get<Template[]>('/api/templates/', { params });
    return response.data;
  },

  getById: async (id: number): Promise<Template> => {
    const response = await api.get<Template>(`/api/templates/${id}`);
    return response.data;
  },

  getByTrigger: async (trigger: string): Promise<Template> => {
    const response = await api.get<Template>(`/api/templates/trigger/${trigger}`);
    return response.data;
  },

  create: async (template: TemplateCreate): Promise<Template> => {
    const response = await api.post<Template>('/api/templates/', template);
    return response.data;
  },

  update: async (id: number, template: TemplateUpdate): Promise<Template> => {
    const response = await api.put<Template>(`/api/templates/${id}`, template);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/api/templates/${id}`);
  },

  expand: async (expand: TemplateExpand): Promise<TemplateExpandResponse> => {
    const response = await api.post<TemplateExpandResponse>('/api/templates/expand', expand);
    return response.data;
  },
};
