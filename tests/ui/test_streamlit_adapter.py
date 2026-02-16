def test_render_ui_imports():
    from rag_interviewer.ui.streamlit_adapter import render_ui
    assert callable(render_ui)
