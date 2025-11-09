import { useState, useRef } from 'react'
import { notesApi } from '../services/notesApi'
import './FileUploader.css'

interface FileUploaderProps {
  noteId: number
  onUploadComplete: () => void
}

function FileUploader({ noteId, onUploadComplete }: FileUploaderProps) {
  const [isUploading, setIsUploading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const supportedTypes = {
    'Images': ['.png', '.jpg', '.jpeg', '.gif', '.bmp'],
    'PDFs': ['.pdf'],
    'Documents': ['.docx', '.pptx'],
    'Text': ['.txt', '.md'],
  }

  const allExtensions = Object.values(supportedTypes).flat().join(', ')

  const handleFileSelect = (file: File) => {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase()
    const isSupported = Object.values(supportedTypes).flat().includes(ext)

    if (!isSupported) {
      alert(`Unsupported file type. Supported types: ${allExtensions}`)
      return
    }

    setSelectedFile(file)
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0])
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0])
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setIsUploading(true)
    try {
      await notesApi.addAttachment(noteId, selectedFile)
      setSelectedFile(null)
      onUploadComplete()
    } catch (error) {
      console.error('Upload failed:', error)
      alert('Failed to upload file')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="file-uploader">
      <div
        className={`drop-zone ${dragActive ? 'active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={allExtensions}
          onChange={handleFileInput}
          style={{ display: 'none' }}
        />

        {selectedFile ? (
          <div className="selected-file">
            <span className="file-icon">📄</span>
            <div className="file-info">
              <p className="file-name">{selectedFile.name}</p>
              <p className="file-size">{(selectedFile.size / 1024).toFixed(1)} KB</p>
            </div>
          </div>
        ) : (
          <div className="drop-zone-content">
            <span className="upload-icon">📁</span>
            <p>Drag and drop a file here, or click to browse</p>
            <p className="supported-types">
              Supported: Images, PDFs, Documents (DOCX, PPTX), Text files
            </p>
          </div>
        )}
      </div>

      {selectedFile && (
        <div className="upload-actions">
          <button
            className="cancel-btn"
            onClick={() => setSelectedFile(null)}
            disabled={isUploading}
          >
            Cancel
          </button>
          <button
            className="upload-btn"
            onClick={handleUpload}
            disabled={isUploading}
          >
            {isUploading ? 'Uploading...' : 'Upload'}
          </button>
        </div>
      )}
    </div>
  )
}

export default FileUploader
