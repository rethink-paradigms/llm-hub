"""
Unit tests for Catalog API public functions.

Tests the public API exposed in llmhub_cli.catalog module.
"""
import pytest
from unittest.mock import patch, Mock
from llmhub_cli.catalog import (
    build_catalog,
    get_catalog,
    Catalog,
    CanonicalModel,
)


@pytest.fixture
def mock_catalog():
    """Return a mock catalog with sample models."""
    models = [
        CanonicalModel(
            canonical_id="openai:gpt-4o-mini",
            provider="openai",
            model_id="gpt-4o-mini",
            cost_tier=1,
            quality_tier=2,
            tags=["chat", "general"],
            input_modalities=["text"],
            output_modalities=["text"],
            price_input_per_million=0.15,
            price_output_per_million=0.60,
        ),
        CanonicalModel(
            canonical_id="openai:gpt-4o",
            provider="openai",
            model_id="gpt-4o",
            cost_tier=4,
            quality_tier=1,
            tags=["chat", "reasoning", "vision"],
            input_modalities=["text", "image"],
            output_modalities=["text"],
            price_input_per_million=2.50,
            price_output_per_million=10.00,
        ),
        CanonicalModel(
            canonical_id="anthropic:claude-3-5-sonnet-20241022",
            provider="anthropic",
            model_id="claude-3-5-sonnet-20241022",
            cost_tier=3,
            quality_tier=1,
            tags=["chat", "reasoning"],
            input_modalities=["text"],
            output_modalities=["text"],
            price_input_per_million=3.00,
            price_output_per_million=15.00,
        ),
        CanonicalModel(
            canonical_id="openai:text-embedding-3-small",
            provider="openai",
            model_id="text-embedding-3-small",
            cost_tier=1,
            quality_tier=3,
            tags=["embedding"],
            input_modalities=["text"],
            output_modalities=["embedding"],
            price_input_per_million=0.02,
            price_output_per_million=0.00,
        ),
    ]
    return Catalog(models=models, built_at="2024-12-02T00:00:00")


class TestBuildCatalog:
    """Tests for build_catalog function."""
    
    @pytest.mark.skip(reason="Requires network access - run in integration tests")
    def test_build_catalog_success(self):
        """Test building catalog successfully."""
        catalog = build_catalog()
        
        assert isinstance(catalog, Catalog)
        assert len(catalog.models) > 0
        assert all(isinstance(m, CanonicalModel) for m in catalog.models)
    
    @pytest.mark.skip(reason="Requires network access - run in integration tests")
    def test_build_catalog_with_cache(self):
        """Test building catalog uses cache when fresh."""
        # First call
        catalog1 = build_catalog(ttl_hours=24)
        
        # Second call should use cache
        catalog2 = build_catalog(ttl_hours=24)
        
        # Should return same data (from cache)
        assert len(catalog1.models) == len(catalog2.models)
    
    @pytest.mark.skip(reason="Requires network access - run in integration tests")
    def test_build_catalog_force_refresh(self):
        """Test force refresh ignores cache."""
        catalog = build_catalog(force_refresh=True)
        
        assert isinstance(catalog, Catalog)
        assert len(catalog.models) > 0
    
    def test_build_catalog_returns_catalog_type(self):
        """Test that build_catalog returns Catalog type."""
        with patch('llmhub_cli.catalog.builder.build_catalog') as mock_build:
            mock_build.return_value = Catalog(models=[], built_at="2024-12-02")
            
            catalog = build_catalog()
            
            assert isinstance(catalog, Catalog)


