# Retrival Augmented Generation
In this notebook we will build a RAG from scratch


```python
corpus_of_documents = [
    "Take a leisurely walk in the park and enjoy the fresh air.",
    "Visit a local museum and discover something new.",
    "Attend a live music concert and feel the rhythm.",
    "Go for a hike and admire the natural scenery.",
    "Have a picnic with friends and share some laughs.",
    "Explore a new cuisine by dining at an ethnic restaurant.",
    "Take a yoga class and stretch your body and mind.",
    "Join a local sports league and enjoy some friendly competition.",
    "Attend a workshop or lecture on a topic you're interested in.",
    "Visit an amusement park and ride the roller coasters."
]
```

We will use Jaccard similarity here. 

**Jaccard Similarty**: It is the intersection divided by the union of "sets" of words (that is, the no of sets of unions).

Preprocessing : We will need to convert the string to a set 


```python
def jaccard_similarity(query, document):
    query = query.lower().split(" ")
    document = document.lower().split(" ")
    intersection = set(query).intersection(set(document))
    union = set(query).union(set(document))
    return len(intersection)/len(union)
```

Now we define a function that will take in the query and corpus and select the best document to return to the user


```python
def return_response(query, corpus):
    similarities = []
    for doc in corpus:
        similarity = jaccard_similarity(user_input, doc)
        similarities.append(similarity)
    return corpus_of_documents[similarities.index(max(similarities))]
```


```python
user_prompt = "What is a leisure activity that you like?"
```


```python
user_input = "i like hiking"
return_response(user_input, corpus_of_documents)
```




    'Take a leisurely walk in the park and enjoy the fresh air.'



We have now successfully completed the **R** from the **RAG**

This retrival has no knowledge of semantics. To solve this, we will bring in an LLM.

Now we move to the Augmentation part.

### Adding LLM


```python
import requests
import json
```

First we define the inputs. To works with this model, we're going to take 

1. User input.
2. Fetch the most similar document.
3. Pass that into a prompt to the language model.
4. Return the result to the user.

Prompt: It is an instruction that you provide to the LLM.

When you run the code you will see the streaming result. Streaming the result is important for user experience.


```python
user_input = "I like to hike"
relevant_document = return_response(user_input, corpus_of_documents)
full_response = []

prompt = """
You are a bot that makes recommendations for activies. You answer in very short sentences and do not include extra information.

This is the recommended activity: {relevant_document}

The user input is: {user_input}

Compile a recommendation to the user based on the recommended activity and the user input.
"""
```

We will try two different models

1. **Llama 3**
2. **Deepseek-R1**

both models have 7B parameters

### Llama 3


```python
url = 'http://localhost:11434/api/generate'

data = {
        "model": "llama3:latest",
        "prompt": prompt.format(user_input=user_input, relevant_document=relevant_document)
}

headers = {'Content-Type': 'application/json'}

response = requests.post(url, data=json.dumps(data), headers=headers, stream=True)

try:
    count = 0
    for line in response.iter_lines():
        if line:
            decoded_line = json.loads(line.decode('utf-8'))
            
            full_response.append(decoded_line['response'])

finally:
    response.close()
print(''.join(full_response))
```

    You'll love this!<think>
    Okay, so I need to come up with a recommendation based on the activities and the user's input. The recommended activity is going for a hike and admiring natural scenery. The user said they "like to hike." 
    
    Hmm, how can I make this more engaging? Maybe emphasize that hiking isn't just about getting tired but also enjoying nature. Adding something about the views could make it more appealing. So putting it all together: "Go for a hike and enjoy the stunning views of nature!" That should be concise and highlight both the activity and the positive experience.
    </think>
    
    Go for a hike and enjoy the stunning views of nature!Try a new trail!You'll love this!Try a new trail!Try a challenging trail!Go for a longer, more challenging hike!You'll love this one!You'll love this!You'll love this!
    

### Deepseek-r1


