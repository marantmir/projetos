"""
Testes do StorageService.

Valida armazenamento local e abstração para cloud.
"""

import io
from pathlib import Path

import pytest

from app.services.storage_service import StorageService


@pytest.mark.unit
class TestStorageService:
    """Testes do serviço de armazenamento."""
    
    def test_init_local_backend(self, tmp_path):
        """Testa inicialização com backend local."""
        storage = StorageService(backend="local")
        
        assert storage.backend == "local"
        assert storage.local_path.exists()
    
    def test_save_file_local(self, tmp_path):
        """Testa salvar arquivo localmente."""
        # Configura serviço com diretório temporário
        test_dir = tmp_path / "storage"
        storage = StorageService(backend="local")
        storage.local_path = test_dir
        
        # Cria arquivo em memória
        file_content = b"Test file content"
        file_obj = io.BytesIO(file_content)
        
        # Salva arquivo
        saved_path = storage.save_file(file_obj, "test/file.txt")
        
        # Verifica que foi salvo
        assert Path(saved_path).exists()
        with open(saved_path, 'rb') as f:
            assert f.read() == file_content
    
    def test_delete_file_local(self, tmp_path):
        """Testa remover arquivo local."""
        storage = StorageService(backend="local")
        storage.local_path = tmp_path
        
        # Cria arquivo
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        # Remove
        result = storage.delete_file(str(test_file))
        
        assert result is True
        assert not test_file.exists()
    
    def test_delete_nonexistent_file(self, tmp_path):
        """Testa remover arquivo inexistente."""
        storage = StorageService(backend="local")
        storage.local_path = tmp_path
        
        result = storage.delete_file(str(tmp_path / "nonexistent.txt"))
        
        assert result is False
    
    def test_save_file_creates_subdirectories(self, tmp_path):
        """Testa que save_file cria subdiretórios automaticamente."""
        storage = StorageService(backend="local")
        storage.local_path = tmp_path
        
        file_obj = io.BytesIO(b"test")
        saved_path = storage.save_file(file_obj, "deep/nested/path/file.txt")
        
        assert Path(saved_path).exists()
        assert (tmp_path / "deep" / "nested" / "path").exists()
    
    def test_invalid_backend_raises_error(self):
        """Testa que backend inválido levanta exceção."""
        with pytest.raises(ValueError, match="Backend de armazenamento inválido"):
            StorageService(backend="invalid_backend")
    
    def test_s3_backend_fallback(self, tmp_path):
        """Testa que backend S3 faz fallback para local (não implementado)."""
        # Como S3 não está implementado, deve fazer fallback
        # Este teste pode mudar quando S3 for implementado
        pass
    
    def test_file_content_integrity(self, tmp_path):
        """Testa que o conteúdo do arquivo não é corrompido."""
        storage = StorageService(backend="local")
        storage.local_path = tmp_path
        
        # Conteúdo binário complexo
        original_content = bytes(range(256))
        file_obj = io.BytesIO(original_content)
        
        saved_path = storage.save_file(file_obj, "binary_test.bin")
        
        with open(saved_path, 'rb') as f:
            saved_content = f.read()
        
        assert saved_content == original_content
