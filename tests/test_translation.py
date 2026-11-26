
import json

from ai_engine.translator import TranslationEngine


def main():

    engine = TranslationEngine()

    test_sentences = [

        "Hello, how are you today?",

        "Artificial intelligence is transforming the world.",

        "Machine translation helps people communicate across languages.",

        "The development of science and technology brings many benefits to society.",

        "Never give up on your dreams."
    ]

    for index, sentence in enumerate(test_sentences, 1):

        print("\n" + "=" * 60)
        print(f"TEST CASE {index}")
        print("=" * 60)

        result = engine.translate(
            text=sentence,
            beam_size=4,
            max_new_tokens=128
        )

        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=4
            )
        )


if __name__ == "__main__":
    main()
