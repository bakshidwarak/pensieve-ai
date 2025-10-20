import os
import uuid
from datetime import datetime
from typing import List, Dict, Any
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        self.backup_dir = os.getenv("BACKUP_DIRECTORY", "./data/backups")
    
    async def ensure_backup_directory(self):
        """Ensure backup directory exists"""
        os.makedirs(self.backup_dir, exist_ok=True)
    
    async def process_document(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process document into chunks"""
        try:
            if metadata is None:
                metadata = {}
            
            # Create document chunks
            chunks = self.text_splitter.split_text(content)
            
            # Create document objects with metadata
            documents = []
            for i, chunk in enumerate(chunks):
                doc_metadata = {
                    **metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "timestamp": datetime.now().isoformat(),
                    "type": self.detect_document_type(content)
                }
                
                documents.append({
                    "id": str(uuid.uuid4()),
                    "content": chunk,
                    "metadata": doc_metadata
                })
            
            return {
                "success": True,
                "documents": documents,
                "chunk_count": len(chunks)
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing document: {e}")
            raise e
    
    def detect_document_type(self, content: str) -> str:
        """Detect the type of document based on content"""
        content_lower = content.lower()
        
        if "[meeting]" in content_lower or "[meet]" in content_lower:
            return "meeting"
        elif "[todo]" in content_lower or "[task]" in content_lower:
            return "todo"
        elif "[feedback]" in content_lower or "[feed]" in content_lower:
            return "feedback"
        elif "[interview]" in content_lower:
            return "interview"
        elif "[note]" in content_lower or "[notes]" in content_lower:
            return "note"
        elif "[decision]" in content_lower:
            return "decision"
        else:
            return "general"
    
    async def backup_document(self, content: str, filename: str = None) -> Dict[str, Any]:
        """Backup document to file"""
        try:
            await self.ensure_backup_directory()
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"backup_{timestamp}.txt"
            
            backup_path = os.path.join(self.backup_dir, filename)
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ Document backed up to {backup_path}")
            return {
                "success": True,
                "backup_path": backup_path,
                "filename": filename
            }
            
        except Exception as e:
            logger.error(f"❌ Error backing up document: {e}")
            raise e
    
    async def get_backup_files(self) -> Dict[str, Any]:
        """Get list of backup files"""
        try:
            await self.ensure_backup_directory()
            
            files = []
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.txt'):
                    file_path = os.path.join(self.backup_dir, filename)
                    stat = os.stat(file_path)
                    files.append({
                        "filename": filename,
                        "path": file_path,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            # Sort by modification time (newest first)
            files.sort(key=lambda x: x["modified"], reverse=True)
            
            return {
                "success": True,
                "files": files
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting backup files: {e}")
            raise e
    
    async def clear_backups(self) -> Dict[str, Any]:
        """Clear all backup files"""
        try:
            await self.ensure_backup_directory()
            
            files_removed = 0
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.txt'):
                    os.remove(os.path.join(self.backup_dir, filename))
                    files_removed += 1
            
            logger.info(f"✅ Cleared {files_removed} backup files")
            return {
                "success": True,
                "files_removed": files_removed
            }
            
        except Exception as e:
            logger.error(f"❌ Error clearing backups: {e}")
            raise e
