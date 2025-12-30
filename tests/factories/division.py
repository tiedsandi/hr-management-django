"""
Factory untuk Division model.
"""
import factory
from factory.django import DjangoModelFactory

from apps.accounts.models import Division


class DivisionFactory(DjangoModelFactory):
    """Factory untuk membuat Division test data"""
    
    class Meta:
        model = Division
        django_get_or_create = ('code',)  # Avoid duplicate codes
    
    name = factory.Sequence(lambda n: f'Division {n}')
    code = factory.Sequence(lambda n: f'DIV{n:03d}')
    description = factory.Faker('paragraph', nb_sentences=2)
    parent = None  # Default no parent (top level)
    level = 0  # Will be auto-calculated by model
    
    @factory.post_generation
    def set_level(obj, create, extracted, **kwargs):
        """Auto-calculate level based on parent"""
        if create and obj.parent:
            obj.level = obj.parent.level + 1
            obj.save()


class SubDivisionFactory(DivisionFactory):
    """Factory untuk sub-division (dengan parent)"""
    
    parent = factory.SubFactory(DivisionFactory)
    name = factory.Sequence(lambda n: f'Sub Division {n}')
    code = factory.Sequence(lambda n: f'SUB{n:03d}')