```python
url = 'http://localhost:11434/api/generate'

data = {
        "model": "deepseek-r1:7b",
        "prompt": prompt.format(user_input=user_input, relevant_document=relevant_document)
}

headers = {'Content-Type': 'application/json'}

response = requests.post(url, data=json.dumps(data), headers=headers, stream=True)

try:
    count = 0
    for line in response.iter_lines():
        if line:
            decoded_line = json.loads(line.decode('utf-8'))
            
            full_response.append(decoded_line['response'])

finally:
    response.close()
print(''.join(full_response))
```

    You'll love this!<think>
    Okay, so I need to come up with a recommendation based on the activities and the user's input. The recommended activity is going for a hike and admiring natural scenery. The user said they "like to hike." 
    
    Hmm, how can I make this more engaging? Maybe emphasize that hiking isn't just about getting tired but also enjoying nature. Adding something about the views could make it more appealing. So putting it all together: "Go for a hike and enjoy the stunning views of nature!" That should be concise and highlight both the activity and the positive experience.
    </think>
    
    Go for a hike and enjoy the stunning views of nature!Try a new trail!You'll love this!Try a new trail!Try a challenging trail!Go for a longer, more challenging hike!You'll love this one!You'll love this!You'll love this!<think>
    Okay, so the user just told me they "like to hike." Hmm, they probably enjoy being outdoors and exploring nature. The initial recommended activity was about going for a hike and appreciating the scenery. I should make sure my response aligns with that.
    
    I need to keep it short since the bot's style is concise. Maybe something like suggesting they go hiking or suggest another outdoor activity if they want more variety. That way, I'm offering options based on their interest in hiking.
    </think>
    
    Try hiking again or explore other outdoor activities you enjoy!
    

---

Lets see what happens when you give the wrong input that isnt in the corpus


```python
user_input = "I don't like to hike"
relevant_document = return_response(user_input, corpus_of_documents)
# https://github.com/jmorganca/ollama/blob/main/docs/api.md
full_response = []
prompt = """
You are a bot that makes recommendations for activities. You answer in very short sentences and do not include extra information.
This is the recommended activity: {relevant_document}
The user input is: {user_input}
Compile a recommendation to the user based on the recommended activity and the user input.
"""
url = 'http://localhost:11434/api/generate'
data = {
    "model": "deepseek-r1:7b",
    "prompt": prompt.format(user_input=user_input, relevant_document=relevant_document)
}
headers = {'Content-Type': 'application/json'}
response = requests.post(url, data=json.dumps(data), headers=headers, stream=True)
try:
    for line in response.iter_lines():
        # filter out keep-alive new lines
        if line:
            decoded_line = json.loads(line.decode('utf-8'))
            # print(decoded_line['response'])  # uncomment to results, token by token
            full_response.append(decoded_line['response'])
finally:
    response.close()
print(''.join(full_response))
```

    <think>
    Okay, so the user wants me to act as a bot that recommends activities. The main activity suggested is going for a hike and admiring nature. But the user's input says they don't like hiking at all. I need to come up with a recommendation based on both.
    
    Hmm, first, understand what the user doesn't want. They hate hiking, so any suggestion around it should be avoided. The original activity was about hiking, which isn't an option anymore.
    
    I should think of alternatives that are still nature-related but don't involve hiking. Maybe something like visiting a botanical garden? That way, they can enjoy nature without the physical activity of hiking.
    
    Alternatively, perhaps going to a museum with a natural history exhibit could work. Or maybe a picnic in a park—just sitting and enjoying the surroundings relaxingly.
    
    Also, maybe reading a book about nature or watching a documentary on environmental topics might be good alternatives. These activities don't require exercise but still connect them with nature.
    
    I need to pick one that's concise and fits their preferences best. Visiting a botanical garden seems like a solid choice because it allows them to enjoy plants and the environment without any hiking involved.
    </think>
    
    Recommendation: Visit a local botanical garden.
    

### References
1. [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)
2. [learnbybuilding](https://learnbybuilding.ai/)
