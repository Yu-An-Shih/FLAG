from openai import OpenAI
client = OpenAI()

with open('system_message_nl.txt', 'r') as fr:
    lines = fr.readlines()
system_message = ''.join(lines)

with open('../Q-Channel/reset_nl.txt', 'r') as fr:
    lines = fr.readlines()
info = ''.join(lines)

with open('../Q-Channel/reset_template.txt', 'r') as fr:
    lines = fr.readlines()
templates = ''.join(lines)

info = 'Waveform information:\n' + info
templates = 'Templates:\n' + templates
user_message = info + '\n\n' + templates

response = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {"role": "system", "content": system_message},
    {"role": "user", "content": user_message}
  ],
  seed=12345,
  temperature=0.0,
  top_p=0.0,
)

#print(response.choices[0])

### Write the assistant message to the output file ###
with open('results_nl.txt', 'a') as fw:
    fw.write('(1)\n')
    fw.write(response.choices[0].message.content + '\n\n')
