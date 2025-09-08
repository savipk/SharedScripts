

# Additional edge case tests for themes mapping
class TestMapControlToThemesEdgeCases:
    """Test edge cases and error handling for themes mapping."""
    
    def test_empty_control_description_raises_validation_error(self):
        with pytest.raises(ValidationError, match="controlDescription must not be empty"):
            map_control_to_themes(
                record_id='r1', 
                control_description='', 
                repo=FakeRepo(), 
                llm=FakeLLM(), 
                deployment='d'
            )
    
    def test_whitespace_only_control_description_raises_validation_error(self):
        with pytest.raises(ValidationError, match="controlDescription must not be empty"):
            map_control_to_themes(
                record_id='r1', 
                control_description='   \t\n  ', 
                repo=FakeRepo(), 
                llm=FakeLLM(), 
                deployment='d'
            )
    
    def test_empty_theme_rows_raises_definitions_not_loaded(self):
        class EmptyRepo(DefinitionsRepository):
            def get_theme_rows(self):
                return []
            def get_fivews_rows(self):
                return []
        
        with pytest.raises(DefinitionsNotLoadedError, match="taxonomy definitions not loaded"):
            map_control_to_themes(
                record_id='r1',
                control_description='valid text',
                repo=EmptyRepo(),
                llm=FakeLLM(),
                deployment='d'
            )
    
    def test_llm_invalid_json_raises_validation_error(self):
        class BadLLM:
            def json_schema_chat(self, **kwargs):
                return "invalid json"
        
        with pytest.raises(ValidationError, match="LLM output validation failed"):
            map_control_to_themes(
                record_id='r1',
                control_description='valid text',
                repo=FakeRepo(),
                llm=BadLLM(),
                deployment='d'
            )
    
    def test_long_control_description_handled(self):
        long_text = "A" * 5000  # Very long control description
        result = map_control_to_themes(
            record_id='r1',
            control_description=long_text,
            repo=FakeRepo(),
            llm=FakeLLM(),
            deployment='d'
        )
        assert isinstance(result, list)
        assert len(result) == 3  # Should still limit to top 3


# Additional edge case tests for 5Ws mapping
class TestMapControlToFiveWsEdgeCases:
    """Test edge cases and error handling for 5Ws mapping."""
    
    def test_empty_control_description_raises_validation_error(self):
        with pytest.raises(ValidationError, match="controlDescription must not be empty"):
            map_control_to_5ws(
                record_id='r1', 
                control_description='', 
                repo=FakeRepo(), 
                llm=FakeLLM(), 
                deployment='d'
            )
    
    def test_whitespace_only_control_description_raises_validation_error(self):
        with pytest.raises(ValidationError, match="controlDescription must not be empty"):
            map_control_to_5ws(
                record_id='r1', 
                control_description='   \t\n  ', 
                repo=FakeRepo(), 
                llm=FakeLLM(), 
                deployment='d'
            )
    
    def test_empty_fivews_definitions_raises_error(self):
        class EmptyRepo(DefinitionsRepository):
            def get_theme_rows(self):
                return []
            def get_fivews_rows(self):
                return []
        
        with pytest.raises(DefinitionsNotLoadedError, match="5Ws definitions not loaded"):
            map_control_to_5ws(
                record_id='r1',
                control_description='valid text',
                repo=EmptyRepo(),
                llm=FakeLLM(),
                deployment='d'
            )
    
    def test_llm_invalid_json_raises_validation_error(self):
        class BadLLM:
            def json_schema_chat(self, **kwargs):
                return "invalid json"
        
        with pytest.raises(ValidationError, match="LLM output validation failed"):
            map_control_to_5ws(
                record_id='r1',
                control_description='valid text',
                repo=FakeRepo(),
                llm=BadLLM(),
                deployment='d'
            )
    
    def test_llm_missing_fivews_field_raises_validation_error(self):
        class BadLLM:
            def json_schema_chat(self, **kwargs):
                return json.dumps({"wrong_field": []})
        
        with pytest.raises(ValidationError, match="LLM output validation failed"):
            map_control_to_5ws(
                record_id='r1',
                control_description='valid text',
                repo=FakeRepo(),
                llm=BadLLM(),
                deployment='d'
            )
    
    def test_ordering_maintained_despite_llm_disorder(self):
        class DisorderedLLM:
            def json_schema_chat(self, **kwargs):
                # Return 5Ws in wrong order
                return json.dumps({
                    'fivews': [
                        {'name': 'why', 'status': 'present', 'reasoning': 'r'},
                        {'name': 'where', 'status': 'present', 'reasoning': 'r'},
                        {'name': 'who', 'status': 'present', 'reasoning': 'r'},
                        {'name': 'when', 'status': 'missing', 'reasoning': 'r'},
                        {'name': 'what', 'status': 'present', 'reasoning': 'r'},
                    ]
                })
        
        result = map_control_to_5ws(
            record_id='r1',
            control_description='valid text',
            repo=FakeRepo(),
            llm=DisorderedLLM(),
            deployment='d'
        )
        
        # Should be reordered correctly
        names = [item['name'] for item in result]
        assert names == ['who', 'what', 'when', 'where', 'why']
    
    def test_context_trace_id_passed_to_llm(self):
        class TraceLLM:
            def __init__(self):
                self.last_context = None
            
            def json_schema_chat(self, **kwargs):
                self.last_context = kwargs.get('context')
                return json.dumps({
                    'fivews': [
                        {'name': 'who', 'status': 'present', 'reasoning': 'r'},
                        {'name': 'what', 'status': 'present', 'reasoning': 'r'},
                        {'name': 'when', 'status': 'missing', 'reasoning': 'r'},
                        {'name': 'where', 'status': 'present', 'reasoning': 'r'},
                        {'name': 'why', 'status': 'present', 'reasoning': 'r'},
                    ]
                })
        
        trace_llm = TraceLLM()
        map_control_to_5ws(
            record_id='test-trace-123',
            control_description='valid text',
            repo=FakeRepo(),
            llm=trace_llm,
            deployment='d'
        )
        
        assert trace_llm.last_context == {"trace_id": "test-trace-123"}


# Tests for the use case classes directly
class TestClassifyControlToThemesClass:
    """Test ClassifyControlToThemes class directly."""
    
    def test_from_defs_creates_instance(self):
        use_case = ClassifyControlToThemes.from_defs(FakeRepo(), FakeLLM())
        assert isinstance(use_case, ClassifyControlToThemes)
        assert use_case.repo is not None
        assert use_case.llm is not None
    
    def test_from_defs_with_empty_repo_raises_error(self):
        class EmptyRepo(DefinitionsRepository):
            def get_theme_rows(self):
                return []
            def get_fivews_rows(self):
                return []
        
        with pytest.raises(DefinitionsNotLoadedError):
            ClassifyControlToThemes.from_defs(EmptyRepo(), FakeLLM())


class TestClassifyControlToFiveWsClass:
    """Test ClassifyControlToFiveWs class directly."""
    
    def test_run_method_direct_call(self):
        use_case = ClassifyControlToFiveWs(repo=FakeRepo(), llm=FakeLLM())
        result = use_case.run(
            record_id='direct-test',
            control_description='test control',
            deployment='test-deployment'
        )
        assert isinstance(result, list)
        assert len(result) == 5
        assert [item['name'] for item in result] == ['who', 'what', 'when', 'where', 'why']
