"""
Custom Schema Views for API versioning
"""
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.settings import spectacular_settings
from drf_spectacular.views import SpectacularAPIView
from rest_framework.settings import api_settings


class SpectacularAPIViewV1(SpectacularAPIView):
    """Schema view for API V1 only - with custom filtering"""
    urlconf = 'api.v1.urls'

    def get(self, request, *args, **kwargs):
        from django.urls import get_resolver
        from drf_spectacular.generators import SchemaGenerator

        # Get schema with custom urlconf
        generator = SchemaGenerator(
            urlconf='api.v1.urls',
            patterns=get_resolver('api.v1.urls').url_patterns
        )

        schema = generator.get_schema(request=request, public=True)

        # Filter schema to remove V2 tags/paths
        if 'paths' in schema:
            filtered_paths = {}
            for path, methods in schema['paths'].items():
                # Exclude V2-only endpoints
                if not (
                    '/users/statistics' in path or
                    '/users/{id}/activity' in path or
                    '[V2]' in str(methods)
                ):
                    filtered_paths[path] = methods
            schema['paths'] = filtered_paths

        # Filter tags
        if 'tags' in schema:
            schema['tags'] = [tag for tag in schema['tags'] if 'V2' not in tag.get('name', '')]

        return self.render(schema, request)

    def render(self, schema, request):
        from rest_framework.renderers import JSONRenderer
        from rest_framework.response import Response
        renderer = JSONRenderer()
        return Response(schema)


class SpectacularAPIViewV2(SpectacularAPIView):
    """Schema view for API V2 only - with custom filtering"""
    
    def get_spectacular_settings(self):
        """Override settings for V2"""
        settings = spectacular_settings.copy()
        # Override tags to only show V2 tags
        settings['TAGS'] = [
            {'name': 'Users V2', 'description': 'Enhanced user endpoints with metadata and statistics (V2)'},
        ]
        return settings
    
    def get(self, request, *args, **kwargs):
        # Force use only api.v2.urls
        from django.urls import get_resolver
        from drf_spectacular.generators import SchemaGenerator

        # Get schema with custom urlconf
        generator = SchemaGenerator(
            urlconf='api.v2.urls',
            patterns=get_resolver('api.v2.urls').url_patterns
        )
        
        schema = generator.get_schema(request=request, public=True)
        
        # Filter schema to remove non-V2 tags
        if 'paths' in schema:
            filtered_paths = {}
            for path, methods in schema['paths'].items():
                # Only include paths that start with /accounts/users/
                if '/accounts/users/' in path or path.endswith('/accounts/users'):
                    filtered_paths[path] = methods
            schema['paths'] = filtered_paths
        
        # Filter tags
        if 'tags' in schema:
            schema['tags'] = [tag for tag in schema['tags'] if 'V2' in tag.get('name', '')]
        
        return self.render(schema, request)
    
    def render(self, schema, request):
        from rest_framework.renderers import JSONRenderer
        from rest_framework.response import Response
        renderer = JSONRenderer()
        return Response(schema)


