from app.categorise.llm_client import LLMClient


def test_default_llm_is_local_and_cached():
    client = LLMClient(provider="none")
    first = client.categorise("UNKNOWN MERCHANT")
    second = client.categorise("UNKNOWN MERCHANT")
    assert first.category == "Uncategorised"
    assert second == first
    assert client.calls == 1


def test_llm_rejects_amounts_ids_and_personal_data():
    client = LLMClient(provider="none")
    email = "PERSON" + chr(64) + "example.com"
    phone = "RAHUL +" + "91" + "9876543210"
    for value in ("SHOP 12345", email, phone):
        try:
            client.categorise(value)
        except ValueError:
            pass
        else:
            raise AssertionError("unsafe text reached the LLM boundary")
