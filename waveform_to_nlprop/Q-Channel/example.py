import base64
from openai import OpenAI
client = OpenAI()

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

with open('system_message.txt', 'r') as fr:
    lines = fr.readlines()

system_message = ''.join(lines)

response = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {"role": "system", "content": system_message},
    {
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{encode_image('Figure2-2.png')}"
          },
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{encode_image('Figure2-3.png')}"
          },
        },
      ],
    }
  ],
  seed=12345,
  temperature=0.0,
  top_p=0.0,
)

#print(response.choices[0])

### Write the assistant message to the output file ###
with open('results.txt', 'a') as fw:
    fw.write('(1)\n')
    fw.write(response.choices[0].message.content + '\n\n')
