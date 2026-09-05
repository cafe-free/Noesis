import pytest
from apps.api.services.generation import GenerationService
from uuid import uuid4

@pytest.mark.asyncio
async def test_generation_service(mock_db, mock_provider):
    mock_supabase, _ = mock_db
    
    # Needs to mock table update and select
    def mock_table_actions(table_name):
        class MockTable:
            def select(self, *args, **kwargs):
                class MockEq:
                    def eq(self, *eargs, **ekwargs):
                        class MockExecute:
                            def execute(self):
                                return type('obj', (object,), {
                                    'data': [{
                                        'id': str(uuid4()),
                                        'language': 'Spanish',
                                        'level': 'A1',
                                        'topic': 'Food',
                                        'count': 1
                                    }]
                                })()
                        return MockExecute()
                return MockEq()
                
            def insert(self, data, **kwargs):
                class MockExecute:
                    def execute(self):
                        return type('obj', (object,), {'data': [{'id': str(uuid4())}]})()
                return MockExecute()
                
            def update(self, data, **kwargs):
                class MockEq:
                    def eq(self, *eargs, **ekwargs):
                        class MockExecute:
                            def execute(self):
                                return type('obj', (object,), {'data': []})()
                        return MockExecute()
                return MockEq()
                
        return MockTable()
        
    mock_supabase.table = mock_table_actions
    
    service = GenerationService(provider=mock_provider)
    # The generation service calls curriculum agent -> exercise agent -> distractor agent -> qa agent
    await service.run_generation_job(str(uuid4()))
    
    # Basically if it doesn't throw, our mock provider and agents are working sequentially
