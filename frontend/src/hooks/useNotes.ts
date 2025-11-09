import { useState, useCallback } from 'react'
import { Note, NoteList, NoteCreate, NoteUpdate } from '../types/notes'
import { notesApi } from '../services/notesApi'

export function useNotes() {
  const [notes, setNotes] = useState<NoteList[]>([])
  const [selectedNote, setSelectedNote] = useState<Note | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const refreshNotes = useCallback(async () => {
    setIsLoading(true)
    try {
      const fetchedNotes = await notesApi.getNotes()
      setNotes(fetchedNotes)
    } catch (error) {
      console.error('Failed to fetch notes:', error)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const selectNote = useCallback(async (id: number) => {
    setIsLoading(true)
    try {
      const note = await notesApi.getNote(id)
      setSelectedNote(note)
    } catch (error) {
      console.error('Failed to fetch note:', error)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const createNote = useCallback(async (noteData: NoteCreate) => {
    setIsLoading(true)
    try {
      const newNote = await notesApi.createNote(noteData)
      setSelectedNote(newNote)
      await refreshNotes()
    } catch (error) {
      console.error('Failed to create note:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [refreshNotes])

  const updateNote = useCallback(async (id: number, update: NoteUpdate) => {
    setIsLoading(true)
    try {
      const updatedNote = await notesApi.updateNote(id, update)
      setSelectedNote(updatedNote)
      await refreshNotes()
    } catch (error) {
      console.error('Failed to update note:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [refreshNotes])

  const deleteNote = useCallback(async (id: number) => {
    setIsLoading(true)
    try {
      await notesApi.deleteNote(id)
      if (selectedNote?.id === id) {
        setSelectedNote(null)
      }
      await refreshNotes()
    } catch (error) {
      console.error('Failed to delete note:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [selectedNote, refreshNotes])

  return {
    notes,
    selectedNote,
    isLoading,
    refreshNotes,
    selectNote,
    createNote,
    updateNote,
    deleteNote,
  }
}
