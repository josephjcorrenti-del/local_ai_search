from local_ai.config import CONFIG


def test_local_ai_config_reads_monorepo_config():
    assert CONFIG.app_name == "local_ai"
    assert CONFIG.ollama_base_url == "http://127.0.0.1:11434"
    assert CONFIG.request_timeout_s == 120

    assert CONFIG.small_model_name == "phi3:mini"
    assert CONFIG.lightweight_model_name == "phi3:mini"
    assert CONFIG.large_model_name == "qwen2.5-coder:3b"

    assert CONFIG.chat_model_name == "qwen2.5-coder:3b"
    assert CONFIG.summary_model_name == "phi3:mini"

    assert CONFIG.default_session_name == "default"
    assert CONFIG.memory_turn_limit == 8

    assert CONFIG.summary_keep_recent_messages == 8
    assert CONFIG.summary_max_input_messages == 12
    assert CONFIG.summary_inactive_minutes == 30
    assert CONFIG.summary_max_input_chars == 600

    assert CONFIG.web_chat_max_source_chars == 6000
