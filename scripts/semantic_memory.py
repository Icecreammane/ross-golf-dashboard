#!/Users/clawdbot/clawd/memory/venv/bin/python3
"""
Semantic Memory System for Jarvis
Production-ready vector search over memory files and conversations.
"""

import os
import json
import time
import glob
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import hashlib

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: pip3 install chromadb sentence-transformers")
    exit(1)


class SemanticMemory:
    """Vector-based semantic search over Jarvis's memory."""
    
    def __init__(self, config_path: str = None):
        """Initialize semantic memory system."""
        if config_path is None:
            config_path = "/Users/clawdbot/clawd/memory/memory_config.json"
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize Chroma client
        self.client = chromadb.PersistentClient(
            path=self.config['vector_db_path'],
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.config['collection_name'],
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize embedding model (lazy load)
        self._model = None
        
        print(f"✓ Semantic memory initialized")
        print(f"  DB: {self.config['vector_db_path']}")
        print(f"  Collection: {self.config['collection_name']}")
    
    @property
    def model(self):
        """Lazy load embedding model."""
        if self._model is None:
            print(f"Loading embedding model: {self.config['embedding_model']}")
            self._model = SentenceTransformer(self.config['embedding_model'])
        return self._model
    
    def chunk_text(self, text: str, metadata: Dict) -> List[Tuple[str, Dict]]:
        """Split text into chunks with metadata."""
        chunk_size = self.config['chunk_size']
        overlap = self.config['chunk_overlap']
        
        # Simple paragraph-based chunking
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para)
            
            if current_size + para_size > chunk_size and current_chunk:
                # Save current chunk
                chunk_text = '\n\n'.join(current_chunk)
                chunk_meta = metadata.copy()
                chunk_meta['chunk_id'] = len(chunks)
                chunks.append((chunk_text, chunk_meta))
                
                # Start new chunk with overlap
                if overlap > 0 and current_chunk:
                    current_chunk = [current_chunk[-1]]  # Keep last paragraph
                    current_size = len(current_chunk[0])
                else:
                    current_chunk = []
                    current_size = 0
            
            current_chunk.append(para)
            current_size += para_size
        
        # Add final chunk
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunk_meta = metadata.copy()
            chunk_meta['chunk_id'] = len(chunks)
            chunks.append((chunk_text, chunk_meta))
        
        return chunks
    
    def embed_file(self, file_path: str, source_type: str) -> int:
        """Embed a single file into the vector database."""
        if not os.path.exists(file_path):
            print(f"⚠ File not found: {file_path}")
            return 0
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        if not content.strip():
            print(f"⚠ Empty file: {file_path}")
            return 0
        
        # Create metadata
        file_stat = os.stat(file_path)
        metadata = {
            'source_file': file_path,
            'source_type': source_type,
            'file_name': os.path.basename(file_path),
            'modified_time': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            'embedded_time': datetime.now().isoformat()
        }
        
        # Chunk the content
        chunks = self.chunk_text(content, metadata)
        
        if not chunks:
            print(f"⚠ No chunks created from: {file_path}")
            return 0
        
        # Create embeddings
        texts = [chunk[0] for chunk in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=False).tolist()
        
        # Generate IDs
        ids = []
        metadatas = []
        for i, (text, meta) in enumerate(chunks):
            # Use content hash + metadata for stable IDs
            content_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            chunk_id = f"{meta['file_name']}_{content_hash}_{i}"
            ids.append(chunk_id)
            metadatas.append(meta)
        
        # Add to collection (upsert to handle updates)
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
        print(f"✓ Embedded {len(chunks)} chunks from {os.path.basename(file_path)}")
        return len(chunks)
    
    def embed_all_sources(self) -> Dict[str, int]:
        """Embed all configured source files."""
        stats = {}
        
        # Embed main memory file
        if os.path.exists(self.config['sources']['memory_file']):
            stats['MEMORY.md'] = self.embed_file(
                self.config['sources']['memory_file'],
                'memory'
            )
        
        # Embed journal
        if os.path.exists(self.config['sources']['journal_file']):
            stats['jarvis-journal.md'] = self.embed_file(
                self.config['sources']['journal_file'],
                'journal'
            )
        
        # Embed daily logs
        daily_logs = glob.glob(self.config['sources']['daily_logs_pattern'])
        for log_file in daily_logs:
            file_name = os.path.basename(log_file)
            stats[file_name] = self.embed_file(log_file, 'daily_log')
        
        return stats
    
    def search(self, query: str, n_results: int = None, 
               source_type: str = None) -> List[Dict]:
        """
        Search memory with semantic similarity.
        
        Args:
            query: Natural language search query
            n_results: Number of results to return (default from config)
            source_type: Filter by source type (memory/journal/daily_log/conversation)
        
        Returns:
            List of results with text, metadata, and relevance scores
        """
        start_time = time.time()
        
        if n_results is None:
            n_results = self.config['max_search_results']
        
        # Embed query
        query_embedding = self.model.encode([query], show_progress_bar=False).tolist()[0]
        
        # Build where filter
        where_filter = None
        if source_type:
            where_filter = {"source_type": source_type}
        
        # Search collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None,
                    'relevance': 1.0 - (results['distances'][0][i] if 'distances' in results else 0.5)
                })
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Check performance target
        if elapsed_ms > self.config['search_timeout_ms']:
            print(f"⚠ Search took {elapsed_ms:.0f}ms (target: {self.config['search_timeout_ms']}ms)")
        
        return formatted_results
    
    def check_memory_before_response(self, user_message: str) -> Optional[str]:
        """
        Check memory for relevant context before responding.
        Returns context summary if relevant memories found, None otherwise.
        """
        results = self.search(user_message, n_results=3)
        
        if not results or results[0]['relevance'] < 0.7:
            return None
        
        # Format context
        context_parts = []
        for i, result in enumerate(results):
            if result['relevance'] < 0.6:
                break
            
            source = result['metadata'].get('file_name', 'unknown')
            text = result['text'][:200] + '...' if len(result['text']) > 200 else result['text']
            
            context_parts.append(f"From {source}: {text}")
        
        if context_parts:
            return "Context from memory:\n" + "\n\n".join(context_parts)
        
        return None
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector database."""
        count = self.collection.count()
        
        # Get breakdown by source type
        source_types = {}
        if count > 0:
            # Sample to get source type distribution
            sample = self.collection.get(limit=1000)
            if sample['metadatas']:
                for meta in sample['metadatas']:
                    stype = meta.get('source_type', 'unknown')
                    source_types[stype] = source_types.get(stype, 0) + 1
        
        return {
            'total_chunks': count,
            'source_types': source_types,
            'collection_name': self.config['collection_name'],
            'db_path': self.config['vector_db_path']
        }
    
    def prune_old_embeddings(self, days: int = None) -> int:
        """Remove embeddings older than specified days."""
        if days is None:
            days = self.config['retention_days']
        
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_iso = cutoff_date.isoformat()
        
        # Get all documents
        all_docs = self.collection.get()
        
        # Find old IDs
        old_ids = []
        for i, meta in enumerate(all_docs['metadatas']):
            embedded_time = meta.get('embedded_time', '')
            if embedded_time and embedded_time < cutoff_iso:
                old_ids.append(all_docs['ids'][i])
        
        # Delete old embeddings
        if old_ids:
            self.collection.delete(ids=old_ids)
            print(f"✓ Pruned {len(old_ids)} embeddings older than {days} days")
        
        return len(old_ids)
    
    def reset(self):
        """Clear all embeddings (use with caution!)."""
        self.client.delete_collection(self.config['collection_name'])
        self.collection = self.client.get_or_create_collection(
            name=self.config['collection_name'],
            metadata={"hnsw:space": "cosine"}
        )
        print("✓ Memory database reset")


def main():
    """Test/demo the semantic memory system."""
    import sys
    
    mem = SemanticMemory()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'embed':
            print("Embedding all sources...")
            stats = mem.embed_all_sources()
            print("\nEmbedding complete:")
            for source, count in stats.items():
                print(f"  {source}: {count} chunks")
        
        elif command == 'stats':
            stats = mem.get_stats()
            print(f"Total chunks: {stats['total_chunks']}")
            print(f"Collection: {stats['collection_name']}")
            print(f"Source breakdown:")
            for stype, count in stats['source_types'].items():
                print(f"  {stype}: {count}")
        
        elif command == 'prune':
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            pruned = mem.prune_old_embeddings(days)
            print(f"Pruned {pruned} old embeddings")
        
        elif command == 'reset':
            confirm = input("Reset all embeddings? (yes/no): ")
            if confirm.lower() == 'yes':
                mem.reset()
        
        else:
            print(f"Unknown command: {command}")
            print("Usage: semantic_memory.py [embed|stats|prune|reset]")
    
    else:
        print("Semantic Memory System")
        print("Usage: semantic_memory.py [embed|stats|prune|reset]")


if __name__ == '__main__':
    main()
