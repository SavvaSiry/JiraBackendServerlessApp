import os
import openai

if __name__ == '__main__':
    openai.api_key = "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"

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "How much is 2 + 2"}
        ]
    )

    print(completion.choices[0].message)









    # encoded_jwt = jwt.encode({'alg': 'RS256', 'typ': 'JWT', 'kid': 'key-id-12345...'}, "secret", algorithm="HS256")
    # code = str(encoded_jwt) + '1'
    # print(str(encoded_jwt) + '1')
    #
    # try:
    #     payload = jwt.decode(code, "secret", algorithms=["HS256"])
    # except jwt.DecodeError:
    #     print('Error')
    #     pass
