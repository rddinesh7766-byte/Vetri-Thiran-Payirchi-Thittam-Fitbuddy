def _generate_structured(prompt: str, model_name: str) -> WorkoutPlan:
    client = get_client()

    if client is None:
        raise RuntimeError("Gemini API key is not configured.")

    import time

    for attempt in range(3):
        try:
            
            print("=" * 50)
            print("MODEL =", model_name)
            print("=" * 50)

            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.6,
                    response_mime_type="application/json",
                    response_schema=WorkoutPlan,
                ),
            )
            break

        except Exception as e:
                    print("=" * 80)
                    print("FULL ERROR:", repr(e))
                    print("=" * 80)

                      if attempt < 2:
                              time.sleep(15)
                       else:
                              raise e

    if getattr(response, "parsed", None) is not None:
        return WorkoutPlan.model_validate(response.parsed)

    if response.text:
        return WorkoutPlan.model_validate_json(response.text)

    raise RuntimeError("Gemini returned an empty response.")