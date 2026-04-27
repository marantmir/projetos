"""
Serviço de armazenamento abstrato para arquivos de vídeo e áudio.

Suporta múltiplos backends: local, AWS S3, Google Cloud Storage.
"""

from pathlib import Path
from typing import BinaryIO, Optional
import shutil

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class StorageService:
    """
    Serviço abstrato de armazenamento de arquivos.
    
    Permite trocar backend de armazenamento via configuração sem
    alterar código da aplicação.
    
    Backends suportados:
    - local: Armazenamento em disco local
    - s3: AWS S3 (implementação futura)
    - gcs: Google Cloud Storage (implementação futura)
    """
    
    def __init__(self, backend: Optional[str] = None):
        """
        Inicializa o serviço de armazenamento.
        
        Args:
            backend: Backend a usar ("local", "s3", "gcs"). Usa config se None.
        """
        self.backend = backend or settings.STORAGE_BACKEND
        self.local_path = Path(settings.STORAGE_LOCAL_PATH)
        
        if self.backend == "local":
            self.local_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"StorageService inicializado (local): {self.local_path}")
        elif self.backend == "s3":
            logger.info(f"StorageService inicializado (S3): {settings.AWS_S3_BUCKET}")
            # TODO: Inicializar cliente boto3
        elif self.backend == "gcs":
            logger.info(f"StorageService inicializado (GCS): {settings.GCS_BUCKET}")
            # TODO: Inicializar cliente google-cloud-storage
        else:
            raise ValueError(f"Backend de armazenamento inválido: {self.backend}")
    
    def save_file(
        self,
        file_obj: BinaryIO,
        destination_path: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Salva um arquivo no backend configurado.
        
        Args:
            file_obj: Objeto de arquivo binário.
            destination_path: Caminho de destino relativo.
            content_type: MIME type do arquivo (usado em S3/GCS).
        
        Returns:
            URI ou caminho onde o arquivo foi salvo.
        """
        if self.backend == "local":
            return self._save_local(file_obj, destination_path)
        elif self.backend == "s3":
            return self._save_s3(file_obj, destination_path, content_type)
        elif self.backend == "gcs":
            return self._save_gcs(file_obj, destination_path, content_type)
    
    def _save_local(self, file_obj: BinaryIO, destination_path: str) -> str:
        """Salva arquivo localmente."""
        full_path = self.local_path / destination_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'wb') as f:
            shutil.copyfileobj(file_obj, f)
        
        logger.info(f"Arquivo salvo localmente: {full_path}")
        return str(full_path)
    
    def _save_s3(
        self,
        file_obj: BinaryIO,
        destination_path: str,
        content_type: Optional[str]
    ) -> str:
        """Salva arquivo no S3."""
        # TODO: Implementar com boto3
        logger.warning("Storage S3 não implementado ainda. Usando fallback local.")
        return self._save_local(file_obj, destination_path)
    
    def _save_gcs(
        self,
        file_obj: BinaryIO,
        destination_path: str,
        content_type: Optional[str]
    ) -> str:
        """Salva arquivo no Google Cloud Storage."""
        # TODO: Implementar com google-cloud-storage
        logger.warning("Storage GCS não implementado ainda. Usando fallback local.")
        return self._save_local(file_obj, destination_path)
    
    def delete_file(self, file_path: str) -> bool:
        """
        Remove um arquivo do armazenamento.
        
        Args:
            file_path: Caminho do arquivo a remover.
        
        Returns:
            True se removido com sucesso, False caso contrário.
        """
        if self.backend == "local":
            return self._delete_local(file_path)
        elif self.backend == "s3":
            return self._delete_s3(file_path)
        elif self.backend == "gcs":
            return self._delete_gcs(file_path)
    
    def _delete_local(self, file_path: str) -> bool:
        """Remove arquivo local."""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Arquivo removido: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao remover arquivo {file_path}: {e}")
            return False
    
    def _delete_s3(self, file_path: str) -> bool:
        """Remove arquivo do S3."""
        # TODO: Implementar
        logger.warning("Delete S3 não implementado.")
        return False
    
    def _delete_gcs(self, file_path: str) -> bool:
        """Remove arquivo do GCS."""
        # TODO: Implementar
        logger.warning("Delete GCS não implementado.")
        return False
    
    def get_file_url(self, file_path: str) -> str:
        """
        Obtém URL pública ou assinada do arquivo.
        
        Args:
            file_path: Caminho do arquivo.
        
        Returns:
            URL de acesso ao arquivo.
        """
        if self.backend == "local":
            return f"file://{file_path}"
        elif self.backend == "s3":
            # TODO: Gerar presigned URL
            return f"s3://{settings.AWS_S3_BUCKET}/{file_path}"
        elif self.backend == "gcs":
            # TODO: Gerar signed URL
            return f"gs://{settings.GCS_BUCKET}/{file_path}"


def get_storage_service() -> StorageService:
    """
    Factory function para StorageService.
    
    Returns:
        Instância do StorageService.
    """
    return StorageService()
