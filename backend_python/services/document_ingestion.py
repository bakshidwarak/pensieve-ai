import asyncio
import logging
import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from services.vector_db import VectorDBService
from services.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

class DocumentIngestionService:
    def __init__(self):
        self.vector_db = VectorDBService()
        self.document_processor = DocumentProcessor()
        self.is_processing = False
        self.pending_documents = []
        self.auto_backup_interval = int(os.getenv("AUTO_BACKUP_INTERVAL", 300))  # 5 minutes
    
    async def initialize(self):
        """Initialize the document ingestion service"""
        try:
            await self.vector_db.initialize()
            await self.document_processor.ensure_backup_directory()
            
            # Start auto-backup task
            asyncio.create_task(self.auto_backup_loop())
            
            logger.info("✅ Document Ingestion Service initialized")
        except Exception as e:
            logger.error(f"❌ Document Ingestion Service initialization failed: {e}")
            raise e
    
    async def auto_backup_loop(self):
        """Auto-backup loop that runs every 5 minutes"""
        while True:
            try:
                await asyncio.sleep(self.auto_backup_interval)
                if self.pending_documents:
                    logger.info("🔄 Auto-backup triggered...")
                    await self.process_pending_documents()
            except Exception as e:
                logger.error(f"❌ Auto-backup error: {e}")
    
    async def ingest_document(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Ingest a document for processing"""
        try:
            logger.info("📄 Ingesting document...")
            
            if metadata is None:
                metadata = {}
            
            # Add to pending documents queue
            self.pending_documents.append({
                "content": content,
                "metadata": {
                    **metadata,
                    "timestamp": datetime.now().isoformat(),
                    "id": str(uuid.uuid4())
                }
            })
            
            # Process immediately if not already processing
            if not self.is_processing:
                await self.process_pending_documents()
            
            return {
                "success": True,
                "message": "Document queued for processing",
                "queue_length": len(self.pending_documents)
            }
            
        except Exception as e:
            logger.error(f"❌ Error ingesting document: {e}")
            raise e
    
    async def process_pending_documents(self):
        """Process all pending documents"""
        if self.is_processing or not self.pending_documents:
            return
        
        self.is_processing = True
        logger.info(f"🔄 Processing {len(self.pending_documents)} pending documents...")
        
        try:
            documents = self.pending_documents.copy()
            self.pending_documents.clear()
            
            # Process each document
            for doc in documents:
                await self.process_single_document(doc)
            
            logger.info("✅ All pending documents processed")
        except Exception as e:
            logger.error(f"❌ Error processing pending documents: {e}")
        finally:
            self.is_processing = False
    
    async def process_single_document(self, document: Dict[str, Any]):
        """Process a single document"""
        try:
            # Process document into chunks
            processed = await self.document_processor.process_document(
                document["content"],
                document["metadata"]
            )
            
            if not processed["success"]:
                raise Exception("Document processing failed")
            
            # Add to vector database
            vector_result = await self.vector_db.add_documents(processed["documents"])
            
            if not vector_result["success"]:
                raise Exception("Vector database insertion failed")
            
            # Backup the document
            await self.document_processor.backup_document(
                document["content"],
                f"doc_{document['metadata']['id']}.txt"
            )
            
            logger.info(f"✅ Document {document['metadata']['id']} processed and indexed")
        except Exception as e:
            logger.error(f"❌ Error processing document {document['metadata']['id']}: {e}")
            # Re-queue the document for retry
            self.pending_documents.append(document)
    
    async def force_process_all(self) -> Dict[str, Any]:
        """Force process all pending documents"""
        logger.info("🚀 Force processing all pending documents...")
        await self.process_pending_documents()
        
        return {
            "success": True,
            "message": "All pending documents processed",
            "queue_length": len(self.pending_documents)
        }
    
    async def clear_and_ingest(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Clear screen and ingest content immediately"""
        try:
            logger.info("🧹 Clearing screen and ingesting content...")
            
            if metadata is None:
                metadata = {}
            
            # Process the document immediately
            processed = await self.document_processor.process_document(content, metadata)
            
            if not processed["success"]:
                raise Exception("Document processing failed")
            
            # Add to vector database
            vector_result = await self.vector_db.add_documents(processed["documents"])
            
            if not vector_result["success"]:
                raise Exception("Vector database insertion failed")
            
            # Backup the document
            backup_result = await self.document_processor.backup_document(
                content,
                f"clear_slate_{int(datetime.now().timestamp())}.txt"
            )
            
            return {
                "success": True,
                "message": "Content processed and screen cleared",
                "chunk_count": processed["chunk_count"],
                "backup_path": backup_result["backup_path"]
            }
            
        except Exception as e:
            logger.error(f"❌ Error in clear and ingest: {e}")
            raise e
    
    async def get_ingestion_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics"""
        try:
            vector_stats = await self.vector_db.get_collection_stats()
            backup_files = await self.document_processor.get_backup_files()
            
            return {
                "success": True,
                "vector_db": vector_stats,
                "backup_files": len(backup_files["files"]) if backup_files["success"] else 0,
                "pending_documents": len(self.pending_documents),
                "is_processing": self.is_processing
            }
        except Exception as e:
            logger.error(f"❌ Error getting ingestion stats: {e}")
            raise e
    
    async def clear_all_data(self) -> Dict[str, Any]:
        """Clear all data"""
        try:
            logger.info("🗑️ Clearing all data...")
            
            # Clear pending documents
            self.pending_documents.clear()
            
            # Clear backups
            await self.document_processor.clear_backups()
            
            return {
                "success": True,
                "message": "All data cleared"
            }
        except Exception as e:
            logger.error(f"❌ Error clearing all data: {e}")
            raise e
