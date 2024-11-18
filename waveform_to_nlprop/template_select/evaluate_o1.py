from openai import OpenAI
client = OpenAI()

with open('system_message_nl.txt', 'r') as fr:
    lines = fr.readlines()
system_message = ''.join(lines)

with open('../Q-Channel/reset_nl.txt', 'r') as fr:
    lines = fr.readlines()
info = ''.join(lines)

info = 'Waveform information:\n' + info
user_message = system_message + '\n\n' + info

response = client.chat.completions.create(
  model="o1-preview",
  messages=[
    {"role": "user", "content": user_message}
  ],
  seed=12345,
)

#print(response.choices[0])

### Write the assistant message to the output file ###
with open('results_o1_nl.txt', 'a') as fw:
    fw.write('(1)\n')
    fw.write(response.choices[0].message.content + '\n\n')