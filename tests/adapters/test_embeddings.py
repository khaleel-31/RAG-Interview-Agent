def test_get_embeddings_monkeypatched(monkeypatch):
    import rag_interviewer.adapters.embeddings as eng
    class Dummy:
        pass
    monkeypatch.setattr(eng, "get_embeddings", lambda: Dummy(), raising=True)
    obj = eng.get_embeddings()
    assert obj is not None