class TestGetCatalog:
    """Tests for get_catalog function."""
    
    def test_get_catalog_with_provider_filter(self, mock_catalog):
        """Test filtering catalog by provider."""
        with patch('llmhub_cli.catalog.build_catalog', return_value=mock_catalog):
            catalog = get_catalog(provider="openai")
            
            assert all(m.provider == "openai" for m in catalog.models)
            assert len(catalog.models) == 3  # 3 OpenAI models in fixture
    
    def test_get_catalog_with_tags_filter(self, mock_catalog):
        """Test filtering catalog by tags."""
        with patch('llmhub_cli.catalog.build_catalog', return_value=mock_catalog):
            catalog = get_catalog(tags=["reasoning"])
            
            assert all("reasoning" in m.tags for m in catalog.models)
            assert len(catalog.models) == 2  # 2 models with reasoning tag
    
    def test_get_catalog_with_multiple_filters(self, mock_catalog):
        """Test filtering catalog by provider and tags."""
        with patch('llmhub_cli.catalog.build_catalog', return_value=mock_catalog):
            catalog = get_catalog(provider="openai", tags=["vision"])
            
            assert all(m.provider == "openai" for m in catalog.models)
            assert all("vision" in m.tags for m in catalog.models)
            assert len(catalog.models) == 1  # Only gpt-4o
    
    def test_get_catalog_empty_results(self, mock_catalog):
        """Test filtering returns empty catalog when no matches."""
        with patch('llmhub_cli.catalog.build_catalog', return_value=mock_catalog):
            catalog = get_catalog(provider="nonexistent")
            
            assert len(catalog.models) == 0
    
    def test_get_catalog_no_filters(self, mock_catalog):
        """Test get_catalog with no filters returns all models."""
        with patch('llmhub_cli.catalog.build_catalog', return_value=mock_catalog):
            catalog = get_catalog()
            
            assert len(catalog.models) == len(mock_catalog.models)
    
    def test_get_catalog_force_refresh(self, mock_catalog):
        """Test get_catalog passes force_refresh parameter."""
        with patch('llmhub_cli.catalog.build_catalog', return_value=mock_catalog) as mock_build:
            get_catalog(force_refresh=True)
            
            mock_build.assert_called_once()
            call_kwargs = mock_build.call_args.kwargs
            assert call_kwargs.get('force_refresh') is True
    
    def test_get_catalog_ttl_hours(self, mock_catalog):
        """Test get_catalog passes ttl_hours parameter."""
        with patch('llmhub_cli.catalog.build_catalog', return_value=mock_catalog) as mock_build:
            get_catalog(ttl_hours=48)
            
            mock_build.assert_called_once()
            call_kwargs = mock_build.call_args.kwargs
            assert call_kwargs.get('ttl_hours') == 48
    
    def test_get_catalog_tags_single_string(self, mock_catalog):
        """Test get_catalog accepts single tag as string."""
        with patch('llmhub_cli.catalog.build_catalog', return_value=mock_catalog):
            catalog = get_catalog(tags="reasoning")
            
            assert all("reasoning" in m.tags for m in catalog.models)
    
    def test_get_catalog_tags_list(self, mock_catalog):
        """Test get_catalog accepts tags as list."""
        with patch('llmhub_cli.catalog.build_catalog', return_value=mock_catalog):
            catalog = get_catalog(tags=["chat", "reasoning"])
            
            # Should return models that have ALL specified tags
            for model in catalog.models:
                assert "chat" in model.tags and "reasoning" in model.tags


class TestCatalogModel:
    """Tests for Catalog model."""
    
    def test_catalog_has_models_attribute(self, mock_catalog):
        """Test Catalog has models attribute."""
        assert hasattr(mock_catalog, 'models')
        assert isinstance(mock_catalog.models, list)
    
    def test_catalog_has_built_at_attribute(self, mock_catalog):
        """Test Catalog has built_at timestamp."""
        assert hasattr(mock_catalog, 'built_at')
        assert isinstance(mock_catalog.built_at, str)
    
    def test_catalog_models_are_canonical_models(self, mock_catalog):
        """Test all catalog models are CanonicalModel instances."""
        assert all(isinstance(m, CanonicalModel) for m in mock_catalog.models)


class TestCanonicalModelModel:
    """Tests for CanonicalModel model."""
    
    def test_canonical_model_required_fields(self):
        """Test CanonicalModel has required fields."""
        model = CanonicalModel(
            canonical_id="test:test-model",
            provider="test",
            model_id="test-model",
            cost_tier=1,
            quality_tier=1,
            tags=[],
            input_modalities=["text"],
            output_modalities=["text"],
        )
        
        assert model.canonical_id == "test:test-model"
        assert model.provider == "test"
        assert model.model_id == "test-model"
        assert model.cost_tier == 1
        assert model.quality_tier == 1
    
    def test_canonical_model_with_pricing(self):
        """Test CanonicalModel with pricing information."""
        model = CanonicalModel(
            canonical_id="test:test-model",
            provider="test",
            model_id="test-model",
            cost_tier=1,
            quality_tier=1,
            tags=[],
            input_modalities=["text"],
            output_modalities=["text"],
            price_input_per_million=0.50,
            price_output_per_million=1.50,
        )
        
        assert model.price_input_per_million == 0.50
        assert model.price_output_per_million == 1.50
    
    def test_canonical_model_with_optional_fields(self):
        """Test CanonicalModel with optional fields."""
        model = CanonicalModel(
            canonical_id="test:test-model",
            provider="test",
            model_id="test-model",
            cost_tier=1,
            quality_tier=1,
            tags=["chat"],
            input_modalities=["text"],
            output_modalities=["text"],
            reasoning_tier=2,
            arena_score=1200.0,
        )
        
        assert model.reasoning_tier == 2
        assert model.arena_score == 1200.0


class TestCatalogAPIDocumentation:
    """Tests for API documentation completeness."""
    
    def test_build_catalog_has_docstring(self):
        """Test that build_catalog has docstring."""
        assert build_catalog.__doc__ is not None
        assert len(build_catalog.__doc__) > 0
    
    def test_get_catalog_has_docstring(self):
        """Test that get_catalog has docstring."""
        assert get_catalog.__doc__ is not None
        assert len(get_catalog.__doc__) > 0
