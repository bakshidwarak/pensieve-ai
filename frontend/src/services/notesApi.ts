import api from './api'
import {  Note, NoteList, NoteCreate, NoteUpdate, Tag, SearchRequest, TranscribeResponse } from '../types/notes'

export const notesApi = {
  // Notes CRUD
  createNote: async (note: NoteCreate): Promise<Note> => {
    const response = await api.post<Note>('/api/notes/', note)
    return response.data
  },

  getNotes: async (skip = 0, limit = 100, tags?: string): Promise<NoteList[]> => {
    const params = new URLSearchParams()
    params.append('skip', skip.toString())
    params.append('limit', limit.toString())
    if (tags) params.append('tags', tags)

    const response = await api.get<NoteList[]>(`/api/notes/?${params.toString()}`)
    return response.data
  },

  getNote: async (id: number): Promise<Note> => {
    const response = await api.get<Note>(`/api/notes/${id}`)
    return response.data
  },

  updateNote: async (id: number, update: NoteUpdate): Promise<Note> => {
    const response = await api.put<Note>(`/api/notes/${id}`, update)
    return response.data
  },

  deleteNote: async (id: number): Promise<void> => {
    await api.delete(`/api/notes/${id}`)
  },

  // File attachments
  addAttachment: async (noteId: number, file: File): Promise<any> => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post(`/api/notes/${noteId}/attachments`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Search
  searchNotes: async (request: SearchRequest): Promise<any[]> => {
    const response = await api.post('/api/notes/search', request)
    return response.data
  },

  // Tags
  getTags: async (): Promise<Tag[]> => {
    const response = await api.get<Tag[]>('/api/notes/tags/all')
    return response.data
  },

  createTag: async (name: string, color?: string, description?: string): Promise<Tag> => {
    const response = await api.post<Tag>('/api/notes/tags', {
      name,
      color: color || '#667eea',
      description,
    })
    return response.data
  },
}

export const transcribeApi = {
  transcribe: async (file: File, language = 'en'): Promise<TranscribeResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('language', language)

    const response = await api.post<TranscribeResponse>('/api/transcribe/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  transcribeRecording: async (audioBlob: Blob, language = 'en'): Promise<TranscribeResponse> => {
    const formData = new FormData()
    formData.append('audio_data', audioBlob, 'recording.webm')
    formData.append('language', language)

    const response = await api.post<TranscribeResponse>('/api/transcribe/from-recording', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
}
