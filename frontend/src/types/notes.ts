export interface Tag {
  id: number
  name: string
  color: string
  description?: string
  created_at: string
}

export interface Attachment {
  id: number
  note_id: number
  filename: string
  file_path: string
  file_type: string
  file_size: number
  mime_type?: string
  extracted_text?: string
  created_at: string
}

export interface Note {
  id: number
  title: string
  content: string
  content_type: string
  created_at: string
  updated_at: string
  file_path?: string
  file_type?: string
  file_size?: number
  audio_duration?: number
  vector_id?: string
  tags: Tag[]
  attachments: Attachment[]
}

export interface NoteList {
  id: number
  title: string
  content: string
  content_type: string
  created_at: string
  updated_at: string
  tags: Tag[]
}

export interface NoteCreate {
  title: string
  content: string
  content_type?: string
  tag_names?: string[]
}

export interface NoteUpdate {
  title?: string
  content?: string
  content_type?: string
  tag_names?: string[]
}

export interface SearchRequest {
  query: string
  tag_filter?: string[]
  limit?: number
}

export interface SearchResult {
  note_id: number
  title: string
  tags: string[]
  score: number
  snippet: string
}

export interface TranscribeResponse {
  text: string
  duration?: number
  language?: string
}
